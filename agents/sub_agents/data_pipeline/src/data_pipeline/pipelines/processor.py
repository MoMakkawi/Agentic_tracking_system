import os
from utils import logger, get_config
from utils.helpers.time import TimestampHelper
from utils.storage.jsonl_repo import JsonlRepository
from utils.storage.json_repo import JsonRepository

class Preprocessor:
    """
    Preprocessor for JSONL attendance data.

    Features:
        - Remove redundant logs per UID
        - Keep earliest timestamps for duplicates
        - Convert logs into structured session objects
        - Track redundant UID counts per session
    """

    def __init__(self, jsonl_path: str = None):
        self.jsonl_path = jsonl_path or get_config().PATHS.LOGS
        self.jsonl_repo = JsonlRepository(self.jsonl_path)
        self.jsonl_repo.ensure_exists()

        logger.info(f"Loading logs data from: {self.jsonl_path}")
        self.logs_data = self.jsonl_repo.read_all()
        self.processed_sessions = []

    # -------------------------------------------------------------------------
    def run(self):
        """
        Execute full preprocessing pipeline.
        Returns processed sessions list.
        """
        logger.info("Running preprocessing pipeline...")

        cleaned_data = self._separate_redundant(self.logs_data)
        sessions = self._create_sessions(cleaned_data)

        self.processed_sessions = sessions
        logger.info(f"Pipeline completed: {len(sessions)} sessions created")

        return sessions

    # ------------------------------------------------------------------
    def _separate_redundant(self, data):
        """
        Remove redundant logs and track redundancy count per UID.
        Keep only earliest timestamp for each UID.
        """
        logger.info("Separating redundant logs within each record...")

        total_redundant = 0

        for record in data:
            logs = record.get("logs", [])
            uid_map = {}
            redundant_count = {}

            for log in logs:
                uid = log.get("uid")
                ts = log.get("ts")

                if uid not in uid_map:
                    uid_map[uid] = log
                else:
                    redundant_count[uid] = redundant_count.get(uid, 0) + 1

                    # Keep earliest timestamp
                    if ts < uid_map[uid]["ts"]:
                        redundant_count[uid] += 1
                        uid_map[uid] = log

            record["logs"] = list(uid_map.values())
            record["redundant_uids"] = redundant_count
            total_redundant += sum(redundant_count.values())

        logger.info(f"Detected {total_redundant} redundant logs in total")
        return data

    # -------------------------------------------------------------------------
    def _create_sessions(self, data):
        """Convert cleaned data into structured session dictionaries."""
        logger.info("Generating structured sessions...")
        sessions = []

        for index, record in enumerate(data, start=1):

            logs = record.get("logs", [])
            redundant_uids = record.get("redundant_uids", {})

            dates = []  # will collect YYYY-MM-DD from each log

            for log in logs:
                ts_str = TimestampHelper.adjust_dst(log["ts"])  # "YYYY-MM-DD HH:MM:SS"
                if not ts_str:
                    continue
                date_part, time_part = ts_str.split(" ")
                dates.append(date_part)
                log["ts"] = time_part

            logs_date = min(dates) if dates else None
            received_at = TimestampHelper.safe_parse(record.get("received_at"))
            logs.sort(key=lambda x: x["ts"])
            
            session = {
                "session_id": index,
                "device_id": record.get("device_id"),
                "received_at": received_at,
                "logs_date": logs_date,
                "recorded_count": record.get("count", len(logs) + sum(redundant_uids.values())),
                "unique_count": len(logs),
                "logs": logs,
                "redundant_uids": redundant_uids
            }

            sessions.append(session)

        logger.info(f"{len(sessions)} structured sessions generated.")
        return sessions

    # -------------------------------------------------------------------------
    def save(self, sessions=None, output_path: str = None):
        """
        Save processed sessions to JSON.
        Optional:
            - Pass custom session data
            - Provide custom output file path
        """
        if sessions is None:
            if not self.processed_sessions:
                logger.error("No processed sessions available to save. Run `.run()` first.")
                raise ValueError("No session data to save.")
            sessions = self.processed_sessions

        output_path = output_path or get_config().PATHS.PREPROCESSED
        json_repo = JsonRepository(output_path)
        json_repo.save_all(sessions)
        logger.info(f"Preprocessed data saved to: {output_path}")
        return output_path
