import logging
from dotenv import load_dotenv

# Load environment variables at package initialization
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.info("Initializing MCP server package")

from .server import main

__all__ = ['main']
