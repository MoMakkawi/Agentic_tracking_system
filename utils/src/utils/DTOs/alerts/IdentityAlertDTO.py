from dataclasses import dataclass
from typing import List

@dataclass
class IdentityAlertDTO:
    id: int
    uid: str
    device_id: str
    normal_sessions_count: int
    repeated_anomaly_count: int
    anomaly_sessions: List[int]
    reasons: List[str]
