from smolagents import tool
from smolagents.agents import CodeAgent
from smolagents.models import OpenAIServerModel
from IPython.display import display, Markdown
from utils import logger, load_config, get_config, Secrets
from pipelines.source_connector import fetch_data
from pipelines.processor import Preprocessor
from pipelines.observer import Observer
from pipelines.group_analyzer import GroupAnalyzer
from gemini_model import GeminiModel 
from tools import *

load_config()

# ========================================
# 1. GEMINI MODEL WRAPPER USAGE
# ========================================

def ask_gemini(prompt: str):
    """
    Ask Gemini a question using the GeminiModel wrapper.
    Displays the markdown response for clarity.
    """
    try:
        gemini = GeminiModel(model_name=get_config().LLM_MODULES.DATA_PIPELINE.MODEL.NAME)
        logger.info(f"Asking Gemini with prompt: {prompt[:80]}...")
        answer = gemini.generate_text(prompt)

        display(Markdown(answer))
        return answer
    except Exception as e:
        logger.exception(f"Failed to query Gemini: {e}")
        return None


# ========================================
# 2. CREATE GEMINI MODEL FOR SMOLAGENT
# ========================================

def create_gemini_model():
    """
    Creates an OpenAIServerModel compatible with Gemini for smolagents.
    """
    try:
        if not Secrets.GOOGLE_API_KEY:
            raise ValueError("Missing GOOGLE_API_KEY. Please set it before running the agent.")

        logger.info("Creating Gemini model for smolagent.")
        return OpenAIServerModel(
            model_id=get_config().LLM_MODULES.DATA_PIPELINE.MODEL.NAME,
            api_base=get_config().LLM_MODULES.DATA_PIPELINE.MODEL.BASE_URL,
            api_key=Secrets.GOOGLE_API_KEY,
        )
    except Exception as e:
        logger.exception(f"Failed to create Gemini model for smolagent: {e}")
        raise


# ========================================
# 3. AGENT CREATION AND EXECUTION
# ========================================

def main():
    """
    Main entry point for executing the AI data pipeline agent.
    """
    try:
        model = create_gemini_model()

        agent = CodeAgent(
            tools=[fetch_tool, preprocess_tool, monitor_tool, group_tool],
            add_base_tools=False,
            model=model,
            instructions=(
                "You are an AI pipeline agent. Use the tools to fetch, preprocess, "
                "then monitor. If parameters are missing in user input, keep them None. "
                "Execute the sequence: Fetch → Grouping → Preprocess → Monitor."
            ),
        )

        task = "Fetch data, preprocess, classify the students also and then monitor anomalies, and save alerts."
        logger.info(f"Running task: {task}")

        result = agent.run(task)
        print("\n=== Result ===")
        print(result)

    except Exception as e:
        logger.exception(f"Pipeline execution failed: {e}")


if __name__ == "__main__":
    load_config()
    main()
