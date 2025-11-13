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


def register_tools(miku: MikuService):
    tool_impl = _ToolImpl(miku)
    tools.auto_register_tools(
        [
            tool_impl.create_bucket,
            tool_impl.create_stream,
        ]
    )
