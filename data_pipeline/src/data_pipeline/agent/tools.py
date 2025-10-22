import os
import pandas as pd
from smolagents import tool
from utils import *
from data_pipeline.pipelines.source_connector import fetch_data
from data_pipeline.pipelines.processor import Preprocessor
from data_pipeline.pipelines.observer import Observer
from data_pipeline.pipelines.group_analyzer import GroupAnalyzer

# ---------------------------------------------------------
# Fetch Tool
# ---------------------------------------------------------
@tool
def fetch_tool() -> str:
    """
    Fetch attendance data from a source and save locally.
    """
    try:
        logger.info("Start fetching data by Agent!")
        fetch_data()
        path = get_config().FETCHED_DATA_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.info(f"Data fetched successfully and saved to {path}")
        return path
    except Exception as e:
        logger.error("Fetch tool error", exc_info=True)
        return f"Error in fetch: {e}"

# ---------------------------------------------------------
# Preprocess Tool
# ---------------------------------------------------------
@tool
def preprocess_tool() -> str:
    """
    Preprocess JSONL attendance data to produce cleaned output.
    """
    try:
        logger.info("Start preprocessing data by Agent!")
        pre = Preprocessor()
        pre.run_full_pipeline()
        path = get_config().PREPROCESSED_DATA_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.info(f"Data preprocessed successfully and saved to {path}")
        return path
    except Exception as e:
        logger.error("Preprocess tool error", exc_info=True)
        return f"Error in preprocessing: {e}"

# ---------------------------------------------------------
# Monitor Tool
# ---------------------------------------------------------
@tool
def monitor_tool() -> str:
    """
    Monitor preprocessed attendance data and save alerts.
    """
    try:
        logger.info("Start monitoring data by Agent!")
        df = pd.read_csv(get_config().PREPROCESSED_DATA_PATH)
        monitor = Observer(df)
        alerts = monitor.run()

        save_path = get_config().MONITORED_OUTPUT_PATH
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        monitor.save_alerts(alerts, path=save_path, file_format="csv")

        logger.info(f"Alerts saved successfully to {save_path}")
        return save_path
    except Exception as e:
        logger.error("Monitor tool error", exc_info=True)
        return f"Error in monitoring: {e}"

# ---------------------------------------------------------
# Group Tool
# ---------------------------------------------------------
@tool
def group_tool() -> str:
    """
    Group students into clusters.
    """
    try:
        # Load JSONL data
        data = load_jsonl(get_config().FETCHED_DATA_PATH)
        logger.info(f"Loaded {len(data)} records for grouping")

        # Run grouping
        analyzer = GroupAnalyzer()
        top_named_groups = analyzer.run(data)

        # Save grouped data
        output_path = get_config().GROUPS_OUTPUT_PATH
        analyzer.save(top_named_groups, output_path)
        logger.info(f"Grouping completed and saved to {output_path}")

        return output_path

    except Exception as e:
        logger.error("Group tool error", exc_info=True)
        return f"Error in grouping: {e}"

