import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from logger import *

load_dotenv()

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

# -----------------------------
# Load config function
# -----------------------------
def load_config(path="config.json") -> Config:
    """
    Load the configuration from a JSON file (with optional env overrides)
    and wrap it recursively in DotDict for dot-access.
    """
    global _config_instance
    if _config_instance is None:
        try:
            logger.info(f"Loading configuration from {path}")
            with open(path, "r") as f:
                data = json.load(f)

            # Override top-level keys with environment variables if they exist
            for key in data.keys():
                env_value = os.getenv(key)
                if env_value is not None:
                    logger.info(f"Overriding {key} with environment variable")
                    try:
                        data[key] = json.loads(env_value)  # parse JSON string if possible
                    except json.JSONDecodeError:
                        data[key] = env_value

            # Wrap entire config in DotDict
            _config_instance = Config(raw=DotDict(data))
            logger.info("Configuration loaded successfully")
        except FileNotFoundError:
            logger.error(f"Config file {path} not found")
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

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    print("NAME -> ", load_config().LLM_MODULES.DATA_PIPELINE.MODEL.NAME)
