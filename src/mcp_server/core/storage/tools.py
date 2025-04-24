import logging
import base64

from mcp import types
from mcp.types import ImageContent, TextContent

from .storage import StorageService
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_BUCKET_DESC = "Qiniu Cloud Storage bucket Name"

class _ToolImpl:
    def __init__(self, storage: StorageService):
        self.storage = storage

    @tools.tool_meta(
        types.Tool(
            name="ListBuckets",
            description="Return the Bucket you configured based on the conditions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prefix": {
                        "type": "string",
                        "description": "Bucket prefix. The listed Buckets will be filtered based on this prefix, and only those matching the prefix will be output.",
                    },
                },
                "required": [],
            },
        )
    )
    async def list_buckets(self, **kwargs) -> list[types.TextContent]:
        buckets = await self.storage.list_buckets(**kwargs)
        return [types.TextContent(type="text", text=str(buckets))]

    @tools.tool_meta(
        types.Tool(
            name="ListObjects",
            description="List objects in Qiniu Cloud, list a part each time, you can set start_after to continue listing, when the number of listed objects is less than max_keys, it means that all files are listed. start_after can be the key of the last file in the previous listing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "max_keys": {
                        "type": "integer",
                        "description": "Sets the max number of keys returned, default: 20",
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Specify the prefix of the operation response key. Only keys that meet this prefix will be listed.",
                    },
                    "start_after": {
                        "type": "string",
                        "description": "start_after is where you want Qiniu Cloud to start listing from. Qiniu Cloud starts listing after this specified key. start_after can be any key in the bucket.",
                    },
                },
                "required": ["bucket"],
            },
        )
    )
    async def list_objects(self, **kwargs) -> list[types.TextContent]:
        objects = await self.storage.list_objects(**kwargs)
        return [types.TextContent(type="text", text=str(objects))]

    @tools.tool_meta(
        types.Tool(
            name="GetObject",
            description="Get an object contents from Qiniu Cloud bucket. In the GetObject request, specify the full key name for the object.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "key": {
                        "type": "string",
                        "description": "Key of the object to get.",
                    },
                },
                "required": ["bucket", "key"],
            },
        )
    )
    async def get_object(self, **kwargs) -> list[ImageContent] | list[TextContent]:
        response = await self.storage.get_object(**kwargs)
        file_content = response["Body"]
        content_type = response.get("ContentType", "application/octet-stream")

        # 根据内容类型返回不同的响应
        if content_type.startswith("image/"):
            base64_data = base64.b64encode(file_content).decode("utf-8")
            return [
                types.ImageContent(
                    type="image", data=base64_data, mimeType=content_type
                )
            ]

        if isinstance(file_content, bytes):
            text_content = file_content.decode("utf-8")
        else:
            text_content = str(file_content)
        return [types.TextContent(type="text", text=text_content)]

    @tools.tool_meta(
        types.Tool(
            name="UploadTextData",
            description="Upload text data to Qiniu bucket.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "key": {
                        "type": "string",
                        "description": "Key of the object to upload. Length Constraints: Minimum length of 1.",
                    },
                    "data": {
                        "type": "string",
                        "description": "The data to upload.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite the existing object if it already exists.",
                    },
                },
                "required": ["bucket", "key", "data"],
            }
        )
    )
    def upload_text_data(self, **kwargs) -> list[types.TextContent]:
        urls = self.storage.upload_text_data(**kwargs)
        return [types.TextContent(type="text", text=str(urls))]

    @tools.tool_meta(
        types.Tool(
            name="UploadFile",
            description="Upload a local file to Qiniu bucket.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "key": {
                        "type": "string",
                        "description": "Key of the object to upload. Length Constraints: Minimum length of 1.",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "The file path of file to upload.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite the existing object if it already exists.",
                    },
                },
                "required": ["bucket", "key", "file_path"],
            }
        )
    )
    def upload_file(self, **kwargs) -> list[types.TextContent]:
        urls = self.storage.upload_file(**kwargs)
        return [types.TextContent(type="text", text=str(urls))]

    @tools.tool_meta(
        types.Tool(
            name="FetchObject",
            description="Fetch a http object to Qiniu bucket.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "key": {
                        "type": "string",
                    }
                }
            }
        )
    )
    def fetch_object(self, **kwargs) -> list[types.TextContent]:
        urls = self.storage.fetch_object(**kwargs)
        return [types.TextContent(type="text", text=str(urls))]

    @tools.tool_meta(
        types.Tool(
            name="GetObjectURL",
            description="Get the file download URL, and note that the Bucket where the file is located must be bound to a domain name. If using Qiniu Cloud test domain, HTTPS access will not be available, and users need to make adjustments for this themselves.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "key": {
                        "type": "string",
                        "description": "Key of the object to get. Length Constraints: Minimum length of 1.",
                    },
                    "disable_ssl": {
                        "type": "boolean",
                        "description": "Whether to disable SSL. By default, it is not disabled (HTTP protocol is used). If disabled, the HTTP protocol will be used.",
                    },
                    "expires": {
                        "type": "integer",
                        "description": "Token expiration time (in seconds) for download links. When the bucket is private, a signed Token is required to access file objects. Public buckets do not require Token signing.",
                    },
                },
                "required": ["bucket", "key"],
            },
        )
    )
    def get_object_url(self, **kwargs) -> list[types.TextContent]:
        urls = self.storage.get_object_url(**kwargs)
        return [types.TextContent(type="text", text=str(urls))]


def register_tools(storage: StorageService):
    tool_impl = _ToolImpl(storage)
    tools.auto_register_tools(
        [
            tool_impl.list_buckets,
            tool_impl.list_objects,
            tool_impl.get_object,
            tool_impl.upload_text_data,
            tool_impl.upload_file,
            tool_impl.fetch_object,
            tool_impl.get_object_url,
        ]
    )
