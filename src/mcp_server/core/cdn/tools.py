from .cdn import CDNService
from ...consts import consts
from ...tools import tools
import logging
from mcp import types
from typing import Optional, List

logger = logging.getLogger(consts.LOGGER_NAME)


def _build_base_list(
    code: Optional[int],
    error: Optional[str],
    request_id: Optional[str],
) -> List[str]:
    rets = []
    if code:
        rets.append(f"Status Code: {code}")
    if error:
        rets.append(f"Message: {error}")
    if request_id:
        rets.append(f"RequestID: {request_id}")
    return rets


class _ToolImpl:
    def __init__(self, cdn: CDNService):
        self._cdn = cdn

    @tools.tool_meta(
        types.Tool(
            name="cdn_prefetch_urls",
            description="Newly added resources are proactively retrieved by the CDN and stored on its cache nodes in advance. Users simply submit the resource URLs, and the CDN automatically triggers the prefetch process.",
            inputSchema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "urls": {
                        "type": "array",
                        "description": "List of individual URLs to prefetch (max 60 items). Must be full URLs with protocol, e.g. 'http://example.com/file.zip'",
                        "items": {
                            "type": "string",
                            "format": "uri",
                            "pattern": "^https?://",
                            "examples": [
                                "https://cdn.example.com/images/photo.jpg",
                                "http://static.example.com/downloads/app.exe",
                            ],
                        },
                        "maxItems": 60,
                        "minItems": 1,
                    }
                },
                "required": ["urls"],
            },
        )
    )
    def prefetch_urls(self, **kwargs) -> list[types.TextContent]:
        ret = self._cdn.prefetch_urls(**kwargs)

        rets = _build_base_list(ret.code, ret.error, ret.requestId)
        if ret.invalidUrls:
            rets.append(f"Invalid URLs: {ret.invalidUrls}")
        if ret.code // 100 == 2:
            if ret.quotaDay is not None:
                rets.append(f"Today's prefetch quota: {ret.quotaDay}")
            if ret.surplusDay is not None:
                rets.append(f"Today's remaining quota: {ret.surplusDay}")

        return [
            types.TextContent(
                type="text",
                text="\n".join(rets),
            )
        ]

    @tools.tool_meta(
        types.Tool(
            name="cdn_refresh",
            description="This function marks resources cached on CDN nodes as expired. When users access these resources again, the CDN nodes will fetch the latest version from the origin server and store them anew.",
            inputSchema={
                "type": "object",
                "additionalProperties": False,  # 不允许出现未定义的属性
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "uri",
                            "pattern": "^https?://",  # 匹配http://或https://开头的URL
                            "examples": ["http://bar.foo.com/index.html"],
                        },
                        "maxItems": 60,
                        "description": "List of exact URLs to refresh (max 60 items). Must be full URLs with protocol, e.g. 'http://example.com/path/page.html'",
                    },
                    "dirs": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "pattern": "^https?://.*/(\\*|$)",  # 匹配以http://或https://开头的URL，并以/或者以/*结尾的字符串
                            "examples": [
                                "http://bar.foo.com/dir/",
                                "http://bar.foo.com/images/*",
                            ],
                        },
                        "maxItems": 10,
                        "description": "List of directory patterns to refresh (max 10 items). Must end with '/' or '/*' to indicate directory scope",
                    },
                }
            },
        )
    )
    def refresh(self, **kwargs) -> list[types.TextContent]:
        ret = self._cdn.refresh(**kwargs)
        rets = _build_base_list(ret.code, ret.error, ret.requestId)
        if ret.taskIds is not None:
            # 这个可能暂时用不到
            pass
        if ret.invalidUrls:
            rets.append(f"Invalid URLs list: {ret.invalidUrls}")
        if ret.invalidDirs:
            rets.append(f"Invalid dirs: {ret.invalidDirs}")

        if ret.code // 100 == 2:
            if ret.urlQuotaDay is not None:
                rets.append(f"Today's URL refresh quota: {ret.urlQuotaDay}")
            if ret.urlSurplusDay is not None:
                rets.append(f"Today's remaining URL refresh quota: {ret.urlSurplusDay}")
            if ret.dirQuotaDay is not None:
                rets.append(f"Today's directory refresh quota: {ret.dirQuotaDay}")
            if ret.dirSurplusDay is not None:
                rets.append(
                    f"Today's remaining directory refresh quota: {ret.dirSurplusDay}"
                )
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
