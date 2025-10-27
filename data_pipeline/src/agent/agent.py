from smolagents.agents import CodeAgent
from utils import logger, load_config, get_config
from utils.models.gemini import GeminiModel
from tools import fetch_tool, preprocess_tool, group_tool

def main():
    try:
        gemini = GeminiModel(get_config().LLM_MODULES.DATA_PIPELINE.MODEL.NAME)
        model = gemini.to_smol_model()

        agent = CodeAgent(
            tools=[fetch_tool, preprocess_tool, group_tool],
            add_base_tools=False,
            model=model,
            instructions=(
                "You are an AI pipeline agent. Use the tools to fetch, preprocess, "
                "Execute in sequence: Fetch → Preprocess → Grouping"
            ),
        )

        task = "Fetch data, preprocess, classify students."
        logger.info(f"Running task: {task}")

        result = agent.run(task)
        print("\n=== Result ===")
        print(result)

    except Exception as e:
        logger.exception(f"Pipeline execution failed: {e}")

if __name__ == "__main__":
    load_config()
    main()
