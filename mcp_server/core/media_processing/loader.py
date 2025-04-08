from . import client
from .tools import register_tools
from ...config import config


def load(cfg: config.Config):
    cli = client.Client(cfg)
    register_tools(cli)
