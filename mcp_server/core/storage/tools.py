import logging

from mcp import types

from .storage import Storage
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)


class _ToolImplement:

    def __init__(self, storage: Storage):
        self.storage = storage

    @staticmethod
    def list_buckets_tool() -> types.Tool:
        t = types.Tool(
            name="ListBuckets",  # https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListBuckets.html
            description="Returns a list of all buckets owned by the authenticated sender of the request. To grant IAM permission to use this operation, you must add the s3:ListAllMyBuckets policy action.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prefix": {"type": "string",
                               "description": "Bucket prefix. The listed Buckets will be filtered based on this prefix, and only those matching the prefix will be output."},
                },
                "required": [],
            },
        )
        return t

    async def list_buckets(self, **kwargs) -> list[
        types.TextContent | types.ImageContent | types.EmbeddedResource]:
        buckets = await self.storage.list_buckets(**kwargs)
        return [
            types.TextContent(
                type="text",
                text=str(buckets)
            )
        ]

    @staticmethod
    def list_objects_tool() -> types.Tool:
        return types.Tool(
            name="ListObjects",  # https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html
            description="Each request will return some or all (up to 100) objects in the bucket. You can use request parameters as selection criteria to return some objects in the bucket. If you want to continue listing, set start_after to the key of the last file in the last listing result so that you can list new content. To get a list of buckets, see ListBuckets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {"type": "string",
                               "description": "When you use this operation with a directory bucket, you must use virtual-hosted-style requests in the format Bucket_name.s3express-az_id.region.amazonaws.com. Path-style requests are not supported. Directory bucket names must be unique in the chosen Availability Zone. Bucket names must follow the format bucket_base_name--az-id--x-s3 (for example, DOC-EXAMPLE-BUCKET--usw2-az1--x-s3)."},
                    "max_keys": {"type": "integer",
                                 "description": "Sets the maximum number of keys returned in the response. By default, the action returns up to 20 key names. The response might contain fewer keys but will never contain more."},
                    "prefix": {"type": "string",
                               "description": "Limits the response to keys that begin with the specified prefix."},
                    "start_after": {"type": "string",
                                    "description": "start_after is where you want Amazon S3 to start listing from. Amazon S3 starts listing after this specified key. start_after can be any key in the bucket."}
                },
                "required": ["bucket"],
            },
        )

    async def list_objects(self, **kwargs) -> list[
        types.TextContent | types.ImageContent | types.EmbeddedResource]:
        objects = await self.storage.list_objects(**kwargs)
        return [
            types.TextContent(
                type="text",
                text=str(objects)
            )
        ]

    @staticmethod
    def get_object_tool() -> types.Tool:
        return types.Tool(
            name="GetObject",  # https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html
            description="Retrieves an object from Amazon S3. In the GetObject request, specify the full key name for the object. General purpose buckets - Both the virtual-hosted-style requests and the path-style requests are supported. For a virtual hosted-style request example, if you have the object photos/2006/February/sample.jpg, specify the object key name as /photos/2006/February/sample.jpg. For a path-style request example, if you have the object photos/2006/February/sample.jpg in the bucket named examplebucket, specify the object key name as /examplebucket/photos/2006/February/sample.jpg. Directory buckets - Only virtual-hosted-style requests are supported. For a virtual hosted-style request example, if you have the object photos/2006/February/sample.jpg in the bucket named examplebucket--use1-az5--x-s3, specify the object key name as /photos/2006/February/sample.jpg. Also, when you make requests to this API operation, your requests are sent to the Zonal endpoint. These endpoints support virtual-hosted-style requests in the format https://bucket_name.s3express-az_id.region.amazonaws.com/key-name . Path-style requests are not supported.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {"type": "string",
                               "description": "Directory buckets - When you use this operation with a directory bucket, you must use virtual-hosted-style requests in the format Bucket_name.s3express-az_id.region.amazonaws.com. Path-style requests are not supported. Directory bucket names must be unique in the chosen Availability Zone. Bucket names must follow the format bucket_base_name--az-id--x-s3 (for example, DOC-EXAMPLE-BUCKET--usw2-az1--x-s3)."},
                    "key": {"type": "string",
                            "description": "Key of the object to get. Length Constraints: Minimum length of 1."},
                },
                "required": ["bucket", "key"]
            },
        )

    async def get_object(self, **kwargs) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        response = await self.storage.get_object(**kwargs)
        file_content = response['Body']
        content_type = response.get('ContentType', 'application/octet-stream')

        # 根据内容类型返回不同的响应
        if content_type.startswith('image/'):
            # 图片类型，需要转换为 base64
            import base64
            base64_data = base64.b64encode(file_content).decode('utf-8')
            return [
                types.ImageContent(
                    type="image",
                    data=base64_data,
                    mimeType=content_type
                )
            ]
        else:
            if isinstance(file_content, bytes):
                text_content = file_content.decode('utf-8')
            else:
                text_content = str(file_content)
            return [
                types.TextContent(
                    type="text",
                    text=text_content
                )
            ]

    @staticmethod
    def get_object_url_tool() -> types.Tool:
        return types.Tool(
            name="GetObjectURL",  # https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html
            description="获取文件下载的 URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {"type": "string",
                               "description": "Directory buckets - When you use this operation with a directory bucket, you must use virtual-hosted-style requests in the format Bucket_name.s3express-az_id.region.amazonaws.com. Path-style requests are not supported. Directory bucket names must be unique in the chosen Availability Zone. Bucket names must follow the format bucket_base_name--az-id--x-s3 (for example, DOC-EXAMPLE-BUCKET--usw2-az1--x-s3)."},
                    "key": {"type": "string",
                            "description": "Key of the object to get. Length Constraints: Minimum length of 1."},
                    "disable_ssl": {"type": "bool",
                                    "description": "是否禁用 SSL，默认不禁用使用 HTTP 协议，禁用后使用 HTTP 协议"},
                    "expires": {"type": "int",
                                "description": "下载链接中 Token 有效期，单位是秒；当空间是私有空间时，访问文件对象时需要对文件链接签名 Token，公有空间不签 Token。"},
                },
                "required": ["bucket", "key"]
            },
        )

    def get_object_url(self, **kwargs) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        urls = self.storage.get_object_url(**kwargs)
        return [
            types.TextContent(
                type="text",
                text=str(urls)
            )
        ]


def register_tools(storage: Storage):
    tool_implement = _ToolImplement(storage)
    tools.register_tool(_ToolImplement.list_buckets_tool(), tool_implement.list_buckets)
    tools.register_tool(_ToolImplement.list_objects_tool(), tool_implement.list_objects)
    tools.register_tool(_ToolImplement.get_object_tool(), tool_implement.get_object)
    tools.register_tool(_ToolImplement.get_object_url_tool(), tool_implement.get_object_url)
