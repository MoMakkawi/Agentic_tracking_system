import os
from .base import FileRepository
from .json_repo import JsonRepository
from .jsonl_repo import JsonlRepository
from .csv_repo import CsvRepository
from .ics_repo import IcsRepository

class RepositoryFactory:
    @staticmethod
    def get_repository(file_path: str) -> FileRepository:
        """
        Returns the appropriate FileRepository based on the file extension.
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.json':
            return JsonRepository(file_path)
        elif ext == '.jsonl':
            return JsonlRepository(file_path)
        elif ext == '.csv':
            return CsvRepository(file_path)
        elif ext == '.ics':
            return IcsRepository(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
