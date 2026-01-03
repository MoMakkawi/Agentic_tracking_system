"""
Custom exceptions for the API.

This module defines custom exception classes for better error handling
and more descriptive error messages throughout the application.
"""


class SessionNotFoundError(Exception):
    """Raised when session data cannot be found."""
    
    def __init__(self, message: str = "Session data not found"):
        self.message = message
        super().__init__(self.message)


class InvalidFilterError(Exception):
    """Raised when filter parameters are invalid."""
    
    def __init__(self, field: str, value: str, reason: str = ""):
        self.field = field
        self.value = value
        self.reason = reason
        self.message = f"Invalid filter for field '{field}' with value '{value}'"
        if reason:
            self.message += f": {reason}"
        super().__init__(self.message)


class InvalidSortFieldError(Exception):
    """Raised when sort field is not valid."""
    
    def __init__(self, field: str, valid_fields: list):
        self.field = field
        self.valid_fields = valid_fields
        self.message = f"Invalid sort field '{field}'. Must be one of: {', '.join(valid_fields)}"
        super().__init__(self.message)


class InvalidDateFormatError(Exception):
    """Raised when date format is invalid."""
    
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        self.message = f"Invalid date format for field '{field}': {value}"
        super().__init__(self.message)
