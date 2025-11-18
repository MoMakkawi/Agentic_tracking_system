import requests
from typing import Optional, Dict, Any

from utils import Secrets, logger, get_config
from utils.files_helper import FilesHelper


class DataFetcher:
    """
    Robust utility class for downloading logs (JSONL) and ICS calendar data.

    Responsibilities:
    - Fetch logs from a configured URL
    - Fetch ICS from a configured URL
    - Save both to disk
    """

    REQUEST_TIMEOUT = 60

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

        self.ics_url = ics_url or Secrets.ICS_URL
        self.ics_path = ics_path or config.PATHS.ICS

        self.data = None
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
        logger.info(f"Fetching {resource_name} from: {url}")

        try:
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            logger.info(f"{resource_name.capitalize()} fetched successfully")
            return response.content

        except requests.Timeout:
            logger.error(f"Timed out while fetching {resource_name} from {url}")
            raise

        except requests.RequestException as e:
            logger.error(f"Failed to fetch {resource_name} from {url}: {e}")
            raise

    def _save(self, data, path: str) -> str:
        """Saves data to disk with robust error handling."""
        logger.info(f"Saving file to: {path}")

        try:
            FilesHelper.save(data, path)
            logger.info(f"Saved successfully to: {path}")
            return path

        except OSError as e:
            logger.error(f"Failed to save file to {path}: {e}")
            raise

    # ----------------------------------------------------------------------
    # Public methods
    # ----------------------------------------------------------------------
    def run(self) -> Dict[str, bytes]:
        """
        Fetch logs and ICS data and store them internally.

        Returns:
            dict: {
                "logs": bytes,
                "ics": bytes
            }
        """
        self.data = self._fetch(self.logs_url, "logs")
        self.ics = self._fetch(self.ics_url, "ics")

        return {
            "logs": self.data,
            "ics": self.ics,
        }

    def save(self) -> Dict[str, str]:
        """
        Saves fetched data to disk.

        Returns:
            dict: {
                "logs": "<path>",
                "ics": "<path>"
            }
        """
        if self.data is None or self.ics is None:
            raise RuntimeError("No data fetched. Call run() before save().")

        logs_path = self._save(self.data, self.logs_path)
        ics_path = self._save(self.ics, self.ics_path)

        return {
            "logs": logs_path,
            "ics": ics_path,
        }
