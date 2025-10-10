import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Logger configuration
LOG_FILE = os.path.join(LOG_DIR, "attendance_ai.log")
LOG_LEVEL = logging.INFO  # Could be DEBUG, INFO, WARNING, ERROR, CRITICAL

# Formatter for logs
formatter = logging.Formatter(
    fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Rotating file handler (5 MB per file, keep 5 backups)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)

# Stream handler (console output)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Create a logger
logger = logging.getLogger("Agentic_tracking_system")
logger.setLevel(LOG_LEVEL)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Optional: silence third-party loggers (like requests) if needed
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
