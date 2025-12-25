"""Custom exceptions for code execution framework."""


class ValidationError(Exception):
    """Raised when code validation fails."""
    pass


class ExecutionError(Exception):
    """Raised when code execution fails."""
    pass