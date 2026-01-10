import re
import pandas as pd
from utils import logger, get_config, load_config
from utils import JsonRepository, CsvRepository

class IdentityValidator:
    """
    Identity Validator for session-based preprocessed data.

    Features:
        - Aggregate alerts per UID & Device
        - Track repeated anomalies across sessions
        - Consistent UID and Device typing
    """

    def __init__(self, input_path: str = None):
        self.input_path = input_path or get_config().PATHS.PREPROCESSED

        json_repo = JsonRepository(self.input_path)
        json_repo.ensure_exists()
        logger.info(f"Loading preprocessed data from: {self.input_path}")
        self.data = json_repo.read_all()

        self.df = self._flatten_logs(self.data)
        self.uid_meta = {}
        self.alerts = []

    # -------------------------------------------------------------------------
    def _flatten_logs(self, sessions):
        """Flatten session-based logs into a single DataFrame with consistent IDs."""
        records = []
        for session in sessions:
            session_id = str(session.get("session_id"))
            device_id = str(session.get("device_id"))
            redundant_dict = session.get("redundant_uids", {})

            for log in session.get("logs", []):
                uid = log.get("uid")
                redundant_count = redundant_dict.get(uid, 0)
                records.append({
                    "uid": uid,
                    "session_id": session_id,
                    "device_id": device_id,
                    "redundant_count": int(redundant_count or 0)
                })

        df = pd.DataFrame(records)
        logger.info(f"Flattened {len(df)} logs into DataFrame for identity validation")
        return df

    # -------------------------------------------------------------------------
    def _flag_suspicious_patterns(self):
        pattern = re.compile(r"^(?=.*[a-z])(?=.*\d)[0-9a-f]{8,9}$")
        self.df["uid_suspicious_pattern"] = ~self.df["uid"].astype(str).apply(lambda x: bool(pattern.match(x)))
        logger.info(f"Flagged {self.df['uid_suspicious_pattern'].sum()} suspicious UID patterns")

    # -------------------------------------------------------------------------
    def _flag_session_redundant_uids(self):
        self.df["uid_redundant"] = self.df["redundant_count"] > 1
        logger.info(f"Flagged {self.df['uid_redundant'].sum()} redundant UIDs within sessions")

    # -------------------------------------------------------------------------
    def _flag_global_rare_uids(self):
        uid_counts = self.df["uid"].value_counts()
        self.df["uid_rare_global"] = self.df["uid"].map(lambda x: uid_counts[x] <= 1)
        logger.info(f"Flagged {self.df['uid_rare_global'].sum()} globally rare UIDs")

    # -------------------------------------------------------------------------
    def _track_repeated_anomalies(self):
        """Track anomaly sessions and repeated anomalies per UID."""
        anomaly_cols = ["uid_suspicious_pattern", "uid_redundant", "uid_rare_global"]
        self.df["has_anomaly"] = self.df[anomaly_cols].any(axis=1)

        anomaly_sessions = (
            self.df[self.df["has_anomaly"]]
            .groupby("uid")["session_id"]
            .agg(lambda s: sorted(set(s.astype(str))))
            .reset_index(name="anomaly_sessions_list")
        )

        all_sessions = (
            self.df.groupby("uid")["session_id"]
            .agg(lambda s: sorted(set(s.astype(str))))
            .reset_index(name="all_sessions_list")
        )

        anomaly_sessions["repeated_anomaly_count"] = anomaly_sessions["anomaly_sessions_list"].apply(len)
        all_sessions["all_sessions_count"] = all_sessions["all_sessions_list"].apply(len)

        uid_meta = all_sessions.merge(anomaly_sessions, on="uid", how="left")
        uid_meta["anomaly_sessions_list"] = uid_meta["anomaly_sessions_list"].apply(lambda x: x if isinstance(x, list) else [])
        uid_meta["repeated_anomaly_count"] = uid_meta["repeated_anomaly_count"].fillna(0).astype(int)

        self.uid_meta = uid_meta.set_index("uid").to_dict(orient="index")
        logger.info(f"Tracked repeated anomalies for {len(uid_meta)} UIDs")

    # -------------------------------------------------------------------------
    def _collect_alerts(self):
        """Collect UID-device level alerts."""
        alerts = []
        grouped = self.df.groupby(["uid", "device_id"])

        alert_id = 1 

        for (uid, device_id), group in grouped:
            all_sessions = sorted(set(group["session_id"].astype(str)))
            meta = self.uid_meta.get(uid, {})
            anomaly_sessions = sorted(meta.get("anomaly_sessions_list", []))
            repeated_count = int(meta.get("repeated_anomaly_count", 0))
            normal_sessions_count = len(set(all_sessions) - set(anomaly_sessions))

            allow_clustering = 1
            reasons = set()
            if group["uid_suspicious_pattern"].any():
                reasons.add("Suspicious UID pattern")
                allow_clustering = 0
            if group["uid_rare_global"].any():
                reasons.add("Globally rare UID")
                allow_clustering = 0
            if group["uid_redundant"].any():
                reasons.add("Redundant UID in sessions")
            if repeated_count > 1:
                reasons.add("Repeated anomaly across sessions")

            if reasons:
                alerts.append([
                    alert_id,                          
                    uid,
                    allow_clustering,
                    device_id,
                    normal_sessions_count,
                    repeated_count,
                    ";".join(anomaly_sessions),
                    ";".join(sorted(reasons))
                ])
                alert_id += 1

        self.alerts = alerts
        logger.info(f"Collected {len(alerts)} UID-device level identity alerts")

    # -------------------------------------------------------------------------
    def run(self):
        """Execute full identity validation pipeline."""
        logger.info("Running IdentityValidator pipeline...")
        self._flag_suspicious_patterns()
        self._flag_session_redundant_uids()
        self._flag_global_rare_uids()
        self._track_repeated_anomalies()
        self._collect_alerts()
        return self.alerts

    # -------------------------------------------------------------------------
    def save(self, output_path: str = None):
        """Save collected alerts to CSV."""
        if not self.alerts:
            logger.error("No alerts to save. Run `.run()` first.")
            raise ValueError("No alert data to save.")

        output_path = output_path or get_config().PATHS.ALERTS.VALIDATION.IDENTITY
        header = [
            "id",
            "uid",
            "allow_clustering",
            "device_id",
            "normal_sessions_count",
            "repeated_anomaly_count",
            "anomaly_sessions",
            "reasons"
        ]
        
        data = [dict(zip(header, alert)) for alert in self.alerts]
        CsvRepository(output_path).save_all(data)
        
        logger.info(f"Identity alerts exported to CSV: {output_path}")
        return output_path
