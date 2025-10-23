import os
from openai import OpenAI
from utils import logger, Secrets

class GeminiModel:
    """
    Wrapper class for interacting with Google's Gemini model through the OpenAI API.
    Handles text-based queries and responses using a unified interface.
    """

    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        """
        Initialize the GeminiModel with the specified model name.
        Automatically reads the API key from environment variables.

        Args:
            model_name (str): The Gemini model to use (default: 'gemini-1.5-pro-latest').
        """
        self.model_name = model_name

        try:
            api_key = Secrets.GOOGLE_API_KEY
            if not api_key:
                logger.error("Environment variable 'GOOGLE_API_KEY' not found.")
                raise EnvironmentError("Missing required environment variable: GOOGLE_API_KEY")

            self.client = OpenAI(api_key=api_key)
            logger.info(f"GeminiModel initialized with model '{self.model_name}'")

        except Exception as e:
            logger.exception(f"Failed to initialize GeminiModel: {e}")
            raise

    def generate_text(self, prompt: str) -> str:
        """
        Sends a prompt to the Gemini model and returns the generated text response.

        Args:
            prompt (str): Input text or question for the model.

        Returns:
            str: The model's generated response.
        """
        logger.debug(f"Sending prompt to Gemini: {prompt[:80]}...")  # log preview of prompt

        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=prompt
            )

            output = response.output_text.strip()
            logger.info(f"Gemini response received successfully.")
            logger.debug(f"Gemini response: {output[:120]}...")  # log preview of response

            return output

        except Exception as e:
            logger.exception(f"Gemini API call failed: {e}")
            raise RuntimeError("Gemini API call failed.") from e
