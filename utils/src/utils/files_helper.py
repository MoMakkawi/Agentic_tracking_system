import csv
import json
import os
from logger import *

class FilesHelper:
    # ---------------------------------------------------------
    # Generic save/load functions
    # ---------------------------------------------------------
    @staticmethod
    def save(data, file_path):
        """
        Save data to CSV, JSON, or JSONL based on file extension.

        Args:
            data: Data to save
            file_path (str): Path including file extension
        """
        FilesHelper._ensure_dir(file_path)

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".csv":
            FilesHelper._save_csv(data, file_path)
        elif ext == ".json":
            FilesHelper._save_json(data, file_path)
        elif ext == ".jsonl":
            FilesHelper._save_jsonl(data, file_path)
        else:
            raise ValueError(f"Unsupported file extension for saving: {ext}")

    @staticmethod
    def load(file_path):
        """
        Load data from CSV, JSON, or JSONL based on file extension.

        Args:
            file_path (str): Path including file extension

        Returns:
            Data loaded from the file
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".csv":
            return FilesHelper._load_csv(file_path)
        elif ext == ".json":
            return FilesHelper._load_json(file_path)
        elif ext == ".jsonl":
            return FilesHelper._load_jsonl(file_path)
        else:
            raise ValueError(f"Unsupported file extension for loading: {ext}")



    # ---------------------------------------------------------
    # Private helper functions
    # ---------------------------------------------------------
    @staticmethod
    def _ensure_dir(file_path: str):
        """
        Ensure the directory for the given file path exists.
        """
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)


    # ---------------------------------------------------------
    # CSV functions
    # ---------------------------------------------------------
    @staticmethod
    def _save_csv(rows, file_path):
        """
        Save rows to a CSV file.
        Each row is a list of values.
        Creates the directory if it does not exist.
        """
        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            logger.info(f"CSV saved successfully: {file_path}")
            logger.debug(f"Total rows saved: {len(rows)}")
        except Exception as e:
            logger.exception(f"Error while saving CSV '{file_path}': {e}")
            raise

    @staticmethod
    def _load_csv(file_path):
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
    @staticmethod
    def _save_json(data, file_path):
        """
        Save a Python object to a JSON file.
        Creates the directory if it does not exist.

        Args:
            data: Any JSON-serializable object
            file_path (str): Output JSON path
        """
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            logger.info(f"JSON saved successfully: {file_path}")
            logger.debug(f"JSON keys/length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        except Exception as e:
            logger.exception(f"Error while saving JSON '{file_path}': {e}")
            raise

    @staticmethod
    def _load_json(file_path):
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
    @staticmethod
    def _save_jsonl(content, file_path: str):
        """
        Save raw JSONL content to a file.

        Args:
            content (bytes or str): Raw JSONL data
            file_path (str): Path to save the JSONL file
        """
        # For JSONL, if data is list of objects, convert to string lines
        if isinstance(content, (list, tuple)):
            content = "\n".join(json.dumps(obj, ensure_ascii=False) for obj in data)
        elif isinstance(content, bytes):
            content = content.decode("utf-8")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"JSONL content saved successfully to: {file_path}")
            return file_path
        except Exception as e:
            logger.exception(f"Error while saving JSONL '{file_path}': {e}")
            raise

    @staticmethod
    def _load_jsonl(file_path: str):
        """
        Load a JSONL (JSON Lines) file and return a list of Python objects.
        
        Each line in the file must be a valid JSON object.
        """
        data = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
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
