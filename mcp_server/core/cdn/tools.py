from .cdn import CDNService
from ...consts import consts
from ...tools import tools
import logging
from mcp import types
from typing import Optional, List

logger = logging.getLogger(consts.LOGGER_NAME)


def _buildBaseList(
    code: Optional[int],
    error: Optional[str],
    requestId: Optional[str],
) -> List[str]:
    rets = []
    if code is not None:
        rets.append(f"Error code: {code}")
    if error is not None:
        rets.append(f"Error message: {error}")
    if requestId is not None:
        rets.append(f"RequestID: {requestId}")


class _ToolImpl:
    def __init__(self, cdn: CDNService):
        self._cdn = cdn

    @tools.tool_meta(
        types.Tool(
            name="CDN_PrefetchUrls",
            description="文件预取，用户的新增资源提前由CDN拉取到CDN缓存节点上；用户直接提交资源的URL，CDN自动执行预取操作",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string", "format": "uri"},
                    }
                },
                "required": ["urls"],
            },
        )
    )
    def prefetch_urls(self, **kwargs) -> list[types.TextContent]:
        ret = self._cdn.prefetch_urls(**kwargs)

        rets = _buildBaseList(ret.code, ret.error, ret.requestId)
        if ret.invalidUrls is not None:
            rets.append(f"Invalid url list: {ret.invalidUrls}")
        if ret.quotaDay is not None:
            rets.append(f"每日的预取 url 限额: {ret.quotaDay}")
        if ret.surplusDay is not None:
            rets.append(f"每日的当前剩余的预取 url 限额: {ret.surplusDay}")

        return [
            types.TextContent(
                type="text",
                text="\n".join(rets),
            )
        ]

    @tools.tool_meta(
        types.Tool(
            name="CDN_Refresh",
            description="缓存刷新，用于将用户已经缓存在CDN节点上的资源设置为过期状态，当用于再次访问时CDN节点将回源拉取源站资源并重新缓存在CDN节点上。用户可以提交一个或多个具体的资源文件的URL，也可以提交一个或多个目录前缀的URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string", "format": "uri"},
                    },
                    "dirs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["urls", "dirs"],
            },
        )
    )
    def refresh(self, **kwargs) -> list[types.TextContent]:
        ret = self._cdn.refresh(**kwargs)
        rets = _buildBaseList(ret.code, ret.error, ret.requestId)
        if ret.taskIds is not None:
            pass
        if ret.invalidUrls is not None:
            rets.append(f"Invalid url list: {ret.invalidUrls}")
        if ret.invalidDirs is not None:
            rets.append(f"Invalid dir list: {ret.invalidDirs}")
        if ret.urlQuotaDay is not None:
            rets.append(f"每日的刷新url限额: {ret.urlQuotaDay}")
        if ret.urlSurplusDay is not None:
            rets.append(f"每日的当前剩余的刷新url限额: {ret.urlSurplusDay}")
        if ret.dirQuotaDay is not None:
            rets.append(f"每日的刷新dir限额: {ret.dirQuotaDay}")
        if ret.dirSurplusDay is not None:
            rets.append(f"每日的当前剩余的刷新dir限额: {ret.dirSurplusDay}")
        return [
            types.TextContent(
                type="text",
                text="\n".join(rets),
            )
        ]


def register_tools(cdn: CDNService):
    tool_impl = _ToolImpl(cdn)
    tools.auto_register_tools(
        [
            tool_impl.refresh,
            tool_impl.prefetch_urls,
        ]
    )
