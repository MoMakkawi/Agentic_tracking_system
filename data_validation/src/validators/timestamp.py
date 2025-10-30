from datetime import datetime, time
import pandas as pd
from utils import logger, get_config, load_config
from utils.helpers import safe_parse_timestamp
from utils.files_helper import FilesHelper
import os
from collections import defaultdict


class TimestampValidator:
    """
    Timestamp Validator for session-based preprocessed data.

    Features:
        - University hours validation
        - Semester period validation
        - Weekend & holiday check-in detection
    """

    def __init__(self, input_path: str = None):
        self.input_path = input_path or get_config().PATHS.PREPROCESSED

        if not os.path.exists(self.input_path):
            logger.error(f"Preprocessed file not found: {self.input_path}")
            raise FileNotFoundError(f"Input file does not exist: {self.input_path}")

        logger.info(f"Loading preprocessed data from: {self.input_path}")
        self.data = FilesHelper.load(self.input_path)
        self.df = self._flatten_logs(self.data)
        self.alerts = []

    # -------------------------------------------------------------------------
    def run(self):
        """Execute full timestamp validation pipeline."""
        logger.info("Running TimestampValidator pipeline...")
        self._flag_out_of_date_range_checkins()
        self._flag_out_of_time_range_checkins()
        self._detect_weekend_and_holiday_checkins()
        self._collect_alerts()
        return self.alerts

    # -------------------------------------------------------------------------
    def save(self, output_path: str = None):
        """Save collected alerts to CSV."""
        if not self.alerts:
            logger.error("No alerts to save. Run `.run()` first.")
            raise ValueError("No alert data to save.")

        output_path = output_path or get_config().PATHS.ALERTS.VALIDATION.TIMESTAMP
        header = ["uid", "timestamp", "session_id", "device_id", "reason"]
        rows = [header] + self.alerts

        FilesHelper.save(rows, output_path)
        logger.info(f"Alerts exported to CSV: {output_path}")
        return output_path

    # -------------------------------------------------------------------------
    def _flatten_logs(self, sessions):
        """Flatten session-based logs into a single DataFrame for validation."""
        records = []
        for session in sessions:
            session_id = session.get("session_id")
            device_id = session.get("device_id")

            for log in session.get("logs", []):
                records.append({
                    "uid": log["uid"],
                    "timestamp": safe_parse_timestamp(log["ts"]),
                    "session_id": session_id,
                    "device_id": device_id
                })

        df = pd.DataFrame(records)
        logger.info(f"Flattened {len(df)} logs into DataFrame")
        return df

    # -------------------------------------------------------------------------
    def _flag_out_of_time_range_checkins(self):
        """Flag check-ins outside the valid daily time range."""
        cfg = get_config()
        start_time = datetime.strptime(cfg.SCHEDULE.START_TIME, "%H:%M:%S").time() if cfg.SCHEDULE.START_TIME else time(8, 0)
        end_time = datetime.strptime(cfg.SCHEDULE.END_TIME, "%H:%M:%S").time() if cfg.SCHEDULE.END_TIME else time(18, 0)

        self.df["outside_valid_time"] = ~self.df["timestamp"].dt.time.between(start_time, end_time)
        logger.info(f"Flagged {self.df['outside_valid_time'].sum()} check-ins outside valid time")

    # -------------------------------------------------------------------------
    def _flag_out_of_date_range_checkins(self):
        """Flag check-ins outside the valid semester date range."""
        cfg = get_config()
        start_date = pd.to_datetime(cfg.SCHEDULE.START_DATE)
        end_date = pd.to_datetime(cfg.SCHEDULE.END_DATE)

        self.df["outside_valid_date"] = ~self.df["timestamp"].between(start_date, end_date)
        logger.info(f"Flagged {self.df['outside_valid_date'].sum()} check-ins outside valid date")

    # -------------------------------------------------------------------------
    def _detect_weekend_and_holiday_checkins(self):
        """Detect check-ins on weekends or holidays."""
        cfg = get_config()
        holidays = cfg.SCHEDULE.HOLIDAYS or []

        self.df["is_weekend"] = self.df["timestamp"].dt.dayofweek >= 5
        self.df["is_holiday"] = self.df["timestamp"].dt.date.isin(holidays)
        self.df["invalid_day_checkin"] = self.df["is_weekend"] | self.df["is_holiday"]

        logger.info(f"Flagged {self.df['invalid_day_checkin'].sum()} check-ins on weekends/holidays")

    # -------------------------------------------------------------------------
    def _collect_alerts(self):
        """Collect and group alerts by UID, timestamp, session_id, and device_id."""
        grouped_alerts = defaultdict(set)

        for _, row in self.df.iterrows():
            key = (row["uid"], row["timestamp"].isoformat(), row["session_id"], row["device_id"])

            if row.get("outside_valid_date"):
                grouped_alerts[key].add("Outside valid date range")
            if row.get("outside_valid_time"):
                grouped_alerts[key].add("Outside valid time range")
            if row.get("invalid_day_checkin"):
                grouped_alerts[key].add("Weekend or holiday check-in")

        self.alerts = [
            [uid, ts, session_id, device_id, "; ".join(sorted(reasons))]
            for (uid, ts, session_id, device_id), reasons in grouped_alerts.items()
        ]
        logger.info(f"Collected {len(self.alerts)} unique alerts (grouped by UID & session)")
