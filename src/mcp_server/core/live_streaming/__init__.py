from .live_streaming import  LiveStreamingService
from .tools import register_tools
from ...config import config


def load(cfg: config.Config):
    miku = LiveStreamingService(cfg)
    register_tools(miku)


__all__ = ["load"]
