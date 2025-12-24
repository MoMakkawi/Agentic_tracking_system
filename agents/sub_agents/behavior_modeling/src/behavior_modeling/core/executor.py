import statistics
import json
from typing import Dict, Any, List
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from utils import get_config, logger, CsvRepository, JsonRepository

class Executor:
    """Executor python code after data loading"""

    def __init__(self):
        config = get_config()

        # Load sessions data
        clean_data_path = config.PATHS.PREPROCESSED
        logger.info(f"Loading session data from: {clean_data_path}")
        json_repo = JsonRepository(clean_data_path)
        json_repo.ensure_exists()
        self.sessions = json_repo.read_all()
        logger.info(f"Loaded {len(self.sessions)} sessions")

        # Load ID alerts
        id_alerts_path = config.PATHS.ALERTS.VALIDATION.IDENTITY
        logger.info(f"Loading invalid UIDs from: {id_alerts_path}")
        csv_repo = CsvRepository(id_alerts_path)
        csv_repo.ensure_exists()
        self.id_alerts = csv_repo.read_all()
        
        # Build invalid UID set for fast lookup
        self.invalid_uids = {row["uid"] for row in self.id_alerts if "uid" in row}
        logger.info(f"Loaded {len(self.invalid_uids)} invalid UIDs")

    def _is_valid_id(self, uid: str) -> bool:
        """Check if UID is valid."""
        return uid not in self.invalid_uids

    def execute_generated_code(self, code: str) -> str:
        """
        Execute Python code in controlled namespace.
        
        Args:
            code: Python code string that assigns result to 'result' variable
            
        Returns:
            Formatted result string
        """
        try:
            # Build execution namespace
            namespace = {
                # Data
                "attendance_data": self.sessions,
                
                # Helper functions
                "is_valid_id": self._is_valid_id,
                
                # Standard library modules
                "statistics": statistics,
                "defaultdict": defaultdict,
                "Counter": Counter,
                "datetime": datetime,
                "timedelta": timedelta,
                "json": json,
                
                # Built-in functions commonly needed
                "len": len,
                "sum": sum,
                "max": max,
                "min": min,
                "sorted": sorted,
                "list": list,
                "dict": dict,
                "set": set,
                "str": str,
                "int": int,
                "float": float,
                
                # Result placeholder
                "result": None,
            }

            # Execute code
            logger.info("Executing generated code...")
            exec(code, namespace)

            # Extract result
            result = namespace.get("result")
            
            if result is None:
                return "ERROR: Code executed but 'result' variable was not assigned"

            # Format output
            if isinstance(result, (dict, list)):
                formatted = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                formatted = str(result)
            
            logger.info(f"Execution successful. Result type: {type(result).__name__}")
            return formatted

        except SyntaxError as e:
            error_msg = f"SYNTAX ERROR: {e}\nLine {e.lineno}: {e.text}"
            logger.error(error_msg)
            return error_msg
        
        except NameError as e:
            error_msg = f"NAME ERROR: {e}\nAvailable variables: attendance_data, is_valid_id"
            logger.error(error_msg)
            return error_msg
        
        except Exception as e:
            error_msg = f"EXECUTION ERROR: {type(e).__name__}: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg