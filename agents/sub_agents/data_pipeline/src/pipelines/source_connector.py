import requests
from utils import logger, get_config
from utils.files_helper import FilesHelper

class DataFetcher:
    """
    DataFetcher for downloading, fetching, and saving JSONL data.

    Features:
    - Fetch data from a URL
    - Return fetched data
    - Save data to disk

    Methods:
        run() -> bytes: Fetches data from the URL and stores it internally.
        save(data=None, output_path=None): Saves the fetched or provided data to a file.
    """

    def __init__(self, data_url=None, data_path=None):
        """
        Initializes the DataFetcher with optional URL and file path.

        Args:
            data_url (str, optional): URL to fetch the data from.
            data_path (str, optional): File path to save the data.
        """
        self.data_url = data_url or get_config().SOURCE_DATA_URL
        self.data_path = data_path or get_config().PATHS.RAW
        self.data = None

        if not self.data_url:
            raise ValueError("data_url must be provided either as argument or in get_config().SOURCE_DATA_URL")
        if not self.data_path:
            raise ValueError("data_path must be provided either as argument or in get_config().PATHS.RAW")
    
    # -------------------------------------------------------------------------
    def _fetch(self):
        """Private method to fetch data from the URL and return the raw content."""
        try:
            response = requests.get(self.data_url, timeout=60)
            response.raise_for_status()
            logger.info(f"Data fetched successfully from {self.data_url}")
            return response.content
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from {self.data_url}: {e}")
            raise
    
    # -------------------------------------------------------------------------
    def run(self):
        """
        Public method that fetches the data and stores it internally.

        Returns:
            bytes: The raw content fetched from the URL.
        """
        self.data = self._fetch()
        return self.data
    
    # -------------------------------------------------------------------------
    def save(self, data=None, output_path: str = None):
        """
        Saves the provided or internally stored data to a file.

        Args:
            data (optional): Data to save; defaults to internally stored data.
            output_path (str, optional): Path to save the data; defaults to initialized path.
        """
        output_path = output_path or self.data_path
        data = data or self.data
        
        try:
            FilesHelper.save(data, output_path)
            logger.info(f"Data saved successfully to {output_path}")
            return output_path
        except OSError as e:
            logger.error(f"Failed to save data to {output_path}: {e}")
            raise
