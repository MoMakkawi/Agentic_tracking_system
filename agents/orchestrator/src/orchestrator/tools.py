from data_pipeline import main as data_pipeline_agent_main
from data_validation import main as validation_main

pipeline_agent_tool = ToolCallingAgent(
    name="DataPipelineAgent",
    description=get_config().LLM_MODULES.DATA_PIPELINE.INSTRUCTIONS,
    agent_path=data_pipeline_agent_main
)

validation_agent_tool = ToolCallingAgent(
    name="ValidationAgent",
    description=get_config().LLM_MODULES.DATA_VALIDATION.INSTRUCTIONS,
    agent_path=validation_agent_main
)

