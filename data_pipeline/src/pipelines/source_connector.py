import requests
import os
from utils import logger, get_config

def fetch_data(data_url=None, data_path=None):
    data_url = data_url or get_config().SOURCE_DATA_URL
    data_path = data_path or get_config().PATHS.RAW
    
    # Validate required configuration
    if not data_url:
        raise ValueError("data_url must be provided either as argument or in get_config().SOURCE_DATA_URL")
    if not data_path:
        raise ValueError("data_path must be provided either as argument or in get_config()")

    try:
        dir_path = os.path.dirname(data_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        response = requests.get(data_url, timeout=60)
        response.raise_for_status()
        
        with open(data_path, "wb") as f:
            f.write(response.content)

        return data_path
        
        logger.info(f"Data fetched successfully and saved to {data_path}")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from {data_url}: {e}")
        raise
    except OSError as e:
        logger.error(f"Failed to write data to {data_path}: {e}")
        raise
