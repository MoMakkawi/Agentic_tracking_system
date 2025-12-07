from typing import Dict, List, Optional
from utils import logger, get_config
from utils import JsonRepository

class GroupIdentifier:
    """
    Performs identification and saving of student attendance groups.

    Workflow:
        1. Load preprocessed attendance sessions from storage.
        2. Group UIDs by event name (splitting multi-event entries).
        3. Save the final group mapping to a JSON file.

    Methods:
        - mapping_students_by_sessions_names(): Returns { event_name: [uids] }
        - save_groups(groups): Saves the mapping to JSON.
    """
    
    def __init__(self):
        config = get_config()
        self.clean_data_path = config.PATHS.PREPROCESSED
        logger.info(f"Loading session data from: {self.clean_data_path}")
        json_repo = JsonRepository(self.clean_data_path)
        json_repo.ensure_exists()
        self.sessions = json_repo.read_all()
        logger.info(f"Loaded {len(self.sessions)} sessions successfully!")
        self.output_path = config.PATHS.GROUPS

    def mapping_students_by_sessions_names(self) -> dict[str, List[str]]:
        groups: dict[str, set] = {}
        
        for session in self.sessions:
            event_context = session.get("event_context", "")
            logs = session.get("logs", [])
            
            # Extract UIDs from this session
            uids = {log.get("uid") for log in logs if log.get("uid")}
            
            if not event_context:
                continue
                
            # Split event names (assuming comma separation as per processor.py)
            # "Coaching professionnel, Communications et Réseaux pour l’IoT" -> ["Coaching professionnel", "Communications et Réseaux pour l’IoT"]
            events = [e.strip() for e in event_context.split(",")]
            
            for event in events:
                if not event:
                    continue
                
                if event not in groups:
                    groups[event] = set()
                
                groups[event].update(uids)
        
        # Convert sets to sorted lists for JSON serialization and consistency
        return {event: sorted(list(uids)) for event, uids in groups.items()}
    
    def save_groups(self, groups: dict[str, List[str]]) -> str:
        logger.info(f"Saving groups {groups} to: {self.output_path}")
        json_repo = JsonRepository(self.output_path)
        json_repo.save_all(groups)
        logger.info(f"Saved successfully groups to: {self.output_path}")
        return json_repo.path