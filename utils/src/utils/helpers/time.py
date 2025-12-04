from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd

class TimestampHelper:
    """
    Helper class for timestamp manipulations, specifically tailored for
    handling various input formats and converting them to Europe/Paris time.
    """

    @staticmethod
    def safe_parse(ts: str) -> str | None:
        """
        Safely parse timestamps in various formats and return a string
        formatted as 'YYYY-MM-DD HH:MM:SS', always in Europe/Paris time.
        """
        dt = TimestampHelper.to_datetime(ts)
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def to_date(ts: str) -> str | None:
        """
        Safely parse timestamps and return the date string 'YYYY-MM-DD'.
        """
        dt = TimestampHelper.to_datetime(ts)
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def adjust_dst(ts: str) -> str | None:
        """
        Adjusts a timestamp for Daylight Saving Time (DST) based on 'Europe/Paris' timezone rules.
        If the timestamp, when interpreted in 'Europe/Paris', falls within the DST period, it is returned as is.
        If the timestamp falls outside the DST period, it is assumed to be a summer time recording on a winter date
        and is adjusted by subtracting one hour to align it with standard winter time.
        """
        try:
            dt = TimestampHelper.to_datetime(ts)
            if dt is None:
                return None

            # Re-localize to Paris to check DST status
            # dt is already naive Paris time from to_datetime
            dt_with_tz = dt.replace(tzinfo=ZoneInfo("Europe/Paris"))
            
            # Check if DST is active
            dst_offset = dt_with_tz.dst()
            is_dst = dst_offset is not None and dst_offset != timedelta(0)

            if is_dst:
                # Summer → keep summer timestamp untouched
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Winter → subtract one hour to convert the recorded
                # summer time to correct winter time
                winter_dt = dt - timedelta(hours=1)
                return winter_dt.strftime("%Y-%m-%d %H:%M:%S")

        except Exception:
            return None

    @staticmethod
    def to_datetime(ts: str) -> datetime | None:
        """
        Parse a timestamp string into a naive datetime object
        representing Europe/Paris time.
        """
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
            
            return dt.to_pydatetime()
        except Exception:
            return None

    @staticmethod
    def combine_date_time(date_str: str, time_str: str) -> datetime | None:
        """
        Combine date and time strings into a datetime object.
        """
        try:
            return datetime.fromisoformat(f"{date_str} {time_str}")
        except (ValueError, TypeError):
            return None

    @staticmethod
    def is_overlap(log_dt: datetime, start_str: str, end_str: str) -> bool:
        """
        Check if a log datetime overlaps with a time range defined by start and end strings.
        """
        if not start_str or not end_str:
            return False
        
        try:
            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            
            # Normalize to naive datetime for comparison if log_dt is naive
            if start_dt.tzinfo and not log_dt.tzinfo:
                start_dt = start_dt.replace(tzinfo=None)
                end_dt = end_dt.replace(tzinfo=None)
            
            return start_dt <= log_dt <= end_dt
        except (ValueError, TypeError):
            return False
