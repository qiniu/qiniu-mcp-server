import logging

from mcp import types

from .miku import MikuService
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_BUCKET_DESC = "Miku bucket name"
_STREAM_DESC = "Miku stream name"


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
            description="Bind a push domain to a Miku bucket for live streaming. This allows you to configure the domain for pushing RTMP/WHIP streams.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "domain": {
                        "type": "string",
                        "description": "The push domain name (e.g., mcp-push1.qiniu.com)",
                    },
                    "domain_type": {
                        "type": "string",
                        "description": "The type of push domain (default: pushRtmp)",
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
            description="Bind a playback domain to a Miku bucket for live streaming. This allows you to configure the domain for playing back streams via FLV/M3U8/WHEP.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "domain": {
                        "type": "string",
                        "description": "The playback domain name (e.g., mcp-play1.qiniu.com)",
                    },
                    "domain_type": {
                        "type": "string",
                        "description": "The type of playback domain (default: live)",
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
            description="Get push URLs for a stream. Returns RTMP and WHIP push URLs that can be used to push live streams.",
            inputSchema={
                "type": "object",
                "properties": {
                    "push_domain": {
                        "type": "string",
                        "description": "The push domain name",
                    },
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "stream_name": {
                        "type": "string",
                        "description": "The stream name",
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
            description="Get playback URLs for a stream. Returns FLV, M3U8, and WHEP playback URLs that can be used to play live streams.",
            inputSchema={
                "type": "object",
                "properties": {
                    "play_domain": {
                        "type": "string",
                        "description": "The playback domain name",
                    },
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "stream_name": {
                        "type": "string",
                        "description": "The stream name",
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
            name="miku_query_live_traffic_stats",
            description="Query live streaming traffic statistics for a time range. Returns bandwidth and traffic usage data.",
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
                },
                "required": ["begin", "end"],
            },
        )
    )
    async def query_live_traffic_stats(self, **kwargs) -> list[types.TextContent]:
        result = await self.miku.query_live_traffic_stats(**kwargs)
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
            tool_impl.query_live_traffic_stats,
        ]
    )
