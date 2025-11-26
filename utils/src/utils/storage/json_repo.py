import json
import os
from typing import List, Dict, Any, Union
from .base import FileRepository

class JsonRepository(FileRepository):
    def read_all(self) -> List[Dict[str, Any]]:
        self.ensure_exists()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save(self, data: List[Dict[str, Any]]):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def save_all(self, data: List[Dict[str, Any]]) -> None:
        """
        Save all records to the JSON file.
        
        Args:
            data: List of dictionaries to save
        """
        try:
            dirname = os.path.dirname(self.file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            from utils import logger
            logger.info(f"JSON content saved successfully to: {self.file_path}")
        except Exception as e:
            from utils import logger
            logger.exception(f"Error while saving JSON '{self.file_path}': {e}")
            raise


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
