import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this Secrets.py file is located
SECRETS_DIR = Path(__file__).parent

# Load .env file from the utils package directory
env_path = SECRETS_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Secrets:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")