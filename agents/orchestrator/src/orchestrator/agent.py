# orchestrator_agent.py
from smolagents.agents import CodeAgent, ToolCallingAgent
from tools import *
from utils.models.gemini import GeminiModel
from utils import get_config, load_config
from utils import logger

def main():
    try:
        load_config()
        # Load LLM model
        gemini = GeminiModel(get_config().LLM_MODULES.ORCHESTRATOR.MODEL.NAME)
        model = gemini.to_smol_model()

        # Master Orchestrator
        orchestrator = CodeAgent(
            tools=[
                pipeline_agent_tool, validation_agent_tool
            ],
            add_base_tools=False,
            model=model,
            instructions=(
                "You are the Master Orchestrator Agent. Your task is to orchestrate sub-agents. "
                "Use PipelineAgent to fetch, preprocess, and group data. "
                "Then use ValidationAgent to validate the data. "
                "Summarize the outputs of each sub-agent and avoid hallucinating results."
            ),
        )

        task = "Run full data pipeline and validate the results."
        logger.info(f"Orchestrator task: {task}")
        result = orchestrator.run(task)

        print("\n=== Orchestrator Result ===")
        print(result)

    except Exception as e:
        logger.exception(f"Orchestrator execution failed: {e}")

if __name__ == "__main__":
    main()
