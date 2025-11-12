import sys
from pathlib import Path

# Get project root (go up 4 levels from tools.py)
project_root = Path(__file__).resolve().parents[4]

# Add sub_agents source paths
sys.path.insert(0, str(project_root / "agents" / "sub_agents" / "data_pipeline" / "src"))
sys.path.insert(0, str(project_root / "agents" / "sub_agents" / "data_validation" / "src"))
sys.path.insert(0, str(project_root / "utils" / "src"))



from smolagents.agents import CodeAgent, ToolCallingAgent
from utils.models.gemini import GeminiModel
from utils import logger, get_config, load_config
from tools import *

def main():
    load_config()
    gemini = GeminiModel(get_config().LLM_MODULES.ORCHESTRATOR.MODEL.NAME)
    model = gemini.to_smol_model()

    orchestrator = ToolCallingAgent(
        tools=[pipeline_agent_tool, validation_agent_tool],
        model=model,
        instructions=get_config().LLM_MODULES.ORCHESTRATOR.INSTRUCTIONS
    )

    task = "Run full data pipeline and validate the results."
    logger.info(f"Starting Orchestrator Task: {task}")

    result = orchestrator.run(task)

    print("\n=== Orchestrator Result ===")
    print(result)

if __name__ == "__main__":
    main()
