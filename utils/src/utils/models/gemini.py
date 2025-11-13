import os
from openai import OpenAI
from smolagents.models import OpenAIServerModel
from utils import logger, Secrets, get_config
from IPython.display import display, Markdown

class GeminiModel:
    """
    Wrapper class for interacting with Google's Gemini model through the OpenAI API.
    Provides unified text generation and smolagent compatibility.
    """

    def __init__(
        self,
        model_name: str = "gemini-1.5-pro-latest",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    ):
        self.model_name = model_name
        self.base_url = base_url
        try:
            api_key = Secrets.GOOGLE_API_KEY
            if not api_key:
                raise EnvironmentError("Missing GOOGLE_API_KEY")

            self.client = OpenAI(api_key=api_key)
            logger.info(f"GeminiModel initialized with model '{self.model_name}'")

        except Exception as e:
            logger.exception(f"Failed to initialize GeminiModel: {e}")
            raise

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
