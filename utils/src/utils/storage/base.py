from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import os

class FileRepository(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def ensure_exists(self) -> None:
        """
        Ensure the file exists. Raises FileNotFoundError if it does not.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

    @abstractmethod
    def read_all(self) -> List[Dict[str, Any]]:
        """Read all records from the file."""
        pass

    @abstractmethod
    def add(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """Add a new record or a list of records to the file."""
        pass

    @abstractmethod
    def update(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a record by ID. Returns True if found and updated.
        Assumes records have an 'id' field.
        """
        pass

    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """
        Delete a record by ID. Returns True if found and deleted.
        Assumes records have an 'id' field.
        """
        pass
