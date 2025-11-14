import logging

from mcp import types

from .miku import MikuService
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_BUCKET_DESC = "Miku bucket name"
_STREAM_DESC = "Miku stream name"
_DOMAIN_DESC = "Domain name to bind"
_PUSH_DOMAIN_DESC = "Push domain name (e.g., mcp-push1.qiniu.com)"
_PLAY_DOMAIN_DESC = "Play domain name (e.g., mcp-play1.qiniu.com)"


class _ToolImpl:
    def __init__(self, miku: MikuService):
        self.miku = miku

    @tools.tool_meta(
        types.Tool(
            name="miku_create_bucket",
            description="Create a new bucket in Miku using S3-style API. The bucket will be created at https://<bucket>.<endpoint_url>",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                },
                "required": ["bucket"],
            },
        )
    )
    async def create_bucket(self, **kwargs) -> list[types.TextContent]:
        result = await self.miku.create_bucket(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="miku_create_stream",
            description="Create a new stream in Miku using S3-style API. The stream will be created at https://<bucket>.<endpoint_url>/<stream>",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "stream": {
                        "type": "string",
                        "description": _STREAM_DESC,
                    },
                },
                "required": ["bucket", "stream"],
            },
        )
    )
    async def create_stream(self, **kwargs) -> list[types.TextContent]:
        result = await self.miku.create_stream(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="miku_bind_push_domain",
            description="Bind a push domain for live streaming. This configures the domain for RTMP and WHIP push protocols.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "domain": {
                        "type": "string",
                        "description": _DOMAIN_DESC,
                    },
                    "domain_type": {
                        "type": "string",
                        "description": "Type of push domain (default: pushRtmp)",
                        "default": "pushRtmp",
                    },
                },
                "required": ["bucket", "domain"],
            },
        )
    )
    async def bind_push_domain(self, **kwargs) -> list[types.TextContent]:
        result = await self.miku.bind_push_domain(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="miku_bind_play_domain",
            description="Bind a play/playback domain for live streaming. This configures the domain for HLS, FLV, and WHEP playback protocols.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "domain": {
                        "type": "string",
                        "description": _DOMAIN_DESC,
                    },
                    "domain_type": {
                        "type": "string",
                        "description": "Type of play domain (default: live)",
                        "default": "live",
                    },
                },
                "required": ["bucket", "domain"],
            },
        )
    )
    async def bind_play_domain(self, **kwargs) -> list[types.TextContent]:
        result = await self.miku.bind_play_domain(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="miku_get_push_urls",
            description="Get push URLs for live streaming. Returns both RTMP and WHIP push URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "push_domain": {
                        "type": "string",
                        "description": _PUSH_DOMAIN_DESC,
                    },
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "stream_name": {
                        "type": "string",
                        "description": _STREAM_DESC,
                    },
                },
                "required": ["push_domain", "bucket", "stream_name"],
            },
        )
    )
    async def get_push_urls(self, **kwargs) -> list[types.TextContent]:
        result = self.miku.get_push_urls(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="miku_get_play_urls",
            description="Get playback URLs for live streaming. Returns FLV, M3U8 (HLS), and WHEP playback URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "play_domain": {
                        "type": "string",
                        "description": _PLAY_DOMAIN_DESC,
                    },
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "stream_name": {
                        "type": "string",
                        "description": _STREAM_DESC,
                    },
                },
                "required": ["play_domain", "bucket", "stream_name"],
            },
        )
    )
    async def get_play_urls(self, **kwargs) -> list[types.TextContent]:
        result = self.miku.get_play_urls(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="miku_query_traffic_stats",
            description="Query live streaming traffic statistics. Returns traffic usage data for a specified time range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "begin": {
                        "type": "string",
                        "description": "Start time in format YYYYMMDDHHMMSS (e.g., 20240101000000)",
                    },
                    "end": {
                        "type": "string",
                        "description": "End time in format YYYYMMDDHHMMSS (e.g., 20240129105148)",
                    },
                    "g": {
                        "type": "string",
                        "description": "Time granularity (default: 5min)",
                        "default": "5min",
                    },
                    "select": {
                        "type": "string",
                        "description": "Select parameter (default: flow)",
                        "default": "flow",
                    },
                    "flow": {
                        "type": "string",
                        "description": "Flow type (default: downflow)",
                        "default": "downflow",
                    },
                },
                "required": ["begin", "end"],
            },
        )
    )
    async def query_traffic_stats(self, **kwargs) -> list[types.TextContent]:
        result = await self.miku.query_traffic_stats(**kwargs)
        return [types.TextContent(type="text", text=str(result))]


def register_tools(miku: MikuService):
    tool_impl = _ToolImpl(miku)
    tools.auto_register_tools(
        [
            tool_impl.create_bucket,
            tool_impl.create_stream,
            tool_impl.bind_push_domain,
            tool_impl.bind_play_domain,
            tool_impl.get_push_urls,
            tool_impl.get_play_urls,
            tool_impl.query_traffic_stats,
        ]
    )
