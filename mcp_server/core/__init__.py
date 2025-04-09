from ..config import config
from .storage import load as load_storage
from .media_processing import load as load_media_processing
from .cdn import load as load_cdn


def load():
    # 加载配置
    cfg = config.load_config()

    # 存储业务
    load_storage(cfg)
    # CDN
    load_cdn(cfg)
    # 智能多媒体
    load_media_processing(cfg)
