from typing import Any, Dict, Optional
from utils import logger, get_config
from utils import JsonRepository, CsvRepository
from .executor import CodeExecutor, CodeValidator

class DataInsighter(CodeExecutor):

    def __init__(self, validator: Optional[CodeValidator] = None):
        config = get_config()

        # Load session data
        sessions_repo = JsonRepository(config.PATHS.PREPROCESSED)
        sessions_repo.ensure_exists()
        datasets = {
            "attendance_data": sessions_repo.read_all()
        }

        # Load invalid UIDs
        alerts_repo = CsvRepository(config.PATHS.ALERTS.VALIDATION.IDENTITY)
        alerts_repo.ensure_exists()
        uid_alerts = alerts_repo.read_all()
        invalid_uids = {row["uid"] for row in uid_alerts if "uid" in row}

        # Define helpers
        helpers = {
            "is_valid_id": lambda uid: uid not in invalid_uids
        }

        # Pass everything to BaseExecutor constructor
        super().__init__(
            validator=validator,
            helpers=helpers,
            datasets=datasets
        )
    