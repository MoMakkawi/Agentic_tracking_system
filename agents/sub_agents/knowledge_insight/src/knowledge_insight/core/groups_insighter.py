from typing import Any, Dict, Optional
from utils import logger, get_config
from utils import JsonRepository, CsvRepository
from .executor import CodeExecutor, CodeValidator

class GroupInsighter(CodeExecutor):

    def __init__(self, validator: Optional[CodeValidator] = None):
        config = get_config()

        # Load session data
        groups_repo = JsonRepository(config.PATHS.GROUPS)
        groups_repo.ensure_exists()
        datasets = {
            "groups_data": groups_repo.read_all()
        }

        # Pass everything to BaseExecutor constructor
        super().__init__(
            validator=validator,
            datasets=datasets
        )
    