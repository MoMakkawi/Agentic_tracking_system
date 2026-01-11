from typing import List, Dict
from utils import JsonRepository 
from utils import logger, get_config

class GroupSaver:
    """Class responsible for saving group data to a JSON repository."""

    def __init__(self):
        """
        Initialize the GroupSaver with the path where groups will be saved.
        """
        config = get_config()
        self.output_path = config.PATHS.GROUPS

    def save(self, groups: Dict[str, List[str]]) -> str:
        """
        Save the groups to a JSON file.

        :param groups: Dictionary of groups to save.
        :return: Path where the groups were saved.
        """
        json_repo = JsonRepository(self.output_path)
        json_repo.save_all(groups)
        return self.output_path
