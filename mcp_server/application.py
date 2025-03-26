import asyncio
import logging
from typing import Optional

import mcp.types as types
from mcp.types import EmptyResult, Resource as ResourceEntry

from mcp import LoggingLevel
from mcp.server.lowlevel import Server
from mcp.types import Tool, AnyUrl
from .consts.consts import ToolTypes, get_logger_name
from .resource.resource import Resource
from .tools.tools import Tools

resource = Resource()
tools = Tools(resource)
logger = logging.getLogger(get_logger_name())

server = Server("mcp-simple-resource")


@server.set_logging_level()
async def set_logging_level(level: LoggingLevel) -> EmptyResult:
    logger.setLevel(level.lower())
    await server.request_context.session.send_log_message(
        level="warning",
        data=f"Log level set to {level}",
        logger="mcp_s3_server"
    )
    return EmptyResult()


@server.list_resources()
async def list_resources(prefix: Optional[str] = None) -> list[types.Resource]:
    """
    List S3 buckets and their contents as resources with pagination
    Args:
        prefix: Prefix listing after this bucket name
    """
    resources = []
    logger.debug("Starting to list resources")
    logger.debug(f"Configured buckets: {resource.configured_buckets}")

    try:
        # Get limited number of buckets
        buckets = await resource.list_buckets(prefix)
        logger.debug(f"Processing {len(buckets)} buckets (max: {resource.max_buckets})")

        # limit concurrent operations
        async def process_bucket(bucket):
            bucket_name = bucket['Name']
            logger.debug(f"Processing bucket: {bucket_name}")

            try:
                # List objects in the bucket with a reasonable limit
                objects = await resource.list_objects(bucket_name, max_keys=1000)

                for obj in objects:
                    if 'Key' in obj and not obj['Key'].endswith('/'):
                        object_key = obj['Key']
                        mime_type = "text/plain" if resource.is_text_file(object_key) else "text/markdown"

                        resourceEntry = ResourceEntry(
                            uri=f"s3://{bucket_name}/{object_key}",
                            name=object_key,
                            mimeType=mime_type
                        )
                        resources.append(resourceEntry)
                        logger.debug(f"Added resource: {resourceEntry.uri}")

            except Exception as e:
                logger.error(f"Error listing objects in bucket {bucket_name}: {str(e)}")

        # Use semaphore to limit concurrent bucket processing
        semaphore = asyncio.Semaphore(3)  # Limit concurrent bucket processing

        async def process_bucket_with_semaphore(bucket):
            async with semaphore:
                await process_bucket(bucket)

        # Process buckets concurrently
        await asyncio.gather(*[process_bucket_with_semaphore(bucket) for bucket in buckets])

    except Exception as e:
        logger.error(f"Error listing buckets: {str(e)}")
        raise

    logger.info(f"Returning {len(resources)} resources")
    return resources


@server.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """
    Read content from an S3 resource and return structured response

    Returns:
        Dict containing 'contents' list with uri, mimeType, and text for each resource
    """
    uri_str = str(uri)
    logger.debug(f"Reading resource: {uri_str}")

    if not uri_str.startswith("s3://"):
        raise ValueError("Invalid S3 URI")

    # Parse the S3 URI
    from urllib.parse import unquote
    path = uri_str[5:]  # Remove "s3://"
    path = unquote(path)  # Decode URL-encoded characters
    parts = path.split("/", 1)

    if len(parts) < 2:
        raise ValueError("Invalid S3 URI format")

    bucket = parts[0]
    key = parts[1]

    response = await resource.get_object(bucket, key)
    file_content = response['Body']
    return file_content

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="ListBuckets",  # https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListBuckets.html
            description="Returns a list of all buckets owned by the authenticated sender of the request. To grant IAM permission to use this operation, you must add the s3:ListAllMyBuckets policy action.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prefix": {"type": "string",
                                          "description": "Bucket prefix. The listed Buckets will be filtered based on this prefix, and only those matching the prefix will be output."},
                    "max_buckets": {"type": "integer",
                                   "description": "Maximum number of buckets to be returned in response. When the number is more than the count of buckets that are owned by an AWS account, return all the buckets in response. Valid Range: Minimum value of 1. Maximum value of 10000."},
                },
                "required": [],
            },
        ),
        Tool(
            name="ListObjectsV2",  # https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html
            description="Returns some or all (up to 1,000) of the objects in a bucket with each request. You can use the request parameters as selection criteria to return a subset of the objects in a bucket. To get a list of your buckets, see ListBuckets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {"type": "string",
                               "description": "When you use this operation with a directory bucket, you must use virtual-hosted-style requests in the format Bucket_name.s3express-az_id.region.amazonaws.com. Path-style requests are not supported. Directory bucket names must be unique in the chosen Availability Zone. Bucket names must follow the format bucket_base_name--az-id--x-s3 (for example, DOC-EXAMPLE-BUCKET--usw2-az1--x-s3)."},
                    "max_keys": {"type": "integer",
                                "description": "Sets the maximum number of keys returned in the response. By default, the action returns up to 1,000 key names. The response might contain fewer keys but will never contain more."},
                    "prefix": {"type": "string",
                               "description": "Limits the response to keys that begin with the specified prefix."},
                },
                "required": ["Bucket"],
            },
        ),
        Tool(
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
                "required": ["Bucket", "Key"]
            }
        )
    ]


@server.call_tool()
async def fetch_tool(
        name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        match name:
            case "ListBuckets":
                buckets = await resource.list_buckets(**arguments)
                return [
                    types.TextContent(
                        type="text",
                        text=str(buckets)
                    )
                ]
            case "ListObjectsV2":
                objects = await resource.list_objects(**arguments)
                return [
                    types.TextContent(
                        type="text",
                        text=str(objects)
                    )
                ]
            case "GetObject":
                response = await resource.get_object(**arguments)
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
                    return [
                        types.TextContent(
                            type="text",
                            text=text_content
                        )
                    ]
    except Exception as error:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(error)}"
            )
        ]
