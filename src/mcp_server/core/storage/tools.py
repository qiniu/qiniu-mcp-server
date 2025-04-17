import logging
import base64

from mcp import types
from mcp.types import ImageContent, TextContent

from .storage import StorageService
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_BUCKET_DESC = """When you use this operation with a directory bucket, you must use virtual-hosted-style requests in the format ${bucket_name}.s3.${region_id}.qiniucs.com. Path-style requests are not supported. Directory bucket names must be unique in the chosen Availability Zone.
"""

class _ToolImpl:
    def __init__(self, storage: StorageService):
        self.storage = storage

    @tools.tool_meta(
        types.Tool(
            name="ListBuckets",
            description="Returns a list of all buckets owned by the authenticated sender of the request. To grant IAM permission to use this operation, you must add the s3:ListAllMyBuckets policy action.",
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
            description="Each request will return some or all (up to 100) objects in the bucket. You can use request parameters as selection criteria to return some objects in the bucket. If you want to continue listing, set start_after to the key of the last file in the last listing result so that you can list new content. To get a list of buckets, see ListBuckets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {
                        "type": "string",
                        "description": _BUCKET_DESC,
                    },
                    "max_keys": {
                        "type": "integer",
                        "description": "Sets the maximum number of keys returned in the response. By default, the action returns up to 20 key names. The response might contain fewer keys but will never contain more.",
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Limits the response to keys that begin with the specified prefix.",
                    },
                    "start_after": {
                        "type": "string",
                        "description": "start_after is where you want S3 to start listing from. S3 starts listing after this specified key. start_after can be any key in the bucket.",
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
            description="Retrieves an object from Qiniu bucket. In the GetObject request, specify the full key name for the object. Path-style requests are not supported.",
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
            name="GetObjectURL",
            description="Get the file download URL, and note that the Bucket where the file is located must be bound to a domain name. If using Qiniu's test domain, HTTPS access will not be available, and users need to make adjustments for this themselves.",
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
            tool_impl.get_object_url,
        ]
    )
