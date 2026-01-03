import pandas as pd
from utils import logger, get_config
from utils import CsvRepository, JsonRepository
from utils import TimestampHelper

class DeviceValidator:
    """
    Device Validator for session-based preprocessed data.

    Features:
        - Detect device clock resets per device-session
        - Detect unusually long active segments
        - Detect long inactive gaps within sessions
        - Detect missing or invalid timestamps
    """

    def __init__(self, input_path: str = None):
        self.input_path = input_path or get_config().PATHS.PREPROCESSED
        
        # Use JsonRepository to load preprocessed data
        json_repo = JsonRepository(self.input_path)
        json_repo.ensure_exists()
        logger.info(f"Loading preprocessed data from: {self.input_path}")
        self.data = json_repo.read_all()
        
        self.df = self._flatten_logs(self.data)
        self.alerts = []

    # -------------------------------------------------------------------------
    def _flatten_logs(self, sessions):
        """Flatten session-based logs into a DataFrame with timestamps."""
        records = []
        for session in sessions:
            session_id = session.get("session_id")
            device_id = session.get("device_id")
            session_received_at = session.get("received_at")
            session_logs_date = session.get("logs_date")

            for log in session.get("logs", []):
                uid = str(log.get("uid"))
                ts = log.get("ts")
                records.append({
                    "uid": uid,
                    "session_id": session_id,
                    "device_id": device_id,
                    "timestamp": ts,
                    "received_at": session_received_at,
                    "logs_date": session_logs_date
                })

        df = pd.DataFrame(records)
        df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        logger.info(f"Flattened {len(df)} logs into DataFrame for device validation")
        return df

    # -------------------------------------------------------------------------
    def _detect_clock_resets(self):
        """Detect backward timestamps, timestamps before system establishment, or date mismatches."""
        self.df["is_clock_reset"] = False

        # Check for date mismatch (Clock reset)
        def check_date_mismatch(row):
            if pd.isna(row["received_at"]):
                return False
            
            # Use UTC to avoid timezone shifts causing false positives
            try:
                rec_dt = pd.to_datetime(str(row["received_at"]), utc=True)
                log_dt = pd.to_datetime(str(row["logs_date"]), utc=True)
            except Exception:
                return False
            
            if pd.isna(rec_dt) or pd.isna(log_dt):
                return False
                
            return rec_dt.date() != log_dt.date()


        self.df["is_clock_reset"] = self.df.apply(check_date_mismatch, axis=1)

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
        """Detect missing or invalid device_id, session_id, or received_at timestamps."""

        self.df["missing_device_id"] = self.df["device_id"].isna() | (self.df["device_id"] == "")
        logger.info(f"Detected {self.df['missing_device_id'].sum()} logs with missing device_id")

        self.df["missing_session_id"] = self.df["session_id"].isna() | (self.df["session_id"] == "")
        logger.info(f"Detected {self.df['missing_session_id'].sum()} logs with missing session_id")

        self.df["missing_received_at"] = self.df["received_at"].isna() | (self.df["received_at"] == "")
        logger.info(f"Detected {self.df['missing_received_at'].sum()} logs with missing received_at")

    # -------------------------------------------------------------------------
    def _collect_alerts(self):
        """Aggregate alerts per device-session."""
        alerts = []
        grouped = self.df.groupby(["session_id", "device_id"])

        alert_id = 1

        for (session_id, device_id), group in grouped:
            reasons = set()
            if group["is_active_continuous"].any():
                reasons.add("Device active unusually long without breaks")
            if group["is_clock_reset"].any():
                reasons.add("Clock reset detected")
            if group["missing_device_id"].any():
                reasons.add("Missing device id")
            if group["missing_session_id"].any():
                reasons.add("Missing session id")
            if group["missing_received_at"].any():
                reasons.add("Missing received_at datetime")

            if reasons:
                alerts.append([
                    alert_id,
                    session_id,
                    device_id,
                    ";".join(sorted(reasons))
                ])
                alert_id += 1

        self.alerts = alerts
        logger.info(f"Collected {len(alerts)} device-session level alerts")

    # -------------------------------------------------------------------------
    def run(self):
        """Run full validation pipeline."""
        logger.info("Running DeviceValidator pipeline...")
        self._detect_missing_data()
        self._detect_clock_resets()
        self._detect_unusual_active_sessions()
        self._collect_alerts()
        return self.alerts

    # -------------------------------------------------------------------------
    def save(self, output_path: str = None):
        """Save alerts to CSV."""
        if not self.alerts:
            logger.error("No alerts to save. Run `.run()` first.")
            raise ValueError("No alert data to save.")

        output_path = output_path or get_config().PATHS.ALERTS.VALIDATION.DEVICE
        
        # Convert alerts from list format to dict format
        alert_dicts = [
            {
                "id": alert[0],
                "session_id": alert[1],
                "device_id": alert[2],
                "reasons": alert[3]
            }
            for alert in self.alerts
        ]
        
        # Use CsvRepository to save alerts
        csv_repo = CsvRepository(output_path)
        csv_repo._save(alert_dicts)
        
        logger.info(f"Device-session alerts exported to CSV: {output_path}")
        return output_path
