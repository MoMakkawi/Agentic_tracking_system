import os
from utils import logger, get_config
from utils import TimestampHelper
from utils import JsonlRepository, JsonRepository, IcsRepository
from datetime import datetime

class Preprocessor:
    """
    Preprocessor for JSONL attendance data.

    Features:
        - Remove redundant logs per UID
        - Keep earliest timestamps for duplicates
        - Convert logs into structured session objects
        - Track redundant UID counts per session
    """

    def __init__(self, jsonl_path: str = None, ics_path: str = None):
        self.jsonl_path = jsonl_path or get_config().PATHS.LOGS
        self.ics_path = ics_path or get_config().PATHS.ICS
        
        logger.info(f"Loading logs data from: {self.jsonl_path}")
        self.jsonl_repo = JsonlRepository(self.jsonl_path)
        self.jsonl_repo.ensure_exists()
        self.logs_data = self.jsonl_repo.read_all()

        logger.info(f"Loading ICS data from: {self.ics_path}")
        self.ics_repo = IcsRepository(self.ics_path)
        self.ics_repo.ensure_exists()
        self.ics_data = self.ics_repo.read_all()

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
                "event_context": "", # will be enriched by _enrich_session
                "matched_events": [], # will be enriched by _enrich_session
                "received_at": received_at,
                "logs_date": logs_date,
                "recorded_count": record.get("count", len(logs) + sum(redundant_uids.values())),
                "unique_count": len(logs),
                "redundant_uids": redundant_uids,
                "logs": logs
            }
            
            # Enrich session with (ics) event context
            self._enrich_session(session)

            sessions.append(session)

        logger.info(f"{len(sessions)} structured sessions generated.")
        return sessions

    # -------------------------------------------------------------------------
    def _enrich_session(self, session):
        """Enrich a session with matching calendar events."""
        received_at = session.get("received_at")
        received_at_date = TimestampHelper.to_date(received_at)
        date_str = received_at_date or session.get("logs_date")
        
        session_logs = session.get("logs", [])
        if not session_logs or not self.ics_data or not date_str:
            session["matched_events"] = []
            session["event_context"] = ""
            return

        matched_events = []
        seen_event_ids = set()

        for log in session_logs:
            log_dt = TimestampHelper.combine_date_time(date_str, log.get("ts"))
            if not log_dt:
                continue

            for event in self.ics_data:
                if event.get("id") in seen_event_ids:
                    continue
                
                if TimestampHelper.is_overlap(log_dt, event.get("start"), event.get("end")):
                    event_copy = self._prepare_event_copy(event)
                    matched_events.append(event_copy)
                    seen_event_ids.add(event.get("id"))

        session["matched_events"] = matched_events
        titles = [e.pop("_title_for_context", "Unknown Event") for e in matched_events]
        session["event_context"] = ", ".join(dict.fromkeys(titles))

    def _prepare_event_copy(self, event):
        """Create event copy with split title/details."""
        event_copy = event.copy()
        raw_summary = event_copy.get("summary", "")
        
        # Split "Title - Details" format
        if " - " in raw_summary:
            title, details = raw_summary.split(" - ", 1)
        else:
            title = details = raw_summary
        
        event_copy["summary"] = details
        event_copy["_title_for_context"] = title
        
        # Remove description
        event_copy.pop("description", None)

        return event_copy

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
