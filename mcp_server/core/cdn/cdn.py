import logging

from qiniu import CdnManager, Auth
from qiniu.http import ResponseInfo
from typing import List, Optional, Dict
from pydantic import BaseModel
from dataclasses import dataclass

from ...consts import consts
from ...config import config

logger = logging.getLogger(consts.LOGGER_NAME)


@dataclass
class PrefetchUrlsResult(BaseModel):
    code: Optional[int] = None
    error: Optional[str] = None
    requestId: Optional[str] = None
    invalidUrls: Optional[List[str]] = None
    quotaDay: Optional[int] = None
    surplusDay: Optional[int] = None


@dataclass
class RefreshResult(BaseModel):
    code: Optional[int] = None
    error: Optional[str] = None
    requestId: Optional[str] = None
    taskIds: Optional[Dict[str, str]] = None
    invalidUrls: Optional[List[str]] = None
    invalidDirs: Optional[List[str]] = None
    urlQuotaDay: Optional[int] = None
    urlSurplusDay: Optional[int] = None
    dirQuotaDay: Optional[int] = None
    dirSurplusDay: Optional[int] = None


def _raise_if_resp_error(resp: ResponseInfo):
    if resp.ok():
        return
    raise RuntimeError(f"qiniu response error: {str(resp)}")


class CDNService:
    def __init__(self, cfg: config.Config):
        auth = Auth(access_key=cfg.access_key, secret_key=cfg.secret_key)
        self._cdn_manager = CdnManager(auth)

    def prefetch_urls(self, urls: List[str] = []) -> PrefetchUrlsResult:
        if not urls:
            raise ValueError("urls is empty")
        info, resp = self._cdn_manager.prefetch_urls(urls)
        _raise_if_resp_error(resp)
        return PrefetchUrlsResult.model_validate(info)

    def refresh(self, urls: List[str] = [], dirs: List[str] = []) -> RefreshResult:
        if not urls and not dirs:
            raise ValueError("urls and dirs cannot be empty")
        info, resp = self._cdn_manager.refresh_urls_and_dirs(urls, dirs)
        _raise_if_resp_error(resp)
        return RefreshResult.model_validate(info)


__all__ = [
    "PrefetchUrlsResult",
    "RefreshResult",
    "CDNService",
]
