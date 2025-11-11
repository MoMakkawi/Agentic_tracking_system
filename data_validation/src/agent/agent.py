import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from smolagents.agents import CodeAgent
from utils import logger, load_config, get_config
from utils.models.gemini import GeminiModel
from tools import device_validation_tool, timestamp_validation_tool, identity_validation_tool

def main():
    try:
        # Initialize Gemini model
        gemini = GeminiModel(get_config().LLM_MODULES.DATA_VALIDATION.MODEL.NAME)
        model = gemini.to_smol_model()

        # Initialize the agent with validation tools
        agent = CodeAgent(
            tools=[
                device_validation_tool,
                timestamp_validation_tool,
                identity_validation_tool,
            ],
            add_base_tools=False,
            model=model,
            instructions=(
                "You are a data validation assistant agent. "
                "You have access to three tools: device_validation_tool, timestamp_validation_tool, "
                "and identity_validation_tool. Each tool checks different aspects of preprocessed session data. "
                "Use them to perform validation, detect anomalies, and produce CSV reports summarizing detected issues. "
                "Return clear paths to generated CSV files and summarize the main anomalies found. "
                "Do not hallucinate paths or results—run the actual tools."
            ),
        )

        # Example of a task (you can replace dynamically)
        task = (
            "Run all validation tools to check device, timestamp, and identity anomalies "
            "in the preprocessed session dataset, then summarize which type of anomalies were found."
        )

        logger.info(f"Running task: {task}")

        # Execute the agent’s task
        result = agent.run(task)

        print("\n=== Result ===")
        print(result)

    except Exception as e:
        logger.exception(f"Validation Pipeline execution failed: {e}")


if __name__ == "__main__":
    load_config()
    main()
