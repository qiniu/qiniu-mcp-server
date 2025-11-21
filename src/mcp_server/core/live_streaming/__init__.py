from .live_streaming import  LiveStreamingService
from .tools import register_tools
from ...config import config


def load(cfg: config.Config):
    live = LiveStreamingService(cfg)
    register_tools(live)


__all__ = ["load"]
