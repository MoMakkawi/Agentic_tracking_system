from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class TimestampAlertDTO:
    id: int
    uid: str
    timestamp: datetime
    session_id: int
    device_id: str
    reasons: list[str]
