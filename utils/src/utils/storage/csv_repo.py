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
            dir_path = os.path.dirname(self.file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            open(self.file_path, 'w').close()
            return

        # Ensure directory exists
        dir_path = os.path.dirname(self.file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
            
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
