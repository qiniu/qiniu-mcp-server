import logging
import asyncio

from qiniu import CdnManager, Auth
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
    invalidUrls: List[str] = None
    invalidDirs: List[str] = None
    urlQuotaDay: Optional[int] = None
    urlSurplusDay: Optional[int] = None
    dirQuotaDay: Optional[int] = None
    dirSurplusDay: Optional[int] = None


class CDNService:
    def __init__(self, cfg: config.Config):
        auth = Auth(access_key=cfg.access_key, secret_key=cfg.secret_key)
        self._cdn_manager = CdnManager(auth)

    def prefetch_urls(self, urls: List[str]) -> PrefetchUrlsResult:
        info, resp = self._cdn_manager.prefetch_urls(urls)
        if not resp.ok():
            return PrefetchUrlsResult.model_validate(resp.json())
        return PrefetchUrlsResult.model_validate(info)

    def refresh(self, urls: List[str], dirs: List[str]) -> RefreshResult:
        info, resp = self._cdn_manager.refresh_urls_and_dirs(urls, dirs)
        if not resp.ok():
            return RefreshResult.model_validate(resp.json())
        return RefreshResult.model_validate(info)


__all__ = [
    "PrefetchUrlsResult",
    "RefreshResult",
    "CDNService",
]
