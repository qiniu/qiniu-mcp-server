from .miku import MikuService
from .tools import register_tools
from ...config import config


def load(cfg: config.Config):
    miku = MikuService(cfg)
    register_tools(miku)


__all__ = ["load"]
