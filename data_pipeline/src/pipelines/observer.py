import pandas as pd
import os
from utils import logger, get_config, load_config

# Load config at startup
load_config("config.json")

class Observer:
    """
    Monitors data to detect abnormal patterns such as clock resets,
    future timestamps, or inconsistent UID behavior.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the monitor with preprocessed data.

        Args:
            df (pd.DataFrame): Cleaned and preprocessed dataset.
        """
        self.df = df
        logger.info(f"Observer initialized with {len(df)} records")

    def run(self) -> pd.DataFrame:
        """
        Execute anomaly detection rules and generate alerts.

        Returns:
            pd.DataFrame: Records flagged with detected anomalies and reasons.
        """
        logger.info("Running anomaly detection on dataset")
        alerts = []

        for idx, row in self.df.iterrows():
            reasons = []

            if row.get("is_clock_reset"):
                reasons.append("Clock reset detected")
            if row.get("is_future_timestamp"):
                reasons.append("Future timestamp anomaly")
            if row.get("uid_length_anomaly"):
                reasons.append("UID length anomaly")
            if row.get("temporal_anomaly"):
                reasons.append("Temporal anomaly")

            if reasons:
                alert = {
                    "device_id": row.get("device_id"),
                    "uid": row.get("uid"),
                    "timestamp": row.get("timestamp"),
                    "reasons": reasons
                }
                alerts.append(alert)
                logger.debug(f"Alert generated for row {idx}: {alert}")

        alerts_df = pd.DataFrame(alerts)
        logger.info(f"Anomaly detection completed, {len(alerts_df)} alerts found")
        return alerts_df

    def save_alerts(
        self,
        alerts: pd.DataFrame,
        path: str = get_config().MONITORED_OUTPUT_PATH,
        file_format: str = "csv"
    ):
        """
        Save generated alerts to a file.

        Args:
            alerts (pd.DataFrame): Alerts dataframe to save
            path (str): Output path
            file_format (str): 'csv' or 'json'
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.info(f"Saving alerts to {path} as {file_format.upper()}")

        try:
            if file_format.lower() == "csv":
                alerts.to_csv(path, index=False)
            elif file_format.lower() == "json":
                alerts.to_json(path, orient="records", lines=True)
            else:
                logger.error(f"Unsupported file format: {file_format}")
                raise ValueError("file_format must be 'csv' or 'json'")

            logger.info(f"Alerts successfully saved to {path}")
        except Exception as e:
            logger.exception(f"Failed to save alerts: {e}")
            raise
