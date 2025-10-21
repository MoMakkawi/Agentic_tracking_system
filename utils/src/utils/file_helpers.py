import csv
import json
import os
from logger import *

# ---------------------------------------------------------
# CSV functions
# ---------------------------------------------------------
def save_csv(rows, file_path):
    """
    Save rows to a CSV file.
    Each row is a list of values.
    Creates the directory if it does not exist.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        logger.info(f"CSV saved successfully: {file_path}")
        logger.debug(f"Total rows saved: {len(rows)}")
    except Exception as e:
        logger.exception(f"Error while saving CSV '{file_path}': {e}")
        raise


def load_csv(file_path):
    """
    Load raw CSV data into a list of rows.
    """
    try:
        with open(file_path, "r", newline="") as f:
            reader = csv.reader(f)
            rows = [row for row in reader if row]
        logger.info(f"CSV loaded successfully: {file_path}")
        logger.debug(f"Total rows read: {len(rows)}")
        return rows
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.exception(f"Error while loading CSV '{file_path}': {e}")
        raise


# ---------------------------------------------------------
# JSON functions
# ---------------------------------------------------------
def save_json(data, file_path, indent=4):
    """
    Save a Python object to a JSON file.
    Creates the directory if it does not exist.

    Args:
        data: Any JSON-serializable object
        file_path (str): Output JSON path
        indent (int): Indentation level for readability
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=indent)
        logger.info(f"JSON saved successfully: {file_path}")
        logger.debug(f"JSON keys/length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
    except Exception as e:
        logger.exception(f"Error while saving JSON '{file_path}': {e}")
        raise


def load_json(file_path):
    """
    Load a JSON file and return the Python object.
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logger.info(f"JSON loaded successfully: {file_path}")
        logger.debug(f"JSON keys/length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        return data
    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in '{file_path}': {e}")
        raise
    except Exception as e:
        logger.exception(f"Error while loading JSON '{file_path}': {e}")
        raise


# ---------------------------------------------------------
# JSONL functions
# ---------------------------------------------------------
def load_jsonl(file_path: str):
    """
    Load a JSONL (JSON Lines) file and return a list of Python objects.
    
    Each line in the file must be a valid JSON object.
    """
    data = []
    try:
        with open(file_path, "r") as f:
            for i, line in enumerate(f, start=1):
                try:
                    obj = json.loads(line.strip())
                    data.append(obj)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON on line {i} in '{file_path}': {e}")
                    continue  # skip invalid line
        logger.info(f"JSONL loaded successfully: {file_path}")
        logger.debug(f"Total records loaded: {len(data)}")
        return data

    except FileNotFoundError:
        logger.error(f"JSONL file not found: {file_path}")
        raise
    except Exception as e:
        logger.exception(f"Error while loading JSONL '{file_path}': {e}")
        raise