from dataclasses import dataclass
from datetime import datetime

@dataclass
class MatchedSessionDTO:
    id: str
    summary: str
    start: datetime
    end: datetime
