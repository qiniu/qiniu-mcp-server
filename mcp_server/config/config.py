import logging
import os
from typing import List

from mcp_server.consts import consts

logger = logging.getLogger(consts.get_logger_name())

class Config:
    def __init__(self,
                 access_key: str = None,
                 secret_key: str = None,
                 endpoint_url: str = None,
                 region_name: str = None,
                 buckets: List[str] = None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.buckets = buckets


def load_config() -> Config:
    config = Config()
    config.access_key = os.getenv(consts.ConfigEnvKeyAccessKey, '')
    config.secret_key = os.getenv(consts.ConfigEnvKeySecretKey, '')
    config.endpoint_url = os.getenv(consts.ConfigEnvKeyEndpointUrl, '')
    config.region_name = os.getenv(consts.ConfigEnvKeyRegionName, '')
    config.buckets = _get_configured_buckets_from_env()
    logger.info(f"Configured   access_key: {config.access_key}")
    logger.info(f"Configured endpoint_url: {config.endpoint_url}")
    logger.info(f"Configured  region_name: {config.region_name}")
    logger.info(f"Configured      buckets: {config.buckets}")
    return config


def _get_configured_buckets_from_env() -> List[str]:
    bucket_list = os.getenv(consts.ConfigEnvKeyBuckets)
    if bucket_list:
        buckets = [b.strip() for b in bucket_list.split(',')]
        return buckets
    else:
        return []
