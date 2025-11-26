import logging

from mcp import types

from .live_streaming import LiveStreamingService
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_BUCKET_DESC = "LiveStreaming bucket name"
_STREAM_DESC = "LiveStreaming stream name"


class _ToolImpl:
    def __init__(self, live_streaming: LiveStreamingService):
        self.live_streaming = live_streaming

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_create_bucket",
            description="Create a new bucket in LiveStreaming using S3-style API. The bucket will be created at https://<bucket>.<endpoint_url>",
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
        result = await self.live_streaming.create_bucket(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_create_stream",
            description="Create a new stream in LiveStreaming using S3-style API. The stream will be created at https://<bucket>.<endpoint_url>/<stream>",
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
        result = await self.live_streaming.create_stream(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_bind_push_domain",
            description="Bind a push domain to a LiveStreaming bucket for live streaming. This allows you to configure the domain for pushing RTMP/WHIP streams.",
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
        result = await self.live_streaming.bind_push_domain(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_bind_play_domain",
            description="Bind a playback domain to a LiveStreaming bucket for live streaming. This allows you to configure the domain for playing back streams via FLV/M3U8/WHEP.",
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
        result = await self.live_streaming.bind_play_domain(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_get_push_urls",
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
        result = self.live_streaming.get_push_urls(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_get_play_urls",
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
        result = self.live_streaming.get_play_urls(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_query_live_traffic_stats",
            description="Query live streaming traffic statistics for a time range. Returns total traffic (bytes), average bandwidth (bps), peak bandwidth (bps), and optionally raw data for download.",
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
                    "include_raw_data": {
                        "type": "boolean",
                        "description": "If true, includes raw JSON data and detailed data points for download. Default is false.",
                        "default": False,
                    },
                },
                "required": ["begin", "end"],
            },
        )
    )
    async def query_live_traffic_stats(self, **kwargs) -> list[types.TextContent]:
        result = await self.live_streaming.query_live_traffic_stats(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_list_buckets",
            description="List all live streaming spaces/buckets. Returns information about all available live streaming buckets.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )
    )
    async def list_buckets(self, **kwargs) -> list[types.TextContent]:
        result = await self.live_streaming.list_buckets(**kwargs)
        return [types.TextContent(type="text", text=str(result))]

    @tools.tool_meta(
        types.Tool(
            name="live_streaming_list_streams",
            description="List all streams in a specific live streaming bucket. Returns the list of streams for the given bucket ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_id": {
                        "type": "string",
                        "description": "The bucket ID/name to list streams from",
                    },
                },
                "required": ["bucket_id"],
            },
        )
    )
    async def list_streams(self, **kwargs) -> list[types.TextContent]:
        result = await self.live_streaming.list_streams(**kwargs)
        return [types.TextContent(type="text", text=str(result))]


def register_tools(live_streaming: LiveStreamingService):
    tool_impl = _ToolImpl(live_streaming)
    tools.auto_register_tools(
        [
            tool_impl.create_bucket,
            tool_impl.create_stream,
            tool_impl.bind_push_domain,
            tool_impl.bind_play_domain,
            tool_impl.get_push_urls,
            tool_impl.get_play_urls,
            tool_impl.query_live_traffic_stats,
            tool_impl.list_buckets,
            tool_impl.list_streams,
        ]
    )
