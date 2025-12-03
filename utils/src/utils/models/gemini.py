import os
from openai import OpenAI
from smolagents.models import OpenAIServerModel
from utils import logger, Secrets
from IPython.display import display, Markdown
from typing import Union, List

class GeminiModel:
    """
    Wrapper class for interacting with Google's Gemini model through the OpenAI API.
    Provides unified text generation and smolagent compatibility.
    Supports automatic model selection from a list with fallback.
    """

    def __init__(
        self,
        model_name: Union[str, List[str]] = "gemini-1.5-pro-latest",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    ):
        self.base_url = base_url
        try:
            api_key = Secrets.GOOGLE_API_KEY
            if not api_key:
                raise EnvironmentError("Missing GOOGLE_API_KEY")

            self.client = OpenAI(api_key=api_key, base_url=self.base_url)
            
            # Select available model from the provided name(s)
            self.model_name = self._select_available_model(model_name)
            logger.info(f"GeminiModel initialized with model '{self.model_name}'")

        except Exception as e:
            logger.exception(f"Failed to initialize GeminiModel: {e}")
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
        """Send a text prompt to Gemini and return the response."""
        logger.debug(f"Sending prompt to Gemini: {prompt[:80]}...")
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=prompt
            )
            output = response.output_text.strip()
            logger.info("Gemini response received successfully.")
            return output

        except Exception as e:
            logger.exception(f"Gemini API call failed: {e}")
            raise RuntimeError("Gemini API call failed.") from e

    def ask(self, prompt: str, display_md: bool = False) -> str:
        """Ask Gemini a question and optionally display as Markdown."""
        answer = self.generate_text(prompt)
        if display_md:
            display(Markdown(answer))
        return answer

    def to_smol_model(self):
        """Convert to OpenAIServerModel for smolagents."""
        return OpenAIServerModel(
            model_id=self.model_name,
            api_base=self.base_url,
            api_key=Secrets.GOOGLE_API_KEY,
        )
