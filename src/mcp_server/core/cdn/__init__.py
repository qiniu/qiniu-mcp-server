from .tools import register_tools
from ...config import config
from .cdn import CDNService


def load(cfg: config.Config):
    cdn = CDNService(cfg)
    register_tools(cdn)


__all__ = [
    "load",
]
