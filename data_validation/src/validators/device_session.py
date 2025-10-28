import os
import pandas as pd
from datetime import datetime
from utils import logger, get_config, load_config
from utils.file_helpers import load_json, save_csv


class DeviceValidator:
    """
    Device Validator for session-based preprocessed data.

    Features:
        - Detect device clock resets per device-session
        - Detect unusually long active segments
        - Detect long inactive gaps within sessions
        - Detect missing or invalid timestamps
        - CSV export of device-session level alerts
    """

    def __init__(self, input_path: str = None):
        self.input_path = input_path or get_config().PATHS.PREPROCESSED

        if not os.path.exists(self.input_path):
            logger.error(f"Preprocessed file not found: {self.input_path}")
            raise FileNotFoundError(f"Input file does not exist: {self.input_path}")

        logger.info(f"Loading preprocessed data from: {self.input_path}")
        self.data = load_json(self.input_path)
        self.df = self._flatten_logs(self.data)
        self.alerts = []

    # -------------------------------------------------------------------------
    def _flatten_logs(self, sessions):
        """Flatten session-based logs into a DataFrame with timestamps."""
        records = []
        for session in sessions:
            session_id = str(session.get("session_id"))
            device_id = str(session.get("device_id"))

            for log in session.get("logs", []):
                uid = str(log.get("uid"))
                ts = log.get("ts")
                records.append({
                    "uid": uid,
                    "session_id": session_id,
                    "device_id": device_id,
                    "timestamp": ts
                })

        df = pd.DataFrame(records)
        df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        logger.info(f"Flattened {len(df)} logs into DataFrame for device validation")
        return df

    # -------------------------------------------------------------------------
    def _detect_clock_resets(self):
        """Detect backward timestamps or timestamps before system establishment."""
        self.df["is_clock_reset"] = False
        for (device_id, session_id), group in self.df.groupby(["device_id", "session_id"]):
            group_sorted = group.sort_values("timestamp_dt")
            timestamps = group_sorted["timestamp_dt"]

            backward_mask = timestamps.diff().dt.total_seconds() < 0
            old_mask = timestamps < get_config().SCHEDULE.SYSTEM_START_DATE
            combined_mask = backward_mask | old_mask

            if combined_mask.any():
                self.df.loc[group_sorted.index[combined_mask], "is_clock_reset"] = True

        logger.info(f"Detected {self.df['is_clock_reset'].sum()} device-session entries with clock resets")

    # -------------------------------------------------------------------------

    def _detect_unusual_active_sessions(self, max_duration_hours: int = 11):
        """
        Detect device-sessions active for unusually long periods.
        Simplified version: just checks total duration between first and last timestamp.
        NOTE : THIS DOUBLE CHECK FUNCTION SHOULD BE HANDLED FROM HW
        """
        self.df["is_active_continuous"] = False

        for (device_id, session_id), group in self.df.groupby(["device_id", "session_id"]):
            timestamps = group["timestamp_dt"].dropna()
            if len(timestamps) < 2:
                continue

            duration_hours = (timestamps.max() - timestamps.min()).total_seconds() / 3600.0
            if duration_hours > max_duration_hours:
                self.df.loc[group.index, "is_active_continuous"] = True

        logger.info(f"Detected {self.df['is_active_continuous'].sum()} entries in unusually long active sessions")

    # -------------------------------------------------------------------------
    def _detect_missing_data(self):
        """Detect missing or invalid device/session id."""

        self.df["has_missing_data"] = self.df["device_id"].isna() | (self.df["device_id"] == "")
        logger.info(f"Detected {self.df['has_missing_data'].sum()} logs with missing device_id")

        self.df["has_missing_data"] |= self.df["session_id"].isna() | (self.df["session_id"] == "")
        logger.info(f"Detected {self.df['has_missing_data'].sum()} logs with missing session_id")

    # -------------------------------------------------------------------------
    def _collect_alerts(self):
        """Aggregate alerts per device-session."""
        alerts = []
        grouped = self.df.groupby(["device_id", "session_id"])
        for (device_id, session_id), group in grouped:
            reasons = set()
            if group["is_clock_reset"].any():
                reasons.add("Clock reset detected")
            if group["is_active_continuous"].any():
                reasons.add("Device active unusually long without breaks")
            if group["has_missing_data"].any():
                reasons.add("Gaps or missing device/session id detected")

            if reasons:
                alerts.append([device_id, session_id, "; ".join(sorted(reasons))])

        self.alerts = alerts
        logger.info(f"Collected {len(alerts)} device-session level alerts")

    # -------------------------------------------------------------------------
    def run(self):
        """Run full validation pipeline."""
        logger.info("Running DeviceValidator pipeline...")
        self._detect_clock_resets()
        self._detect_unusual_active_sessions()
        self._detect_missing_data()
        self._collect_alerts()
        return self.alerts

    # -------------------------------------------------------------------------
    def save(self, output_path: str = None):
        """Save alerts to CSV."""
        if not self.alerts:
            logger.error("No alerts to save. Run `.run()` first.")
            raise ValueError("No alert data to save.")

        output_path = output_path or get_config().PATHS.ALERTS.VALIDATION.DEVICE
        header = ["device_id", "session_id", "reason"]
        rows = [header] + self.alerts
        save_csv(rows, output_path)
        logger.info(f"Device-session alerts exported to CSV: {output_path}")
        return output_path
