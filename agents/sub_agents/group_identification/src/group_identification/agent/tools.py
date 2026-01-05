from smolagents import tool
from utils import logger
from typing import List, Dict
from ..identifier.louvain import LouvainGroupIdentifier
from ..identifier.saver import GroupSaver

# ---------------------------------------------------------
#  Louvain Clustering Tool
# ---------------------------------------------------------
@tool
def louvain_clustering_tool() -> Dict[str, List[str]]:
    """
    Cluster attendance based on session names using Louvain clustering.

    Returns:
        Dict[str, List[str]]: A mapping of session/session names to lists of UIDs.

        Example output:
        {
            "Group 1": ["uid1", "uid2", "uid3"],
            "Group 2": ["uid1", "uid2", "uid4"]
        }
    """
    try:
        logger.info("Starting Louvain Clustering Tool...")
        identifier = LouvainGroupIdentifier()
        groups = identifier.run()
        logger.info("Louvain Clustering Tool finished successfully!")
        return groups

    except Exception as e:
        logger.error("Error in Louvain Clustering Tool", exc_info=True)
        return f"Error in Louvain_clustering_tool: {e}"

# ---------------------------------------------------------
# Save Tool
# --------------------------------------------------------- 
@tool
def save_tool(groups: dict[str, List[str]]) -> str:
    """
    Save identified student groups to a JSON file.

    Args:
        groups (dict[str, List[str]]): A mapping of group names to lists of UIDs.
        
        Example:
        {
            "MSc-IoT": ["uid1", "uid2", "uid3"],
            "MSc-CS": ["uid1", "uid5", "uid6"]
        }

    Returns:
        str: The file path where the groups JSON was saved.

    Behavior:
        - Overwrites the previous groups file.
        - Ensures valid JSON format.
        - Returns the storage path.
    """
    try:
        logger.info("Starting Save Tool...")

        output_path = GroupSaver().save(groups)

        logger.info(f"Groups saved successfully to {output_path}")
        return output_path

    except Exception as e:
        logger.error("Error in Save Tool", exc_info=True)
        return f"Error in save_tool: {e}"
