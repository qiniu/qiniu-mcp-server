import os
import aioboto3
import asyncio
import logging
from mcp_server.consts import consts
from typing import List, Dict, Any, Optional
from botocore.config import Config

logger = logging.getLogger(consts.get_logger_name())

class Resource:
    """
    S3 Resource provider that handles interactions with AWS S3 buckets.
    Part of a collection of resource providers (S3, DynamoDB, etc.) for the MCP server.
    """

    def __init__(self, region_name: str = None):
        """
        Initialize S3 resource provider
        Args:
            region_name: AWS region name
            profile_name: AWS profile name
            max_buckets: Maximum number of buckets to process (default: 5)
        """

        # Configure boto3 with retries and timeouts
        self.config = Config(
            retries=dict(
                max_attempts=3,
                mode='adaptive'
            ),
            connect_timeout=5,
            read_timeout=60,
            max_pool_connections=50
        )

        self.session = aioboto3.Session()
        self.region_name = region_name
        self.max_buckets = int(os.getenv('S3_MAX_BUCKETS', '5'))
        logger.info(f"Initializing Resource with max_buckets: {self.max_buckets}")
        self.configured_buckets = self._get_configured_buckets()
        logger.info(f"Configured buckets: {self.configured_buckets}")

    def _get_configured_buckets(self) -> List[str]:
        """
        Get configured bucket names from environment variables.
        Format in .env file:
        S3_BUCKETS=bucket1,bucket2,bucket3
        or
        S3_BUCKET_1=bucket1
        S3_BUCKET_2=bucket2
        see env.example ############
        """

        # Try comma-separated list first
        bucket_list = os.getenv('S3_BUCKETS')
        if bucket_list:
            buckets = [b.strip() for b in bucket_list.split(',')]
            return buckets

        # Try individual bucket entries
        buckets = []
        i = 1
        while True:
            bucket = os.getenv(f'S3_BUCKET_{i}')
            if not bucket:
                break
            buckets.append(bucket.strip())
            i += 1
        
        return buckets

    async def list_buckets(self, prefix: Optional[str] = None, max_buckets: int = 50) -> List[dict]:
        """
        List S3 buckets using async client with pagination
        """

        if max_buckets > 50:
            max_buckets = 50

        async with self.session.client('s3', region_name=self.region_name) as s3:
            max_buckets = max_buckets or self.max_buckets or 5
            if self.configured_buckets:
                # If buckets are configured, only return those
                response = await s3.list_buckets()
                all_buckets = response.get('Buckets', [])
                
                configured_bucket_list = [
                    bucket for bucket in all_buckets
                    if bucket['Name'] in self.configured_buckets
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

    async def list_objects(self, bucket: str, prefix: str = "", max_keys: int = 20, start_after: str = "") -> List[dict]:
        """
        List objects in a specific bucket using async client with pagination
        Args:
            bucket: Name of the S3 bucket
            prefix: Object prefix for filtering
            max_keys: Maximum number of keys to return
            start_after: the index that list from，can be last object key
        """
        #
        if self.configured_buckets and bucket not in self.configured_buckets:
            logger.warning(f"Bucket {bucket} not in configured bucket list")
            return []

        if max_keys > 100:
            max_keys = 100

        async with self.session.client('s3', region_name=self.region_name) as s3:
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
        if self.configured_buckets and bucket not in self.configured_buckets:
            raise ValueError(f"Bucket {bucket} not in configured bucket list")

        attempt = 0
        last_exception = None

        while attempt < max_retries:
            try:
                async with self.session.client('s3',
                                               region_name=self.region_name,
                                               config=self.config) as s3:

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
