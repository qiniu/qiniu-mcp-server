
from .storage import loader as storage_loader
from ..config import config


def load():
    # 加载配置
    _conf = config.load_config()

    # 存储业务
    storage_loader.load(_conf)