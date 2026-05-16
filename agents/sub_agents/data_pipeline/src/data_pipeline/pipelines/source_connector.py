import os
import json
import requests
from typing import Optional, Dict
from utils import Secrets, logger, get_config
from utils import RepositoryFactory

class DataFetcher:
    """
    Robust utility class for downloading logs (JSONL) and ICS calendar data.

    Responsibilities:
    - Fetch logs from a configured URL
    - Fetch ICS from a configured URL
    - Save both to disk
    - Merge generated synthetic logs into the main log file
    """

    def __init__(
        self,
        logs_url: Optional[str] = None,
        logs_path: Optional[str] = None,
        ics_url: Optional[str] = None,
        ics_path: Optional[str] = None,
    ):
        config = get_config()

        self.logs_url = logs_url or config.SOURCE_URLS.LOGS
        self.logs_path = logs_path or config.PATHS.LOGS
        self.generated_logs_path = config.PATHS.GENERATED_LOGS

        self.ics_url = ics_url or Secrets.ICS_URL
        self.ics_path = ics_path or config.PATHS.ICS

        self.logs = None
        self.ics = None

        self._validate_config()

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------
    def _validate_config(self) -> None:
        """Ensures all required URLs and paths are provided."""
        required = {
            "logs_url": self.logs_url,
            "logs_path": self.logs_path,
            "ics_url": self.ics_url,
            "ics_path": self.ics_path,
        }

        missing = [key for key, val in required.items() if not val]
        if missing:
            raise ValueError(f"Missing required configuration values: {', '.join(missing)}")

    def _fetch(self, url: str, resource_name: str) -> bytes:
        """Generic fetch wrapper with logging and error handling."""
        try:
            response = requests.get(url, timeout= 60)
            response.raise_for_status()
            return response.content

        except requests.Timeout:
            logger.error(f"Timed out while fetching {resource_name}.")
            raise

        except requests.RequestException as e:
            logger.error(f"Failed to fetch {resource_name}: {e}.")
            raise

    def _save_data(self, data: bytes, path: str, resource_name: str) -> None:
        """
        Helper method to save data using RepositoryFactory.
        
        Args:
            data: The bytes data to save
            path: The file path where data should be saved
            resource_name: Name of the resource for logging purposes
        """
        try:
            repo = RepositoryFactory.get_repository(path)
            repo.save_from_bytes(data)
        except Exception as e:
            logger.error(f"Failed to save {resource_name} to {path}: {e}")
            raise

    def _merge_generated_logs(self) -> None:
        """
        Merge generated synthetic logs into the main logs file.
        
        Reads from the generated_logs.jsonl file (if it exists) and appends
        each record to the main logs_data.jsonl file using the repository's
        add() method.
        """
        if not self.generated_logs_path:
            return

        if not os.path.exists(self.generated_logs_path):
            logger.info("No generated logs file found, skipping merge.")
            return

        try:
            # Read generated log records
            generated_records = []
            with open(self.generated_logs_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        generated_records.append(json.loads(line))

            if not generated_records:
                logger.info("Generated logs file is empty, skipping merge.")
                return

            # Append to the main logs file
            logs_repo = RepositoryFactory.get_repository(self.logs_path)
            logs_repo.add(generated_records)
            logger.info(
                f"Merged {len(generated_records)} generated log entries "
                f"from '{self.generated_logs_path}' into '{self.logs_path}'."
            )

        except Exception as e:
            logger.error(f"Failed to merge generated logs: {e}")
            raise

    # ----------------------------------------------------------------------
    # Public methods
    # ----------------------------------------------------------------------
    def run(self) -> Dict[str, bytes]:
        """
        Fetch logs and ICS data.

        Returns:
            dict: {
                "logs": bytes,
                "ics": bytes
            }
        """
        self.ics = self._fetch(self.ics_url, "ics")
        self.logs = self._fetch(self.logs_url, "logs")

        return {
            "logs": self.logs,
            "ics": self.ics,
        }

    def save(self) -> Dict[str, str]:
        """
        Saves fetched data to disk, then merges any generated synthetic logs.

        Returns:
            dict: {
                "logs": "<path>",
                "ics": "<path>"
            }
        """
        if not self.logs or not self.ics:
            raise ValueError("Data must contain both 'logs' and 'ics' keys")

        # Save ICS in ics format using RepositoryFactory
        self._save_data(self.ics, self.ics_path, "ics")

        # Save logs in jsonl format using RepositoryFactory
        self._save_data(self.logs, self.logs_path, "logs")

        # Merge generated synthetic logs into the main log file
        self._merge_generated_logs()

        # Return the saved paths
        return {
            "logs": self.logs_path,
            "ics": self.ics_path,
        }
