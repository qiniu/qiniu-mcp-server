import logging
import os
from typing import List
from attr import dataclass
from dotenv import load_dotenv

from ..consts import consts

_CONFIG_ENV_KEY_ACCESS_KEY = "QINIU_ACCESS_KEY"
_CONFIG_ENV_KEY_SECRET_KEY = "QINIU_SECRET_KEY"
_CONFIG_ENV_KEY_ENDPOINT_URL = "QINIU_ENDPOINT_URL"
_CONFIG_ENV_KEY_REGION_NAME = "QINIU_REGION_NAME"
_CONFIG_ENV_KEY_BUCKETS = "QINIU_BUCKETS"

logger = logging.getLogger(consts.LOGGER_NAME)

# Load environment variables at package initialization
load_dotenv()


@dataclass
class Config:
    access_key: str
    secret_key: str
    endpoint_url: str
    region_name: str
    buckets: List[str]


def load_config() -> Config:
    config = Config(
        access_key=os.getenv(_CONFIG_ENV_KEY_ACCESS_KEY, ""),
        secret_key=os.getenv(_CONFIG_ENV_KEY_SECRET_KEY, ""),
        endpoint_url=os.getenv(_CONFIG_ENV_KEY_ENDPOINT_URL, ""),
        region_name=os.getenv(_CONFIG_ENV_KEY_REGION_NAME, ""),
        buckets=_get_configured_buckets_from_env(),
    )

    if not config.access_key:
        logger.error("QINIU_ACCESS_KEY is not configured")
        raise ValueError("QINIU_ACCESS_KEY is not configured")

    if not config.secret_key:
        logger.error("QINIU_SECRET_KEY is not configured")
        raise ValueError("QINIU_SECRET_KEY is not configured")

    if not config.endpoint_url:
        logger.error("QINIU_ENDPOINT_URL is not configured")
        raise ValueError("QINIU_ENDPOINT_URL is not configured")

    if not config.region_name:
        logger.error("QINIU_REGION_NAME is not configured")
        raise ValueError("QINIU_REGION_NAME is not configured")

    if not config.buckets:
        logger.error("QINIU_BUCKETS is not configured")
        raise ValueError("QINIU_BUCKETS is not configured")

    logger.info(f"Configured   access_key: {config.access_key}")
    logger.info(f"Configured endpoint_url: {config.endpoint_url}")
    logger.info(f"Configured  region_name: {config.region_name}")
    logger.info(f"Configured      buckets: {config.buckets}")
    return config


def _get_configured_buckets_from_env() -> List[str]:
    bucket_list = os.getenv(_CONFIG_ENV_KEY_BUCKETS)
    if bucket_list:
        buckets = [b.strip() for b in bucket_list.split(",")]
        return buckets
    else:
        return []
