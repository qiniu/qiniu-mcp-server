from .storage import load as load_storage
from .media_processing import loader as media_processing_loader
from ..config import config
from .cdn import load as load_cdn


def load():
    # 加载配置
    cfg = config.load_config()

    # 存储业务
    load_storage(cfg)

    # CDN
    load_cdn(cfg)

    # dora
    media_processing_loader.load(cfg)
