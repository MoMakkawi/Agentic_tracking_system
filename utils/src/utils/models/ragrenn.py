from openai import OpenAI
from smolagents.models import OpenAIServerModel
from utils import logger, Secrets

class RagrennModel:
    """
    Wrapper class for interacting with the Ragrenn (Rennes) model through its OpenAI-compatible API.
    Provides unified text generation and smolagent compatibility.
    """

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-Small-3.2-24B",
        base_url: str = "https://ragarenn.eskemm-numerique.fr/sso/ch@t/api"
    ):
        self.model_name = model_name
        self.base_url = base_url
        try:
            api_key = Secrets.RENNES_API_KEY
            if not api_key:
                raise EnvironmentError("Missing RENNES_API_KEY")

            self.client = OpenAI(api_key=api_key, base_url=self.base_url)
            logger.info(f"RagrennModel initialized with model '{self.model_name}'")

        except Exception as e:
            logger.exception(f"Failed to initialize RagrennModel: {e}")
            raise

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
        )
