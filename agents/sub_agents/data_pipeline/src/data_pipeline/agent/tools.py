from smolagents import tool
from utils import logger
from ..pipelines.processor import Preprocessor
from ..pipelines.group_analyzer import GroupAnalyzer
from ..pipelines.source_connector import DataFetcher

# ---------------------------------------------------------
# Fetch Tool
# ---------------------------------------------------------
@tool
def fetch_tool() -> str:
    """
    Download ICS + logs JSONL attendance data from the configured source and save it locally.

    Workflow:
        1. Instantiate DataFetcher.
        2. Fetch data from the URL.
        3. Store fetched data internally.
        4. Save data to disk using Files Helper Repositories.

    Returns: output paths for fetched data in this form
        dict: {
            "logs": "<path>", # logs saved in this file path
            "ics": "<path>"   # ics saved in this file path
        }    """
    try:
        logger.info("Start fetching data by Agent!")

        fetcher = DataFetcher()
        fetcher.run()
        output_paths = fetcher.save() 

        logger.info(f"Fetched successfully and saved as {output_paths}")
        return output_paths

    except Exception as e:
        logger.error("Fetch tool error", exc_info=True)
        return f"Error in fetch: {e}"


# ---------------------------------------------------------
# Preprocess Tool
# ---------------------------------------------------------
@tool
def preprocess_tool() -> str:
    """
    Preprocess raw JSONL attendance data into structured session objects.

    Workflow:
        1. Instantiate Preprocessor with path to raw JSONL.
        2. Remove redundant logs for each UID.
        3. Keep earliest timestamps for duplicate UIDs.
        4. Convert logs into structured session dictionaries.
        5. Track redundant UID counts per session.
        6. Save processed sessions to disk.

    Returns:
        str: Path to the saved preprocessed data file, or an error message if preprocessing fails.
    """
    try:
        logger.info("Start preprocessing data by Agent!")

        p = Preprocessor()
        p.run()
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
    Analyze preprocessed attendance sessions and generate student groupings.

    Workflow:
        1. Instantiate GroupAnalyzer with path to preprocessed sessions.
        2. Filter sessions by valid unique counts.
        3. Extract UID sets from filtered sessions.
        4. Count frequency of identical UID combinations.
        5. Assign readable group names based on group size and frequency.
        6. Save grouped results to disk.

    Returns:
        str: Path to the saved grouped data file, or an error message if grouping fails.
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
