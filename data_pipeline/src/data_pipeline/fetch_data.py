import requests
import os
from utils import Config, logger

def fetch_data(data_url=None, save_path=None):
    data_url = data_url or Config.DATA_URL
    save_path = save_path or Config.SAVE_PATH
    
    # Validate required configuration
    if not data_url:
        raise ValueError("data_url must be provided either as argument or in Config.DATA_URL")
    if not save_path:
        raise ValueError("save_path must be provided either as argument or in Config.SAVE_PATH")

    try:
        dir_path = os.path.dirname(save_path)
        if dir_path:  # Only create directory if path includes one
            os.makedirs(dir_path, exist_ok=True)
        
        response = requests.get(data_url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Data fetched successfully and saved to {save_path}")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from {data_url}: {e}")
        raise
    except OSError as e:
        logger.error(f"Failed to write data to {save_path}: {e}")
        raise
