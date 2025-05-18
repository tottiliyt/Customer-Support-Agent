"""
Sierra Outfitters Customer Support Agent

This is the main entry point for the customer support agent application.
It integrates the conversation manager, data service, and AI service
to provide a complete customer support experience.
"""
import os
from pathlib import Path
import sys
from support_agent_server import SupportAgentServer
from dotenv import load_dotenv
from utils.logger import logger

if __name__ == "__main__":
    # Check for OpenAI API key
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OpenAI API key not found")
        print("\nError: The customer support agent encountered an error and needs to close.")
        sys.exit(1)


    # Initialize services
    project_root = Path(__file__).parent.parent
    support_agent_server = SupportAgentServer(openai_api_key, project_root)
    support_agent_server.start()