import logging
import os
from logging.handlers import RotatingFileHandler
import inspect
import pathlib

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "agentic_tracking_system.log")
LOG_LEVEL = logging.INFO

# Formatter
formatter = logging.Formatter(
    fmt="%(asctime)s | %(package_file)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File and console handlers
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# -------------------------------
# Filter to add package | file
# -------------------------------
class PackageFileFilter(logging.Filter):
    def filter(self, record):
        for frame_info in inspect.stack()[1:]:
            filename = frame_info.filename
            if filename.endswith("logger.py") or "logging" in filename:
                continue
            file_name = pathlib.Path(filename).stem
            module_name = frame_info.frame.f_globals.get("__name__", "")
            if module_name == "__main__":
                try:
                    rel_path = pathlib.Path(filename).resolve().relative_to(pathlib.Path.cwd())
                    package = rel_path.parts[0] if len(rel_path.parts) > 1 else "__main__"
                except ValueError:
                    package = "__main__"
            else:
                package = module_name.split(".")[0] if module_name else "__unknown__"
            record.package_file = f"{package} | {file_name}"
            break
        else:
            record.package_file = "__unknown__ | __unknown__"
        return True

file_handler.addFilter(PackageFileFilter())
console_handler.addFilter(PackageFileFilter())

# -------------------------------
# Single logger instance
# -------------------------------
logger = logging.getLogger("Agentic_tracking_system")
logger.setLevel(LOG_LEVEL)

# Add handlers only once
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Silence noisy libraries
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
