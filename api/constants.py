"""
Constants for API configuration and validation.

This module contains all constant values used across the API to avoid
magic numbers and strings scattered throughout the codebase.
"""

# Sortable fields for session queries
SORTABLE_FIELDS = [
    "session_id",
    "device_id",
    "received_at",
    "logs_date",
    "recorded_count",
    "unique_count",
    "alert_count"
]

# Pagination defaults
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 1000

# Sort directions
SORT_ASC = "asc"
SORT_DESC = "desc"
VALID_SORT_DIRECTIONS = [SORT_ASC, SORT_DESC]

# Date format for logs
LOGS_DATE_FORMAT = "YYYY-MM-DD"

# Sortable fields for alert queries
DEVICE_ALERT_SORTABLE_FIELDS = ["id", "session_id", "device_id"]
IDENTITY_ALERT_SORTABLE_FIELDS = ["id", "uid", "device_id", "normal_sessions_count", "repeated_anomaly_count"]
TIMESTAMP_ALERT_SORTABLE_FIELDS = ["id", "uid", "session_id", "device_id", "timestamp"]
GROUP_SORTABLE_FIELDS = ["name", "member_count"]

# Error messages
ERROR_INVALID_SORT_FIELD = "Invalid order_by field. Must be one of: {fields}"
ERROR_INVALID_PAGE = "Page {page} does not exist. Total pages: {total_pages}"
ERROR_INVALID_DATE_FORMAT = "Invalid {field} format: {value}"
ERROR_READING_SESSIONS = "Error reading sessions: {error}"
ERROR_FILTERING_SESSIONS = "Error filtering sessions: {error}"
ERROR_READING_ALERTS = "Error reading alerts: {error}"
ERROR_FILTERING_ALERTS = "Error filtering alerts: {error}"
ERROR_READING_GROUPS = "Error reading groups: {error}"
ERROR_FILTERING_GROUPS = "Error filtering groups: {error}"
