from ..config import config
from .storage import load as load_storage
from .media_processing import load as load_media_processing
from .cdn import load as load_cdn


def load():
    # 加载配置
    cfg = config.load_config()

    load_storage(cfg)  # 存储业务
    load_cdn(cfg)  # CDN
    load_media_processing(cfg)  # dora
