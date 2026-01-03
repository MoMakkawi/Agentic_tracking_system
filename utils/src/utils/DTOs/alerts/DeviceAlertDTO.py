from dataclasses import dataclass
from typing import List

@dataclass
class DeviceAlertDTO:
    id: int
    session_id: int
    device_id: str
    reasons: List[str]
