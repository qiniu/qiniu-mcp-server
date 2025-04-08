
from .storage import loader as storage_loader
from .media_processing import loader as media_processing_loader
from ..config import config


def load():
    # 加载配置
    _conf = config.load_config()

    # 存储业务
    storage_loader.load(_conf)

    # dora
    media_processing_loader.load(_conf)