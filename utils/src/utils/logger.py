import logging
import os
from logging.handlers import RotatingFileHandler
import inspect
import pathlib

ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "agentic_tracking_system.log"
LOG_LEVEL = logging.INFO

# Formatter
formatter = logging.Formatter(
    fmt="%(asctime)s | %(caller_path)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -------------------------------
# Filter to add package | file
# -------------------------------

# -------------------------------
# Filter to add package | file
# -------------------------------
class PackageFileFilter(logging.Filter):
    def filter(self, record):
        for frame_info in inspect.stack()[1:]:
            filename = frame_info.filename
            if filename.endswith("logger.py") or "logging" in filename:
                continue
            
            # Calculate relative path from ROOT_DIR
            p = pathlib.Path(filename).resolve()
            try:
                rel_path = p.relative_to(ROOT_DIR)
            except ValueError:
                rel_path = p
            
            record.caller_path = str(rel_path)
            break
        else:
            record.caller_path = "__unknown__"
        return True


# -------------------------------
# Single logger instance
# -------------------------------
logger = logging.getLogger("Agentic_tracking_system")
logger.setLevel(LOG_LEVEL)

# Add handlers only once
if not logger.handlers:
    # File handler with robust settings
    file_handler = RotatingFileHandler(
        str(LOG_FILE), 
        mode='a', 
        maxBytes=50*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(PackageFileFilter())

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(PackageFileFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Silence noisy libraries
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
