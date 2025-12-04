from openai import OpenAI
from smolagents.models import OpenAIServerModel
from utils import logger, Secrets
from typing import Union, List

class RagrennModel:
    """
    Wrapper class for interacting with the Ragrenn (Rennes) model through its OpenAI-compatible API.
    Provides unified text generation and smolagent compatibility.
    Supports automatic model selection from a list with fallback.
    """

    def __init__(self, model_config):
        self.base_url = model_config.MODEL.BASE_URL
        target_model_name = model_config.MODEL.NAME

        try:
            api_key = Secrets.RENNES_API_KEY
            if not api_key:
                raise EnvironmentError("Missing RENNES_API_KEY")

            self.client = OpenAI(api_key=api_key, base_url=self.base_url)
            
            # Select available model from the provided name(s)
            self.model_name = self._select_available_model(target_model_name)
            logger.info(f"RagrennModel initialized with model '{self.model_name}'")

        except Exception as e:
            logger.exception(f"Failed to initialize RagrennModel: {e}")
            raise

    def _select_available_model(self, model_name: Union[str, List[str]]) -> str:
        """
        Select the first available model from the provided name(s).
        
        Args:
            model_name: Single model name or list of model names to try
            
        Returns:
            The first available model name
            
        Raises:
            RuntimeError: If no models are available
        """
        # Convert single string to list for uniform processing
        model_names = [model_name] if isinstance(model_name, str) else model_name
        
        try:
            # Fetch available models from the API
            available_models_response = self.client.models.list()
            available_model_ids = {model.id for model in available_models_response.data}
            
            logger.debug(f"Available models from API: {available_model_ids}")
            logger.debug(f"Requested models: {model_names}")
            
            # Find the first available model
            for model in model_names:
                if model in available_model_ids:
                    logger.info(f"Selected model: {model}")
                    return model
            
            # No models available
            raise RuntimeError(
                f"None of the requested models are available. "
                f"Requested: {model_names}, Available: {available_model_ids}"
            )
            
        except Exception as e:
            logger.warning(f"Failed to fetch available models: {e}. Using first model from list.")
            # Fallback: use the first model in the list if API check fails
            return model_names[0]

    def generate_text(self, prompt: str) -> str:
        """Send a text prompt to Ragrenn and return the response."""
        logger.debug(f"Sending prompt to Ragrenn: {prompt[:80]}...")
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=prompt
            )
            output = response.output_text.strip()
            logger.info("Ragrenn response received successfully.")
            return output

        except Exception as e:
            logger.exception(f"Ragrenn API call failed: {e}")
            raise RuntimeError("Ragrenn API call failed.") from e

    def ask(self, prompt: str, display_md: bool = False) -> str:
        """Ask Ragrenn a question and optionally display as Markdown."""
        from IPython.display import Markdown, display
        answer = self.generate_text(prompt)
        if display_md:
            display(Markdown(answer))
        return answer

    def to_smol_model(self):
        """Convert to OpenAIServerModel for smolagents."""
        return OpenAIServerModel(
            model_id=self.model_name,
            api_base=self.base_url,
            api_key=Secrets.RENNES_API_KEY,
            flatten_messages_as_text=True,
        )
