from typing import Any, Dict, Optional
from utils import logger, get_config
from utils import JsonRepository, CsvRepository
from .executor import CodeExecutor, CodeValidator

class AlertsInsighter(CodeExecutor):

    def __init__(self, validator: Optional[CodeValidator] = None):
        config = get_config()

        # Load alerts data
        identity_alerts_repo = CsvRepository(config.PATHS.ALERTS.VALIDATION.IDENTITY)
        identity_alerts_repo.ensure_exists()
        identity_alerts_data = identity_alerts_repo.read_all()

        timestamp_alerts_repo = CsvRepository(config.PATHS.ALERTS.VALIDATION.TIMESTAMP)
        timestamp_alerts_repo.ensure_exists()
        timestamp_alerts_data = timestamp_alerts_repo.read_all()

        device_alerts_repo = CsvRepository(config.PATHS.ALERTS.VALIDATION.DEVICE)
        device_alerts_repo.ensure_exists()
        device_alerts_data = device_alerts_repo.read_all()

        # Pass everything to BaseExecutor constructor
        super().__init__(
            validator=validator,
            datasets={
                "identity_alerts": identity_alerts_data,
                "timestamp_alerts": timestamp_alerts_data,
                "device_alerts": device_alerts_data
            }
        )
    