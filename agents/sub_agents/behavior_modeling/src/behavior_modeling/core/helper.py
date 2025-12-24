from typing import Dict, Any
from utils import get_config, logger, JsonRepository
  
class Helper:
    """behavior helper"""

    def __init__(self):
        config = get_config()

        # Load sessions data
        clean_data_path = config.PATHS.PREPROCESSED
        logger.info(f"Loading session data from: {clean_data_path}")
        json_repo = JsonRepository(clean_data_path)
        json_repo.ensure_exists()
        self.sessions = json_repo.read_all()
        logger.info(f"Loaded {len(self.sessions)} sessions")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Extract schema information for debugging."""
        if not self.sessions:
            return {"total_sessions": 0, "fields": []}
        
        fields = set()
        for session in self.sessions[:10]:
            fields.update(session.keys())

        return {
            "total_sessions": len(self.sessions),
            "fields": sorted(fields),
            "sample": self.sessions[0] if self.sessions else None
        }