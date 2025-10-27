from utils import logger, get_config
from utils.helpers import safe_parse_timestamp
from utils.file_helpers import save_json, load_jsonl
import os


class Preprocessor:
    """
    Preprocessing for JSONL attendance data with tracking of redundant logs.
    """

    def __init__(self, jsonl_path: str = None):
        self.jsonl_path = jsonl_path or get_config().FETCHED_DATA_PATH

        if not self.jsonl_path or not os.path.exists(self.jsonl_path):
            logger.error(f"JSONL path not found or invalid: {self.jsonl_path}")
            raise FileNotFoundError(f"Input file not found: {self.jsonl_path}")

        self.raw_data = load_jsonl(self.jsonl_path)
        self.processed_sessions = []
        logger.info(f"Preprocessor initialized with file: {self.jsonl_path}")

    # ------------------------------------------------------------------
    def run(self):
        """
        Execute full preprocessing pipeline.
        Returns processed sessions list.
        """
        logger.info("Running preprocessing pipeline...")

        cleaned_data = self._separate_redundant(self.raw_data)
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

        logger.info(f"Identified {total_redundant} redundant logs in total")
        return data

    # ------------------------------------------------------------------
    def _create_sessions(self, data):
        """
        Convert cleaned raw data into structured sessions.
        """
        logger.info("Generating structured session objects...")
        sessions = []

        for index, record in enumerate(data, start=1):
            logs = record.get("logs", [])
            redundant_uids = record.get("redundant_uids", {})

            # Parse timestamps in main logs
            for log in logs:
                log["ts"] = str(safe_parse_timestamp(log["ts"]))

            logs.sort(key=lambda x: x["ts"])

            session = {
                "session_id": f"session_{index}",
                "device_id": record.get("device_id"),
                "recorded_count": record.get("count", len(logs) + sum(redundant_uids.values())),
                "unique_count": len({log["uid"] for log in logs}),
                "logs": logs,
                "redundant_uids": redundant_uids
            }
            sessions.append(session)

        logger.info(f"{len(sessions)} sessions generated successfully.")
        return sessions

    # ------------------------------------------------------------------
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

        output_path = output_path or get_config().PREPROCESSED_DATA_PATH
        save_json(sessions, output_path)
        logger.info(f"Preprocessed data saved to: {output_path}")
        return output_path
