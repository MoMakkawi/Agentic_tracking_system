import json
import os
from typing import List, Dict, Any, Union
from .base import FileRepository
from utils import logger

class JsonlRepository(FileRepository):
    def read_all(self) -> List[Dict[str, Any]]:
        data = []
        try:
            self.ensure_exists()
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, start=1):
                    try:
                        if line.strip():
                            data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON on line {i} in '{self.file_path}': {e}")
                        continue
            logger.info(f"JSONL loaded successfully: {self.file_path}")
            logger.debug(f"Total records loaded: {len(data)}")
            return data
        except FileNotFoundError:
            logger.error(f"JSONL file not found: {self.file_path}")
            raise
        except Exception as e:
            logger.exception(f"Error while loading JSONL '{self.file_path}': {e}")
            raise

    def add(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        try:
            self.ensure_directory_exists()
            with open(self.file_path, 'a', encoding='utf-8') as f:
                if isinstance(data, list):
                    for record in data:
                        f.write(json.dumps(record, ensure_ascii=False) + '\n')
                else:
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            logger.info(f"Added data to JSONL: {self.file_path}")
        except Exception as e:
            logger.exception(f"Error while adding to JSONL '{self.file_path}': {e}")
            raise

    def save_all(self, data: List[Dict[str, Any]]):
        try:
            self.ensure_directory_exists()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                for record in data:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            logger.info(f"JSONL content saved successfully to: {self.file_path}")
        except Exception as e:
            logger.exception(f"Error while saving JSONL '{self.file_path}': {e}")
            raise

    def update(self, record_id: str, updates: Dict[str, Any]) -> bool:
        try:
            data = self.read_all()
            updated = False
            for i, record in enumerate(data):
                if str(record.get('id')) == str(record_id):
                    data[i].update(updates)
                    updated = True
                    break
            
            if updated:
                self.save_all(data)
                logger.info(f"Updated record {record_id} in {self.file_path}")
            return updated
        except Exception as e:
            logger.exception(f"Error while updating JSONL '{self.file_path}': {e}")
            raise

    def delete(self, record_id: str) -> bool:
        try:
            data = self.read_all()
            initial_len = len(data)
            data = [r for r in data if str(r.get('id')) != str(record_id)]
            
            if len(data) < initial_len:
                self.save_all(data)
                logger.info(f"Deleted record {record_id} from {self.file_path}")
                return True
            return False
        except Exception as e:
            logger.exception(f"Error while deleting from JSONL '{self.file_path}': {e}")
            raise

    def save_from_bytes(self, content: bytes) -> None:
        """
        Parse raw bytes content into JSON objects and save them.
        """
        self.ensure_directory_exists()
        try:
            logs_str = content.decode('utf-8')
            data = []
            for line in logs_str.splitlines():
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            self.save_all(data)
            logger.info(f"Saved {len(data)} records from bytes to {self.file_path}")
        except Exception as e:
            logger.exception(f"Error while saving from bytes to '{self.file_path}': {e}")
            raise
