import json
import os
from typing import List, Dict, Any, Union, Optional
from .base import FileRepository
from ..logger import logger

class JsonRepository(FileRepository):
    """
    Repository for JSON files supporting both record collections (lists) 
    and single objects (dicts).
    """

    def read(self, default: Any = None) -> Any:
        """
        Read the entire JSON content from the file.
        
        Args:
            default: Value to return if file doesn't exist or is invalid. 
                    Defaults to an empty dict.
        
        Returns:
            The parsed JSON data (list, dict, etc.)
        """
        try:
            self.ensure_exists()
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default if default is not None else {}

    def save(self, data: Any) -> None:
        """
        Save any JSON-serializable data to the file.
        
        Args:
            data: The data to save.
        """
        self._save(data)

    def read_all(self) -> Any:
        """
        Read all data from the file. Supports both collections (lists) 
        and single objects (dicts).
        """
        return self.read(default=[])

    def save_all(self, data: List[Dict[str, Any]]) -> None:
        """
        Save all records to the JSON file.
        """
        try:
            self.save(data)
            logger.info(f"JSON content saved successfully to: {self.file_path}")
        except Exception as e:
            logger.exception(f"Error while saving JSON '{self.file_path}': {e}")
            raise

    def _save(self, data: Any):
        """Internal save method used by CRUD operations."""
        self.ensure_directory_exists()
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def update_dict(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper for object-style files. Reads the dict, updates it, and saves.
        
        Args:
            updates: Dictionary of keys/values to update.
            
        Returns:
            The updated dictionary.
        """
        data = self.read(default={})
        if not isinstance(data, dict):
            data = {}
        data.update(updates)
        self.save(data)
        return data

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a record by its 'id' field in a collection.
        
        Args:
            record_id: The ID to search for.
            
        Returns:
            The record dictionary if found, else None.
        """
        data = self.read_all()
        if not isinstance(data, list):
            return None
            
        for record in data:
            if isinstance(record, dict) and str(record.get('id')) == str(record_id):
                return record
        return None

    def add(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        current_data = self.read_all()
        
        if not isinstance(current_data, list):
            if not current_data:
                current_data = []
            else:
                from ..logger import logger
                logger.error(f"Cannot 'add' to a non-list JSON repository: {self.file_path}")
                raise ValueError(f"Repository at {self.file_path} is a dictionary, not a list. Use update_dict instead.")

        if isinstance(data, list):
            current_data.extend(data)
        else:
            current_data.append(data)
        self._save(current_data)

    def update(self, record_id: str, updates: Dict[str, Any]) -> bool:
        data = self.read_all()
        if not isinstance(data, list):
            return False

        updated = False
        for i, record in enumerate(data):
            if isinstance(record, dict) and str(record.get('id')) == str(record_id):
                data[i].update(updates)
                updated = True
                break
        
        if updated:
            self._save(data)
        return updated

    def delete(self, record_id: str) -> bool:
        data = self.read_all()
        if not isinstance(data, list):
            return False

        initial_len = len(data)
        data = [r for r in data if not isinstance(r, dict) or str(r.get('id')) != str(record_id)]
        
        if len(data) < initial_len:
            self._save(data)
            return True
        return False

    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information including nested structures."""
        data = self.read_all()
        
        all_fields = {}
        sample = None
        best_sample = None
        max_populated = 0

        if isinstance(data, list):
            for record in data:
                if isinstance(record, dict):
                    self._analyze_fields(record, all_fields)
                    
                    # Count populated fields (non-empty arrays/objects)
                    populated = self._count_populated_fields(record)
                    
                    if sample is None:
                        sample = record
                    
                    # Keep track of the record with most populated data
                    if populated > max_populated:
                        max_populated = populated
                        best_sample = record
                        
        elif isinstance(data, dict):
            self._analyze_fields(data, all_fields)
            sample = data
            best_sample = data

        return {
            "fields": sorted(all_fields.keys()),
            "schema": all_fields,
            "sample": best_sample if best_sample else sample
        }
    
    def _count_populated_fields(self, obj: Dict[str, Any]) -> int:
        """Count how many fields have meaningful data (non-empty)."""
        count = 0
        for value in obj.values():
            if isinstance(value, (list, dict)):
                if value:  # Non-empty list or dict
                    count += 1
            elif value is not None:
                count += 1
        return count

    def _analyze_fields(self, obj: Dict[str, Any], fields: Dict[str, Any]) -> None:
        """Recursively analyze fields and capture nested schemas."""
        for key, value in obj.items():
            field_info = self._get_type_info(value)
            
            # Merge with existing field info if present
            if key in fields:
                existing = fields[key]
                # If both are arrays with nested schemas, merge them
                if (field_info.get("type") == "array" and existing.get("type") == "array" and
                    "nested" in field_info and "nested" in existing):
                    self._merge_fields(existing["nested"], field_info["nested"])
                # If we found a non-empty array after an empty one, update it
                elif (field_info.get("type") == "array" and "nested" in field_info and 
                      existing.get("type") == "array" and "nested" not in existing):
                    fields[key] = field_info
            else:
                fields[key] = field_info

    def _get_type_info(self, value: Any) -> Dict[str, Any]:
        """Get type information for a value."""
        if isinstance(value, dict):
            nested = {}
            self._analyze_fields(value, nested)
            return {"type": "object", "nested": nested}
            
        elif isinstance(value, list):
            if not value:  # Empty array
                return {"type": "array", "items": "unknown"}
            
            first = value[0]
            if isinstance(first, dict):
                # Analyze all dict items in the array
                nested = {}
                for item in value:
                    if isinstance(item, dict):
                        self._analyze_fields(item, nested)
                return {"type": "array", "items": "object", "nested": nested}
            else:
                return {"type": "array", "items": type(first).__name__}
                
        elif isinstance(value, bool):
            return {"type": "bool"}
        elif isinstance(value, int):
            return {"type": "int"}
        elif isinstance(value, float):
            return {"type": "float"}
        elif isinstance(value, str):
            return {"type": "str"}
        elif value is None:
            return {"type": "null"}
        else:
            return {"type": "unknown"}

    def _merge_fields(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Merge source fields into target."""
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif "nested" in value and "nested" in target[key]:
                self._merge_fields(target[key]["nested"], value["nested"])