import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this config.py file is located
CONFIG_DIR = Path(__file__).parent

# Load .env file from the utils package directory
env_path = CONFIG_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    DATA_URL = os.getenv("DATA_URL")
    SAVE_PATH = os.getenv("SAVE_PATH")