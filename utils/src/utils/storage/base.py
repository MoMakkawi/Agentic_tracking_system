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

    def ensure_directory_exists(self) -> None:
        """
        Create parent directories for the file path if they don't exist.
        This method extracts the directory path from self.file_path and creates
        all necessary parent directories.
        """
        dir_path = os.path.dirname(self.file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

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

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information about the file.
        Returns a dictionary containing schema details, typically 'fields' and 'sample'.
        """
        pass
