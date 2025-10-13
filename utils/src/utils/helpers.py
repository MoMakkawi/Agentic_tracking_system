from datetime import datetime
import pandas as pd

def safe_parse_timestamp(ts):
    """Safely parse timestamps in various formats and normalize tz-aware ones to naive (local) datetimes."""
    if not isinstance(ts, str):
        return pd.NaT

    try:
        # Try pandas first (handles both tz-aware and naive)
        dt = pd.to_datetime(ts, errors="coerce", utc=False)
        if pd.isna(dt):
            return pd.NaT

        # If tz-aware (e.g. +02:00), convert to naive local time
        if getattr(dt, "tzinfo", None) is not None:
            dt = dt.tz_convert("Europe/Paris").tz_localize(None)

        return dt

    except Exception:
        return pd.NaT
