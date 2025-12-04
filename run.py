def main():
    print("------------------------")
    print("Agentic Tracking System")
    print("------------------------")

    # Example imports (replace with your orchestration logic)
    from agents.orchestrator import orchestrator_main

    orchestrator_main()

if __name__ == "__main__":
    from openai import OpenAI
    from utils import Secrets

    client = OpenAI(
        base_url="https://ragarenn.eskemm-numerique.fr/sso/ch@t/api",
        api_key= Secrets.RENNES_API_KEY
    )

    # List available models from ragarenn
    try:
        models = client.models.list()
        print("Available models from ragarenn:")
        for model in models.data:
            print(model.id)
    except Exception as e:
        print(f"Error fetching models: {str(e)}")

    main()
