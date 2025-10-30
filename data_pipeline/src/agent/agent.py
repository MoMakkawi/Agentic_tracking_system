from smolagents.agents import CodeAgent
from utils import logger, load_config, get_config
from utils.models.gemini import GeminiModel
from tools import fetch_tool, preprocess_tool, group_tool


def main():
    try:
        # Initialize the Gemini LLM model
        gemini = GeminiModel(get_config().LLM_MODULES.DATA_PIPELINE.MODEL.NAME)
        model = gemini.to_smol_model()

        # Initialize the Data Preprocessing Agent
        agent = CodeAgent(
            tools=[
                fetch_tool,
                preprocess_tool,
                group_tool,
            ],
            add_base_tools=False,
            model=model,
            instructions=(
                "You are a **Data Preprocessing Assistant Agent**. "
                "Your role is to orchestrate the early stages of the data pipeline. "
                "You have access to three specialized tools: "
                "1. **fetch_tool** – retrieves raw session or activity data from the configured data sources. "
                "2. **preprocess_tool** – cleans, formats, and standardizes the raw data to ensure structural and temporal consistency. "
                "3. **group_tool** – analyzes preprocessed data to cluster or classify students into meaningful groups Based on matching the number of attendees in the most frequent sessions with the appropriate group whose attendance is specified in the configuration."
                "Execute the tools sequentially in the following order: **Fetch → Preprocess → Grouping**. "
                "After execution, summarize the main results — including data shape, groups formed, and any key insights from preprocessing. "
                "Avoid hallucinating file paths or results; rely solely on the actual outputs from the tools."
                "Stop from the first error if there any error in one of those steps"
            ),
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
