from . import processing
from .tools import register_tools
from ...config import config


def load(cfg: config.Config):
    cli = processing.MediaProcessingService(cfg)
    register_tools(cli)


__all__ = [
    "load",
]
