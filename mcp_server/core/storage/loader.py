from .storage import Storage
from .tools import _register_tools
from .resource import _register_resource_provider
from ...config import config


def load(cfg: config.Config):
    storage = Storage(cfg)
    _register_tools(storage)
    _register_resource_provider(storage)

