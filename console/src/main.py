from utils import print_data, Config, logger
from data_pipeline import fetch_data

# Use config
data_url = Config.DATA_URL
save_path = Config.SAVE_PATH
print("AAAAAAAA -> ",data_url)
# Use logger
fetch_data();
print("SSSSSSSSSSSSSSSSSS")