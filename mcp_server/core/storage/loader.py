from .storage import Storage
from .tools import register_tools
from .resource import register_resource_provider
from ...config import config


def load(cfg: config.Config):
    storage = Storage(cfg)
    register_tools(storage)
    register_resource_provider(storage)

