import csv
import os
from typing import List, Dict, Any, Union
from .base import FileRepository

class CsvRepository(FileRepository):
    def read_all(self) -> List[Dict[str, Any]]:
        self.ensure_exists()
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception:
            return []

    def _save(self, data: List[Dict[str, Any]]):
        if not data:
            # If empty, create an empty file
            self.ensure_directory_exists()
            open(self.file_path, 'w').close()
            return

        # Ensure directory exists
        self.ensure_directory_exists()
            
        fieldnames = data[0].keys()
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def add(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        current_data = self.read_all()
        if isinstance(data, list):
            current_data.extend(data)
        else:
            current_data.append(data)
        self._save(current_data)

    def update(self, record_id: str, updates: Dict[str, Any]) -> bool:
        data = self.read_all()
        updated = False
        for i, record in enumerate(data):
            if str(record.get('id')) == str(record_id):
                data[i].update(updates)
                updated = True
                break
        
        if updated:
            self._save(data)
        return updated

    def delete(self, record_id: str) -> bool:
        data = self.read_all()
        initial_len = len(data)
        data = [r for r in data if str(r.get('id')) != str(record_id)]
        
        if len(data) < initial_len:
            self._save(data)
            return True
        return False

    def save_all(self, data: List[Dict[str, Any]]) -> None:
        """
        Overwrite the file with the provided list of records.
        """
        self._save(data)

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information about the CSV file.
        Returns fieldnames as 'fields', type schema as 'schema', and a sample row.
        Types are inferred by analyzing all rows.
        """
        try:
            self.ensure_exists()
            data = self.read_all()
            
            if not data:
                return {"fields": [], "schema": {}, "sample": None}
            
            # Get field names from the first record
            fieldnames = list(data[0].keys()) if data else []
            
            # Analyze all records to determine types
            schema = {}
            for field in fieldnames:
                schema[field] = {"type": "unknown"}
            
            for record in data:
                for field, value in record.items():
                    if field in schema:
                        inferred_type = self._infer_type(value)
                        # Update type if we find a more specific type
                        if schema[field]["type"] == "unknown" or inferred_type != "str":
                            schema[field] = {"type": inferred_type}
            
            # Find the best sample (row with most non-empty values)
            best_sample = data[0]
            max_populated = 0
            
            for record in data:
                populated = sum(1 for v in record.values() if v and str(v).strip())
                if populated > max_populated:
                    max_populated = populated
                    best_sample = record
            
            return {
                "fields": fieldnames,
                "schema": schema,
                "sample": best_sample
            }
        except Exception:
            return {"fields": [], "schema": {}, "sample": None}

    def _infer_type(self, value: str) -> str:
        """
        Infer the type of a CSV value (all CSV values are strings).
        Returns: 'int', 'float', 'bool', 'null', or 'str'
        """
        if value is None or value == "":
            return "null"
        
        # Check for boolean
        if value.lower() in ("true", "false"):
            return "bool"
        
        # Check for integer
        try:
            int(value)
            return "int"
        except ValueError:
            pass
        
        # Check for float
        try:
            float(value)
            return "float"
        except ValueError:
            pass
        
        return "str"
