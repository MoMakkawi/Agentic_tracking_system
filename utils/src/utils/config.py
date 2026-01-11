import json
import os
import time
import threading
from dataclasses import dataclass
from logger import *

# -----------------------------
# Recursive wrapper for any dict
# -----------------------------
class DotDict:
    """Recursively convert a dict to an object with dot-access."""
    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                value = DotDict(value)  # recurse for nested dict
            elif isinstance(value, list):
                value = [DotDict(v) if isinstance(v, dict) else v for v in value]  # handle lists of dicts
            setattr(self, key, value)

    def to_dict(self):
        """Convert back to regular dict recursively."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DotDict):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [v.to_dict() if isinstance(v, DotDict) else v for v in value]
            result[key] = value
        return result

# -----------------------------
# Top-level config dataclass
# -----------------------------
@dataclass
class Config:
    raw: DotDict

    def __getattr__(self, item):
        # Delegate attribute access to the DotDict
        return getattr(self.raw, item)

# -----------------------------
# Module-level cache
# -----------------------------
_config_instance: Config | None = None
_watcher_thread: threading.Thread | None = None
_stop_watcher = False

# -----------------------------
# Load config function
# -----------------------------
def _load_data(path: str) -> dict:
    """Helper to read and process the config file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Override top-level keys with environment variables if they exist
        for key in data.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                try:
                    data[key] = json.loads(env_value)  # parse JSON string if possible
                except json.JSONDecodeError:
                    data[key] = env_value
        return data
    except Exception as e:
        logger.error(f"Error reading config data from {path}: {e}")
        raise

def _watch_config(path: str):
    """Background thread to watch for file changes."""
    last_mtime = 0
    try:
        last_mtime = os.stat(path).st_mtime
    except FileNotFoundError:
        pass

    while not _stop_watcher:
        time.sleep(10)  # Check every 10 seconds
        try:
            current_mtime = os.stat(path).st_mtime
            if current_mtime != last_mtime:
                logger.info(f"Config file {path} changed, reloading...")
                last_mtime = current_mtime
                try:
                    new_data = _load_data(path)
                    if _config_instance:
                        # Update the existing DotDict in place so references remain valid if possible,
                        # but since DotDict structure might change, we replace the raw attribute.
                        _config_instance.raw = DotDict(new_data)
                        logger.info("Configuration reloaded successfully")
                except Exception as e:
                    logger.error(f"Failed to reload config: {e}")
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error in config watcher: {e}")

def load_config(path="config.json", start_watcher=True) -> Config:
    """
    Load the configuration from a JSON file (with optional env overrides)
    and wrap it recursively in DotDict for dot-access.
    """
    global _config_instance, _watcher_thread

    if _config_instance is None:
        try:
            logger.info(f"Loading configuration from {path}")
            data = _load_data(path)

            # Wrap entire config in DotDict
            _config_instance = Config(raw=DotDict(data))
            logger.info("Configuration loaded successfully")
            
            if start_watcher and _watcher_thread is None:
                _watcher_thread = threading.Thread(target=_watch_config, args=(path,), daemon=True)
                _watcher_thread.start()
                logger.info(f"Started config watcher for {path}")
                
        except FileNotFoundError:
            logger.error(f"Config file {path} not found")
            try:
                # Try to look one directory up if running from subfolder
                parent_path = os.path.join("..", path)
                if os.path.exists(parent_path):
                     logger.info(f"Found config at {parent_path}, retrying...")
                     return load_config(parent_path, start_watcher)
            except:
                pass
            raise
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    else:
        logger.debug("Config already loaded, using cached instance")
    return _config_instance

# -----------------------------
# Get config function
# -----------------------------
def get_config() -> Config:
    """
    Retrieve the already loaded configuration.
    Raises an error if load_config() hasn't been called yet.
    """
    if _config_instance is None:
        logger.error("Config not loaded yet. Call load_config() first.")
        raise RuntimeError("Config not loaded yet. Call load_config() first.")
    return _config_instance