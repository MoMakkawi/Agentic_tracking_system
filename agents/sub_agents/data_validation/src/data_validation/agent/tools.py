from smolagents import tool
from utils import logger, load_config
from data_validation.validators.device_session import DeviceValidator
from data_validation.validators.identity import IdentityValidator
from data_validation.validators.timestamp import TimestampValidator

# ---------------------------------------------------------
# Device Validation Tool
# ---------------------------------------------------------
@tool
def device_validation_tool() -> str:
    """
    Validate device sessions for anomalies such as:
        - Clock resets
        - Unusually long active periods
        - Missing or invalid device/session IDs

    Returns:
        str: Path to the generated CSV containing device-session alerts.
    """
    try:
        logger.info("Start device validation by Agent!")

        validator = DeviceValidator()
        validator.run()
        output_path = validator.save()

        logger.info("Device validation completed successfully saved by Agent!")
        return output_path

    except Exception as e:
        logger.error("Device validation tool error", exc_info=True)
        return f"Error in device validation: {e}"

# ---------------------------------------------------------
# Timestamp Validation Tool
# ---------------------------------------------------------
@tool
def timestamp_validation_tool() -> str:
    """
    Validate session timestamps for schedule compliance.

    Features checked:
        - University hours validation
        - Semester date range compliance
        - Weekend and holiday check-ins

    Returns:
        str: Path to the generated CSV file containing timestamp-related alerts.
    """
    try:
        logger.info("Start timestamp validation by Agent!")

        validator = TimestampValidator()
        validator.run()
        output_path = validator.save()

        logger.info("Timestamp validation completed successfully saved by Agent!")
        return output_path

    except Exception as e:
        logger.error("Timestamp validation tool error", exc_info=True)
        return f"Error in timestamp validation: {e}"

# ---------------------------------------------------------
# Identity Validation Tool
# ---------------------------------------------------------
@tool
def identity_validation_tool() -> str:
    """
    Validate user identity consistency across sessions and devices.

    Features checked:
        - Suspicious UID patterns (non-standard or malformed UIDs)
        - Redundant UIDs within the same session
        - Globally rare UIDs (appearing only once)
        - Repeated anomalies across multiple sessions

    Returns:
        str: Path to the generated CSV file containing identity-related alerts.
    """
    try:
        logger.info("Start identity validation by Agent!")

        validator = IdentityValidator()
        validator.run()
        output_path = validator.save()

        logger.info("Identity validation completed successfully saved by Agent!")
        return output_path

    except Exception as e:
        logger.error("Identity validation tool error", exc_info=True)
        return f"Error in identity validation: {e}"