import asyncio
import logging
import base64

from mcp import types
from urllib.parse import unquote

from mcp.server.lowlevel.helper_types import ReadResourceContents

from .storage import StorageService
from ...consts import consts
from ...resource import resource
from ...resource.resource import ResourceContents

logger = logging.getLogger(consts.LOGGER_NAME)


class _ResourceProvider(resource.ResourceProvider):
    def __init__(self, storage: StorageService):
        super().__init__("s3")
        self.storage = storage

    async def list_resources(
        self, prefix: str = "", max_keys: int = 20, **kwargs
    ) -> list[types.Resource]:
        """
        List S3 buckets and their contents as resources with pagination
        Args:
            prefix: Prefix listing after this bucket name
            max_keys: Returns the maximum number of keys (up to 100), default 20
        """
        resources = []
        logger.debug("Starting to list resources")
        logger.debug(f"Configured buckets: {self.storage.config.buckets}")

        try:
            # Get limited number of buckets
            buckets = await self.storage.list_buckets(prefix)

            # limit concurrent operations
            async def process_bucket(bucket):
                bucket_name = bucket["Name"]
                logger.debug(f"Processing bucket: {bucket_name}")

                try:
                    # List objects in the bucket with a reasonable limit
                    objects = await self.storage.list_objects(
                        bucket_name, max_keys=max_keys
                    )

                    for obj in objects:
                        if "Key" in obj and not obj["Key"].endswith("/"):
                            object_key = obj["Key"]
                            if self.storage.is_markdown_file(object_key):
                                mime_type = "text/markdown"
                            elif self.storage.is_image_file(object_key):
                                mime_type = "image/png"
                            else:
                                mime_type = "text/plain"

                            resource_entry = types.Resource(
                                uri=f"s3://{bucket_name}/{object_key}",
                                name=object_key,
                                mimeType=mime_type,
                                description=str(obj),
                            )
                            resources.append(resource_entry)
                            logger.debug(f"Added resource: {resource_entry.uri}")

                except Exception as e:
                    logger.error(
                        f"Error listing objects in bucket {bucket_name}: {str(e)}"
                    )

            # Use semaphore to limit concurrent bucket processing
            semaphore = asyncio.Semaphore(3)  # Limit concurrent bucket processing

            async def process_bucket_with_semaphore(bucket):
                async with semaphore:
                    await process_bucket(bucket)

            # Process buckets concurrently
            await asyncio.gather(
                *[process_bucket_with_semaphore(bucket) for bucket in buckets]
            )

        except Exception as e:
            logger.error(f"Error listing buckets: {str(e)}")
            raise

        logger.info(f"Returning {len(resources)} resources")
        return resources

    async def read_resource(self, uri: types.AnyUrl, **kwargs) -> ResourceContents:
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
        path = uri_str[5:]  # Remove "s3://"
        path = unquote(path)  # Decode URL-encoded characters
        parts = path.split("/", 1)

        if len(parts) < 2:
            raise ValueError("Invalid S3 URI format")

        bucket = parts[0]
        key = parts[1]

        response = await self.storage.get_object(bucket, key)
        file_content = response["Body"]

        content_type = response.get("ContentType", "application/octet-stream")
        # 根据内容类型返回不同的响应
        if content_type.startswith("image/"):
            file_content = base64.b64encode(file_content).decode("utf-8")

        return [ReadResourceContents(mime_type=content_type, content=file_content)]


def register_resource_provider(storage: StorageService):
    resource_provider = _ResourceProvider(storage)
    resource.register_resource_provider(resource_provider)
