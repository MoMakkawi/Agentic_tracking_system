from utils import Config, logger
import json
from data_pipeline import fetch_data
from data_pipeline import Preprocessor

fetch_data();
print("----- End Fetching data -----")

preprocessor = Preprocessor()

df_clean, sessions, profiles, device_health = preprocessor.run_full_pipeline()

print("\n=== Sample User Profile ===")
if profiles:
    sample_uid = next(iter(profiles))
    print(json.dumps(profiles[sample_uid], indent=2, default=str))
else:
    logger.warning("No profiles generated — skipping profile display.")

print("\n=== Sample Device Health ===")
if device_health:
    sample_device = next(iter(device_health))
    print(json.dumps(device_health[sample_device], indent=2, default=str))
else:
    logger.warning("No device health records available — skipping device health display.")

print("----- End Preprocessor -----")