from dataclasses import dataclass
from typing import List

@dataclass
class GroupItemDTO:
    """DTO for an individual group."""
    name: str
    members: List[str]
    member_count: int
