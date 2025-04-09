from .storage import StorageService
from .tools import register_tools
from .resource import register_resource_provider
from ...config import config


def load(cfg: config.Config):
    storage = StorageService(cfg)
    register_tools(storage)
    register_resource_provider(storage)


__all__ = ["load"]
