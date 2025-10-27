import os
import pandas as pd
from smolagents import tool
from utils import *
from pipelines.source_connector import fetch_data
from pipelines.processor import Preprocessor
from pipelines.group_analyzer import GroupAnalyzer

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

        output_path = fetch_data()

        logger.info(f"Data fetched successfully and saved to {output_path}")
        return output_path

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

        p = Preprocessor()
        sessions = p.run()
        output_path = p.save()

        logger.info(f"Data preprocessed successfully and saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error("Preprocess tool error", exc_info=True)
        return f"Error in preprocessing: {e}"

# ---------------------------------------------------------
# Group Tool
# ---------------------------------------------------------
@tool
def group_tool() -> str:
    """
    Categorize or Aggregate or Classify students into groups Based on the preprocessed data.
    """
    try:
        logger.info("Start grouping data by Agent!")

        analyzer = GroupAnalyzer()
        analyzer.run()
        output_path = analyzer.save()

        logger.info(f"Grouping completed successfully. Results saved to: {output_path}")
        return output_path

    except Exception as e:
        logger.error("Group tool error", exc_info=True)
        return f"Error in grouping: {e}"