import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os
from utils import logger, get_config, load_config
from utils.helpers import *

load_config()

class Preprocessor:
    """
    Complete preprocessing pipeline for attendance data.
    Steps:
      1. Flatten JSONL logs
      2. Detect temporal anomalies
      3. Detect fake badges
      4. Cluster logs into sessions
      5. Build user behavior profiles
      6. Assess device health
      7. Export clean ML-ready dataset
    """

    def __init__(self):
        self.jsonl_path = get_config().FETCHED_DATA_PATH
        if not self.jsonl_path or not os.path.exists(self.jsonl_path):
            logger.error(f"JSONL path not found or invalid: {self.jsonl_path}")
            raise FileNotFoundError(f"Input file not found: {self.jsonl_path}")

        self.raw_data = self._load_jsonl(self.jsonl_path)
        self.df = None
        self.session_df = None
        self.user_profiles = {}
        self.device_health = {}

        logger.info(f"Preprocessor initialized with file: {self.jsonl_path}")

    # -------------------------------------------------------------------------
    def _load_jsonl(self, path: str) -> list:
        """Load JSONL file into list of dicts."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = [json.loads(line.strip()) for line in f if line.strip()]
            logger.info(f"Loaded {len(data)} records from {path}")
            return data
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load JSONL file {path}: {e}")
            raise

    # -------------------------------------------------------------------------
    def flatten_logs(self) -> pd.DataFrame:
        """Flatten nested log structure into a tabular DataFrame."""
        logger.info("Flattening nested attendance logs...")
        flattened = []

        for record in self.raw_data:
            device_id = record.get("device_id")
            count = record.get("count", 0)
            logs = record.get("logs", [])

            if not logs:
                logger.warning(f"No logs found for device {device_id}")
                continue

            for log in logs:
                flattened.append({
                    "device_id": device_id,
                    "uid": log.get("uid"),
                    "timestamp": log.get("ts"),
                    "batch_count": count
                })

        df = pd.DataFrame(flattened)
        if df.empty:
            logger.warning("Flattened DataFrame is empty — check input data format.")

        df["timestamp"] = df["timestamp"].apply(safe_parse_timestamp)

        df = df.sort_values("timestamp").reset_index(drop=True)
        self.df = df
        logger.info(f"Flattened {len(df)} total log entries.")
        return df

    # -------------------------------------------------------------------------
    def detect_temporal_anomalies(self) -> pd.DataFrame:
        """Identify invalid timestamps and clock resets."""
        logger.info("Detecting temporal anomalies...")
        current_time = datetime.now()

        self.df["is_clock_reset"] = self.df["timestamp"].dt.year == 2000
        self.df["is_future_timestamp"] = self.df["timestamp"] > current_time
        self.df["has_timezone"] = self.df["timestamp"].apply(
            lambda x: x.tzinfo is not None if pd.notna(x) else False
        )
        self.df["temporal_anomaly"] = (
            self.df["is_clock_reset"] | self.df["is_future_timestamp"]
        )

        anomaly_count = int(self.df["temporal_anomaly"].sum())
        logger.info(f"Detected {anomaly_count} temporal anomalies.")
        return self.df

    # -------------------------------------------------------------------------
    def detect_fake_badges(self) -> pd.DataFrame:
        """Identify suspicious or duplicated badge usage."""
        logger.info("Detecting fake badge patterns...")
        suspicious_patterns = ["0", "A1B2C3D4", "11223344", "fake"]

        self.df["uid_suspicious_pattern"] = self.df["uid"].isin(suspicious_patterns)
        self.df["uid_length"] = self.df["uid"].astype(str).str.len()
        median_length = self.df["uid_length"].median()

        self.df["uid_length_anomaly"] = np.abs(
            self.df["uid_length"] - median_length
        ) > 2

        self.df["multi_device_flag"] = False
        for uid in self.df["uid"].unique():
            uid_logs = self.df[self.df["uid"] == uid].copy()
            if len(uid_logs) > 1:
                uid_logs = uid_logs.sort_values("timestamp")
                time_diffs = uid_logs["timestamp"].diff()
                device_changes = uid_logs["device_id"] != uid_logs["device_id"].shift()
                suspicious = (time_diffs < timedelta(minutes=1)) & device_changes
                self.df.loc[uid_logs[suspicious].index, "multi_device_flag"] = True

        self.df["fake_badge_score"] = (
            self.df["uid_suspicious_pattern"].astype(int)
            + self.df["uid_length_anomaly"].astype(int)
            + self.df["multi_device_flag"].astype(int)
        )

        fake_count = int((self.df["fake_badge_score"] > 0).sum())
        logger.info(f"Detected {fake_count} potentially fake badges.")
        return self.df

    # -------------------------------------------------------------------------
    def cluster_sessions(self, gap_threshold_minutes: int = 5) -> pd.DataFrame:
        """Group rapid scans into attendance sessions."""
        logger.info("Clustering attendance sessions...")
        self.df["session_id"] = None
        session_counter = 0

        for (uid, device), group in self.df.groupby(["uid", "device_id"]):
            group = group.sort_values("timestamp")
            if len(group) == 0:
                continue

            current_session = session_counter
            prev_time = group.iloc[0]["timestamp"]

            for idx, row in group.iterrows():
                time_diff = (row["timestamp"] - prev_time).total_seconds() / 60
                if time_diff > gap_threshold_minutes:
                    session_counter += 1
                    current_session = session_counter
                self.df.at[idx, "session_id"] = current_session
                prev_time = row["timestamp"]
            session_counter += 1

        session_summary = (
            self.df.groupby("session_id")
            .agg({
                "timestamp": ["min", "max", "count"],
                "uid": "first",
                "device_id": "first",
                "fake_badge_score": "max",
                "temporal_anomaly": "any"
            })
            .reset_index()
        )

        session_summary.columns = [
            "session_id", "session_start", "session_end", "scan_count",
            "uid", "device_id", "max_fake_score", "has_temporal_anomaly"
        ]
        session_summary["session_duration_sec"] = (
            session_summary["session_end"] - session_summary["session_start"]
        ).dt.total_seconds()

        self.session_df = session_summary
        logger.info(f"Generated {len(session_summary)} session records.")
        return session_summary

    # -------------------------------------------------------------------------
    def build_user_profiles(self) -> dict:
        """Create behavior profiles per user based on session stats."""
        logger.info("Building user profiles...")

        if self.session_df is None or self.session_df.empty:
            logger.warning("No session data available for profile building.")
            return {}

        profiles = {}
        for uid, group in self.session_df.groupby("uid"):
            profiles[uid] = {
                "total_sessions": len(group),
                "avg_session_duration_sec": group["session_duration_sec"].mean(),
                "avg_scans_per_session": group["scan_count"].mean(),
                "devices_used": group["device_id"].nunique(),
                "has_temporal_anomaly": bool(group["has_temporal_anomaly"].any()),
            }

        self.user_profiles = profiles
        logger.info(f"Generated {len(profiles)} user profiles.")
        return profiles

    # -------------------------------------------------------------------------
    def assess_device_health(self) -> dict:
        """Evaluate device reliability and consistency."""
        logger.info("Assessing device health...")

        if self.df is None or self.df.empty:
            logger.warning("No data available for device health assessment.")
            return {}

        health_summary = (
            self.df.groupby("device_id")
            .agg({
                "temporal_anomaly": "sum",
                "fake_badge_score": "sum",
                "uid": "count"
            })
            .rename(columns={
                "temporal_anomaly": "anomaly_count",
                "fake_badge_score": "fake_badge_total",
                "uid": "total_logs"
            })
        )

        health_summary["anomaly_rate"] = (
            health_summary["anomaly_count"] / health_summary["total_logs"]
        ).round(3)
        health_summary["fake_badge_rate"] = (
            health_summary["fake_badge_total"] / health_summary["total_logs"]
        ).round(3)

        self.device_health = health_summary.to_dict(orient="index")
        logger.info(f"Device health computed for {len(self.device_health)} devices.")
        return self.device_health

    # -------------------------------------------------------------------------
    def export_clean_data(self, output_path: str = None):
        """Export cleaned data to CSV."""
        clean_data_path = output_path or get_config().PREPROCESSED_DATA_PATH
        try:
            os.makedirs(os.path.dirname(clean_data_path), exist_ok=True)
            self.df.to_csv(clean_data_path, index=False)
            logger.info(f"Clean data exported successfully to {clean_data_path}")
        except OSError as e:
            logger.error(f"Failed to export clean data to {clean_data_path}: {e}")
            raise

    # -------------------------------------------------------------------------
    def generate_summary_report(self) -> dict:
        """Generate a summary report."""
        try:
            report = {
                "total_records": len(self.df),
                "unique_uids": self.df["uid"].nunique(),
                "unique_sessions": len(self.session_df) if self.session_df is not None else 0,
                "devices_analyzed": len(self.device_health),
            }
            logger.info("Summary report generated successfully.")
            return report
        except Exception as e:
            logger.error(f"Failed to generate summary report: {e}")
            raise

    # -------------------------------------------------------------------------
    def run_full_pipeline(self) -> tuple:
        """Execute the full preprocessing workflow."""
        logger.info("Starting full preprocessing pipeline...")

        self.flatten_logs()
        self.detect_temporal_anomalies()
        self.detect_fake_badges()
        self.cluster_sessions()
        self.build_user_profiles()
        self.assess_device_health()
        self.export_clean_data()

        summary = self.generate_summary_report()
        logger.info("Preprocessing pipeline completed successfully.")
        logger.info(f"Summary: {summary}")

        return self.df, self.session_df, self.user_profiles, self.device_health
