import logging

from .consts import consts
from .server import main

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(consts.LOGGER_NAME)
logger.info("Initializing MCP server package")

__all__ = ["main"]
