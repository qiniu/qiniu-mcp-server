import aiohttp
import logging

from typing import Dict, Any
from ...config import config
from ...consts import consts

logger = logging.getLogger(consts.LOGGER_NAME)


class MikuService:
    def __init__(self, cfg: config.Config = None):
        self.config = cfg
        self.api_key = cfg.access_key if cfg else None
        self.endpoint_url = cfg.endpoint_url if cfg else None

    def _get_auth_header(self) -> Dict[str, str]:
        """Generate Bearer token authorization header"""
        if not self.api_key:
            raise ValueError("QINIU_API_KEY is not configured")
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def _build_bucket_url(self, bucket: str) -> str:
        """Build S3-style bucket URL"""
        if not self.endpoint_url:
            raise ValueError("QINIU_ENDPOINT_URL is not configured")

        # Remove protocol if present in endpoint_url
        endpoint = self.endpoint_url
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]

        # Build URL in format: https://<bucket>.<endpoint>
        return f"https://{bucket}.{endpoint}"

    def _build_stream_url(self, bucket: str, stream: str) -> str:
        """Build S3-style stream URL"""
        if not self.endpoint_url:
            raise ValueError("QINIU_ENDPOINT_URL is not configured")

        # Remove protocol if present in endpoint_url
        endpoint = self.endpoint_url
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]

        # Build URL in format: https://<bucket>.<endpoint>/<stream>
        return f"https://{bucket}.{endpoint}/{stream}"

    async def create_bucket(self, bucket: str) -> Dict[str, Any]:
        """
        Create a bucket using S3-style API

        Args:
            bucket: The bucket name to create

        Returns:
            Dict containing the response status and message
        """
        url = self._build_bucket_url(bucket)
        headers = self._get_auth_header()

        logger.info(f"Creating bucket: {bucket} at {url}")

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers) as response:
                status = response.status
                text = await response.text()

                if status == 200 or status == 201:
                    logger.info(f"Successfully created bucket: {bucket}")
                    return {
                        "status": "success",
                        "bucket": bucket,
                        "url": url,
                        "message": f"Bucket '{bucket}' created successfully",
                        "status_code": status
                    }
                else:
                    logger.error(f"Failed to create bucket: {bucket}, status: {status}, response: {text}")
                    return {
                        "status": "error",
                        "bucket": bucket,
                        "url": url,
                        "message": f"Failed to create bucket: {text}",
                        "status_code": status
                    }

    async def create_stream(self, bucket: str, stream: str) -> Dict[str, Any]:
        """
        Create a stream using S3-style API

        Args:
            bucket: The bucket name
            stream: The stream name to create

        Returns:
            Dict containing the response status and message
        """
        url = self._build_stream_url(bucket, stream)
        headers = self._get_auth_header()

        logger.info(f"Creating stream: {stream} in bucket: {bucket} at {url}")

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers) as response:
                status = response.status
                text = await response.text()

                if status == 200 or status == 201:
                    logger.info(f"Successfully created stream: {stream} in bucket: {bucket}")
                    return {
                        "status": "success",
                        "bucket": bucket,
                        "stream": stream,
                        "url": url,
                        "message": f"Stream '{stream}' created successfully in bucket '{bucket}'",
                        "status_code": status
                    }
                else:
                    logger.error(f"Failed to create stream: {stream}, status: {status}, response: {text}")
                    return {
                        "status": "error",
                        "bucket": bucket,
                        "stream": stream,
                        "url": url,
                        "message": f"Failed to create stream: {text}",
                        "status_code": status
                    }
