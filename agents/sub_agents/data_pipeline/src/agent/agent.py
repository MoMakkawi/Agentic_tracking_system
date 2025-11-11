import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from smolagents.agents import CodeAgent
from utils import logger, load_config, get_config
from utils.models.gemini import GeminiModel
from tools import fetch_tool, preprocess_tool, group_tool


def main():
    try:
        # Initialize the Gemini LLM model
        gemini = GeminiModel(get_config().LLM_MODULES.DATA_PIPELINE.MODEL.NAME)
        model = gemini.to_smol_model()
        instructions = get_config().LLM_MODULES.DATA_PIPELINE.INSTRACTIONS

        # Initialize the Data Preprocessing Agent
        agent = CodeAgent(
            tools=[
                fetch_tool,
                preprocess_tool,
                group_tool,
            ],
            add_base_tools=False,
            model=model,
            instructions=instructions,
        )

        # Define the main task for the pipeline
        task = (
            "Fetch the raw dataset, perform preprocessing to clean and normalize it, "
            "then group students into clusters or behavior-based categories."
        )

        logger.info(f"Running task: {task}")

        # Execute the agent’s task
        result = agent.run(task)

        print("\n=== Result ===")
        print(result)

    except Exception as e:
        logger.exception(f"Data Preprocessing Pipeline execution failed: {e}")


if __name__ == "__main__":
    load_config()
    main()
