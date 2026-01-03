from dataclasses import dataclass
from typing import Dict, List

@dataclass
class GroupsDTO:
    groups: Dict[str, List[str]]