import aioboto3
import asyncio
import logging

from typing import List, Dict, Any, Optional
from botocore.config import Config as S3Config

from ...config import config
from ...consts import consts

logger = logging.getLogger(consts.LOGGER_NAME)


class Storage:
    """
    S3 Resource provider that handles interactions with AWS S3 buckets.
    Part of a collection of resource providers (S3, DynamoDB, etc.) for the MCP server.
    """

    def __init__(self, cfg: config.Config = None):
        """
        Initialize S3 resource provider
        """
        # Configure boto3 with retries and timeouts
        self.s3_config = S3Config(
            retries=dict(
                max_attempts=3,
                mode='adaptive'
            ),
            connect_timeout=5,
            read_timeout=60,
            max_pool_connections=50,
        )
        self.config = cfg
        self.session = aioboto3.Session()

    async def list_buckets(self, prefix: Optional[str] = None) -> List[dict]:
        """
        List S3 buckets using async client with pagination
        """
        max_buckets = 50

        async with self.session.client('s3',
                                       aws_access_key_id=self.config.access_key,
                                       aws_secret_access_key=self.config.secret_key,
                                       endpoint_url=self.config.endpoint_url,
                                       region_name=self.config.region_name) as s3:
            if self.config.buckets:
                # If buckets are configured, only return those
                response = await s3.list_buckets()
                all_buckets = response.get('Buckets', [])

                configured_bucket_list = [
                    bucket for bucket in all_buckets
                    if bucket['Name'] in self.config.buckets
                ]

                if prefix:
                    configured_bucket_list = [
                        b for b in configured_bucket_list
                        if b['Name'] > prefix
                    ]

                return configured_bucket_list[:max_buckets]
            else:
                # Default behavior if no buckets configured
                response = await s3.list_buckets()
                buckets = response.get('Buckets', [])

                if prefix:
                    buckets = [b for b in buckets if b['Name'] > prefix]

                return buckets[:max_buckets]

    async def list_objects(self, bucket: str, prefix: str = "", max_keys: int = 20, start_after: str = "") -> List[
        dict]:
        """
        List objects in a specific bucket using async client with pagination
        Args:
            bucket: Name of the S3 bucket
            prefix: Object prefix for filtering
            max_keys: Maximum number of keys to return
            start_after: the index that list from，can be last object key
        """
        #
        if self.config.buckets and bucket not in self.config.buckets:
            logger.warning(f"Bucket {bucket} not in configured bucket list")
            return []

        if isinstance(max_keys, str):
            max_keys = int(max_keys)

        if max_keys > 100:
            max_keys = 100

        async with self.session.client('s3',
                                       aws_access_key_id=self.config.access_key,
                                       aws_secret_access_key=self.config.secret_key,
                                       endpoint_url=self.config.endpoint_url,
                                       region_name=self.config.region_name) as s3:
            response = await s3.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys,
                StartAfter=start_after,
            )
            return response.get('Contents', [])

    async def get_object(self, bucket: str, key: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Get object from S3 using streaming to handle large files and PDFs reliably.
        The method reads the stream in chunks and concatenates them before returning.
        """
        if self.config.buckets and bucket not in self.config.buckets:
            logger.warning(f"Bucket {bucket} not in configured bucket list")
            return {}

        attempt = 0
        last_exception = None

        while attempt < max_retries:
            try:
                async with self.session.client('s3',
                                               aws_access_key_id=self.config.access_key,
                                               aws_secret_access_key=self.config.secret_key,
                                               endpoint_url=self.config.endpoint_url,
                                               region_name=self.config.region_name,
                                               config=self.s3_config) as s3:

                    # Get the object and its stream
                    response = await s3.get_object(Bucket=bucket, Key=key)
                    stream = response['Body']

                    # Read the entire stream in chunks
                    chunks = []
                    async for chunk in stream:
                        chunks.append(chunk)

                    # Replace the stream with the complete data
                    response['Body'] = b''.join(chunks)
                    return response

            except Exception as e:
                last_exception = e
                if 'NoSuchKey' in str(e):
                    raise

                attempt += 1
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Attempt {attempt} failed, retrying in {wait_time} seconds: {str(e)}")
                    await asyncio.sleep(wait_time)
                continue

        raise last_exception or Exception("Failed to get object after all retries")

    def is_text_file(self, key: str) -> bool:
        """Determine if a file is text-based by its extension"""
        text_extensions = {
            '.txt', '.log', '.json', '.xml', '.yml', '.yaml', '.md',
            '.csv', '.ini', '.conf', '.py', '.js', '.html', '.css',
            '.sh', '.bash', '.cfg', '.properties'
        }
        return any(key.lower().endswith(ext) for ext in text_extensions)

    def is_image_file(self, key: str) -> bool:
        """Determine if a file is text-based by its extension"""
        text_extensions = {
            '.png', '.jpeg', '.jpg', '.gif', '.bmp', '.tiff', '.svg', '.webp',
        }
        return any(key.lower().endswith(ext) for ext in text_extensions)

    def is_markdown_file(self, key: str) -> bool:
        """Determine if a file is text-based by its extension"""
        text_extensions = {
            '.md',
        }
        return any(key.lower().endswith(ext) for ext in text_extensions)
