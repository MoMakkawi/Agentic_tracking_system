import subprocess
import os
import sys
import time
from utils import logger, load_config

def run_parallel():
    load_config()
    logger.info("      AGENTIC TRACKING SYSTEM - DASHBOARD & API")
    
    # 1. Start the API
    logger.info("Starting API on http://localhost:8000...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    )

    # 2. Start the Dashboard
    logger.info("Starting Dashboard...")
    dashboard_path = os.path.join(os.getcwd(), "dashboard")
    
    # Check if node_modules exists
    if not os.path.exists(os.path.join(dashboard_path, "node_modules")):
        logger.warning("node_modules not found in dashboard. Attempting npm install...")
        subprocess.run(["npm", "install"], cwd=dashboard_path, shell=True)

    dashboard_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=dashboard_path,
        shell=True
    )

    logger.info("Both services are starting. Press Ctrl+C to stop both.")

    try:
        while True:
            # Check if processes are still running
            api_status = api_process.poll()
            dash_status = dashboard_process.poll()

            if api_status is not None:
                logger.error(f"API process exited with code {api_status}")
                break
            if dash_status is not None:
                logger.error(f"Dashboard process exited with code {dash_status}")
                break
            
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down services...")
        api_process.terminate()
        dashboard_process.terminate()
        logger.info("Cleanup complete.")

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
        
    run_parallel()
