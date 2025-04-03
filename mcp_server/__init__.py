import logging

from dotenv import load_dotenv

from .server import main

# Load environment variables at package initialization
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.info("Initializing MCP server package")

__all__ = ['main']
