from typing import Any, Dict, Optional
from utils import logger, get_config
from utils import JsonRepository
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

        # Pass everything to BaseExecutor constructor
        super().__init__(
            validator=validator,
            datasets=datasets
        )
    