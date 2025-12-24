from smolagents import tool
from utils import logger, get_config
from typing import List, Dict
from ..core.group_identifier import GroupIdentifier

# ---------------------------------------------------------
# Attendance Mapper Tool
# ---------------------------------------------------------
@tool
def attendance_mapper_tool() -> Dict[str, List[str]]:
    """
    Map attendance based on session names.

    Returns:
        Dict[str, List[str]]: A mapping of event/session names to lists of UIDs.

        Example output:
        {
            "Coaching professionnel (R)": ["uid1", "uid2", "uid3"],
            "Communications et Réseaux pour l’IoT": ["uid1", "uid2", "uid4"]
        }

    Notes:
        - Aggregates UIDs from all sessions.
        - Splits multi-event sessions (comma-separated).
        - Ensures unique UIDs per event.
        - Sorted UIDs for consistency.
    """
    try:
        logger.info("Starting Attendance Mapper Tool...")
        identifier = GroupIdentifier()
        sessions_attendence = identifier.mapping_students_by_sessions_names()
        logger.info("Attendance Mapper Tool finished successfully!")
        return sessions_attendence

    except Exception as e:
        logger.error("Error in Attendance Mapper Tool", exc_info=True)
        return f"Error in attendance_mapper_tool: {e}"

# ---------------------------------------------------------
# Cluster Tool
# ---------------------------------------------------------
@tool
def cluster_tool() -> Dict[str, List[str]]:
    """
    Cluster attendance based on session names.

    Returns:
        Dict[str, List[str]]: A mapping of event/session names to lists of UIDs.

        Example output:
        {
            "Group 1": ["uid1", "uid2", "uid3"],
            "Group 2": ["uid1", "uid2", "uid4"]
        }

    Notes:
        - Aggregates UIDs from all sessions.
        - Splits multi-event sessions (comma-separated).
        - Ensures unique UIDs per event.
        - Sorted UIDs for consistency.
    """
    try:
        logger.info("Starting Cluster Tool...")
        identifier = GroupIdentifier()
        groups = identifier.cluster_students()
        logger.info("Cluster Tool finished successfully!")
        return groups

    except Exception as e:
        logger.error("Error in Cluster Tool", exc_info=True)
        return f"Error in cluster_tool: {e}"

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
        logger.info(f"Groups to save: {groups}")
        identifier = GroupIdentifier()
        output_path = identifier.save_groups(groups)

        logger.info(f"Groups saved successfully to {output_path}")
        return str(output_path)

    except Exception as e:
        logger.error("Error in Save Tool", exc_info=True)
        return f"Error in save_tool: {e}"
