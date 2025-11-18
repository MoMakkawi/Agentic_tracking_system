from datetime import datetime
import pandas as pd

def safe_parse_timestamp(ts):
    """Safely parse timestamps in various formats and return a string
       formatted as 'YYYY-MM-DD HH:MM:SS', always in Europe/Paris time."""

    if not isinstance(ts, str):
        return None

    try:
        # Detect Zulu timestamps explicitly
        if ts.endswith("Z"):
            dt = pd.to_datetime(ts, utc=True)
        else:
            dt = pd.to_datetime(ts, errors="coerce", utc=False)

        if pd.isna(dt):
            return None

        # Convert tz-aware timestamps to Europe/Paris naive
        if getattr(dt, "tzinfo", None) is not None:
            dt = dt.tz_convert("Europe/Paris").tz_localize(None)

        # Drop microseconds
        dt = dt.replace(microsecond=0)

        # RETURN STRING (IMPORTANT FOR JSON)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return None
