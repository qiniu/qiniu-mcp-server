import aiohttp
import json
import logging
import qiniu

from typing import Dict, Any
from ...config import config
from ...consts import consts

logger = logging.getLogger(consts.LOGGER_NAME)


class LiveStreamingService:
    def __init__(self, cfg: config.Config = None):
        self.config = cfg
        self.api_key = cfg.api_key if cfg else None
        self.endpoint_url = cfg.endpoint_url if cfg else None
        self.access_key = cfg.access_key if cfg else None
        self.secret_key = cfg.secret_key if cfg else None

        # Initialize qiniu.Auth if access_key and secret_key are available
        self.auth = None
        if self.access_key and self.secret_key and \
           self.access_key != "YOUR_QINIU_ACCESS_KEY" and \
           self.secret_key != "YOUR_QINIU_SECRET_KEY":
            self.auth = qiniu.Auth(self.access_key, self.secret_key)

    def _get_auth_header(self, url: str = "", body: bytes = None, content_type: str = "application/x-www-form-urlencoded") -> Dict[str, str]:
        """
        Generate authorization header
        Priority: QINIU_ACCESS_KEY/QINIU_SECRET_KEY > API KEY

        Args:
            url: The request URL for signing (required for Qiniu Auth)
            body: The request body for signing
            content_type: The content type of the request
        """
        # Priority 1: Use QINIU_ACCESS_KEY/QINIU_SECRET_KEY if configured
        if self.auth:
            # Generate Qiniu token for the request with the actual URL
            # This ensures proper authentication for dynamic hosts like <bucket>.mls.cn-east-1.qiniumiku.com
            token = self.auth.token_of_request(
                url=url,
                body=body,
                content_type=content_type
            )
            return {
                "Authorization": f"Qiniu {token}"
            }

        # Priority 2: Fall back to API KEY if ACCESS_KEY/SECRET_KEY not configured
        if not self.api_key or self.api_key == "YOUR_QINIU_API_KEY":
            raise ValueError("Neither QINIU_ACCESS_KEY/QINIU_SECRET_KEY nor QINIU_API_KEY is configured")

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
        headers = self._get_auth_header(url=url)

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
        headers = self._get_auth_header(url=url)

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

    async def bind_push_domain(self, bucket: str, domain: str, domain_type: str = "pushRtmp") -> Dict[str, Any]:
        """
        Bind a push domain to the bucket

        Args:
            bucket: The bucket name
            domain: The push domain name
            domain_type: The type of push domain (default: pushRtmp)

        Returns:
            Dict containing the response status and message
        """
        url = f"{self._build_bucket_url(bucket)}/?pushDomain"
        data = {
            "domain": domain,
            "type": domain_type
        }
        body = json.dumps(data).encode('utf-8')
        headers = {
            **self._get_auth_header(url=url, body=body, content_type="application/json"),
            "Content-Type": "application/json"
        }

        logger.info(f"Binding push domain: {domain} (type: {domain_type}) to bucket: {bucket}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                status = response.status
                text = await response.text()

                if status == 200 or status == 201:
                    logger.info(f"Successfully bound push domain: {domain} to bucket: {bucket}")
                    return {
                        "status": "success",
                        "bucket": bucket,
                        "domain": domain,
                        "type": domain_type,
                        "message": f"Push domain '{domain}' bound successfully to bucket '{bucket}'",
                        "status_code": status
                    }
                else:
                    logger.error(f"Failed to bind push domain: {domain}, status: {status}, response: {text}")
                    return {
                        "status": "error",
                        "bucket": bucket,
                        "domain": domain,
                        "type": domain_type,
                        "message": f"Failed to bind push domain: {text}",
                        "status_code": status
                    }

    async def bind_play_domain(self, bucket: str, domain: str, domain_type: str = "live") -> Dict[str, Any]:
        """
        Bind a playback domain to the bucket

        Args:
            bucket: The bucket name
            domain: The playback domain name
            domain_type: The type of playback domain (default: live)

        Returns:
            Dict containing the response status and message
        """
        url = f"{self._build_bucket_url(bucket)}/?domain"
        data = {
            "domain": domain,
            "type": domain_type
        }
        body = json.dumps(data).encode('utf-8')
        headers = {
            **self._get_auth_header(url=url, body=body, content_type="application/json"),
            "Content-Type": "application/json"
        }

        logger.info(f"Binding playback domain: {domain} (type: {domain_type}) to bucket: {bucket}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                status = response.status
                text = await response.text()

                if status == 200 or status == 201:
                    logger.info(f"Successfully bound playback domain: {domain} to bucket: {bucket}")
                    return {
                        "status": "success",
                        "bucket": bucket,
                        "domain": domain,
                        "type": domain_type,
                        "message": f"Playback domain '{domain}' bound successfully to bucket '{bucket}'",
                        "status_code": status
                    }
                else:
                    logger.error(f"Failed to bind playback domain: {domain}, status: {status}, response: {text}")
                    return {
                        "status": "error",
                        "bucket": bucket,
                        "domain": domain,
                        "type": domain_type,
                        "message": f"Failed to bind playback domain: {text}",
                        "status_code": status
                    }

    def get_push_urls(self, push_domain: str, bucket: str, stream_name: str) -> Dict[str, Any]:
        """
        Generate push URLs for RTMP and WHIP protocols

        Args:
            push_domain: The push domain
            bucket: The bucket name
            stream_name: The stream name

        Returns:
            Dict containing RTMP and WHIP push URLs
        """
        rtmp_url = f"rtmp://{push_domain}/{bucket}/{stream_name}"
        whip_url = f"https://{push_domain}/{bucket}/{stream_name}.whip"

        logger.info(f"Generated push URLs for stream: {stream_name}")
        return {
            "status": "success",
            "push_domain": push_domain,
            "bucket": bucket,
            "stream_name": stream_name,
            "rtmp_url": rtmp_url,
            "whip_url": whip_url,
            "message": "Push URLs generated successfully"
        }

    def get_play_urls(self, play_domain: str, bucket: str, stream_name: str) -> Dict[str, Any]:
        """
        Generate playback URLs for FLV, M3U8, and WHEP protocols

        Args:
            play_domain: The playback domain
            bucket: The bucket name
            stream_name: The stream name

        Returns:
            Dict containing FLV, M3U8, and WHEP playback URLs
        """
        flv_url = f"https://{play_domain}/{bucket}/{stream_name}.flv"
        m3u8_url = f"https://{play_domain}/{bucket}/{stream_name}.m3u8"
        whep_url = f"https://{play_domain}/{bucket}/{stream_name}.whep"

        logger.info(f"Generated playback URLs for stream: {stream_name}")
        return {
            "status": "success",
            "play_domain": play_domain,
            "bucket": bucket,
            "stream_name": stream_name,
            "flv_url": flv_url,
            "m3u8_url": m3u8_url,
            "whep_url": whep_url,
            "message": "Playback URLs generated successfully"
        }

    async def query_live_traffic_stats(self, begin: str, end: str) -> Dict[str, Any]:
        """
        Query live streaming traffic statistics

        Args:
            begin: Start time in format YYYYMMDDHHMMSS (e.g., 20240101000000)
            end: End time in format YYYYMMDDHHMMSS (e.g., 20240129105148)

        Returns:
            Dict containing traffic statistics
        """
        if not self.endpoint_url:
            raise ValueError("QINIU_ENDPOINT_URL is not configured")

        # Remove protocol and bucket prefix to get base endpoint
        endpoint = self.endpoint_url
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]

        # Remove bucket prefix if present (format: bucket.endpoint)
       # if '.' in endpoint:
       #     parts = endpoint.split('.', 1)
       #     if len(parts) > 1:
       #         endpoint = parts[1]

        url = f"http://{endpoint}/?trafficStats&begin={begin}&end={end}&g=5min&select=flow&flow=downflow"
        headers = {
            **self._get_auth_header(url=url, content_type="application/json"),
            "Content-Type": "application/json"
        }

        logger.info(f"Querying live traffic stats from {begin} to {end}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status = response.status
                text = await response.text()

                if status == 200:
                    logger.info("Successfully queried live traffic stats")
                    return {
                        "status": "success",
                        "begin": begin,
                        "end": end,
                        "data": text,
                        "message": "Traffic statistics retrieved successfully",
                        "status_code": status
                    }
                else:
                    logger.error(f"Failed to query traffic stats, status: {status}, response: {text}")
                    return {
                        "status": "error",
                        "begin": begin,
                        "end": end,
                        "message": f"Failed to query traffic stats: {text}",
                        "status_code": status
                    }

    async def list_buckets(self) -> Dict[str, Any]:
        """
        List all live streaming spaces/buckets

        Returns:
            Dict containing the list of buckets
        """
        if not self.endpoint_url:
            raise ValueError("QINIU_ENDPOINT_URL is not configured")

        # Remove protocol to get base endpoint
        endpoint = self.endpoint_url
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]

        url = f"https://{endpoint}/"
        headers = self._get_auth_header(url=url)

        logger.info(f"Listing all live streaming buckets from {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status = response.status
                text = await response.text()

                if status == 200:
                    logger.info("Successfully listed all buckets")
                    return {
                        "status": "success",
                        "data": text,
                        "message": "Buckets listed successfully",
                        "status_code": status
                    }
                else:
                    logger.error(f"Failed to list buckets, status: {status}, response: {text}")
                    return {
                        "status": "error",
                        "message": f"Failed to list buckets: {text}",
                        "status_code": status
                    }

    async def list_streams(self, bucket_id: str) -> Dict[str, Any]:
        """
        List all streams in a specific live streaming bucket

        Args:
            bucket_id: The bucket ID/name

        Returns:
            Dict containing the list of streams in the bucket
        """
        if not self.endpoint_url:
            raise ValueError("QINIU_ENDPOINT_URL is not configured")

        # Remove protocol to get base endpoint
        endpoint = self.endpoint_url
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]

        url = f"https://{endpoint}/?streamlist&bucketId={bucket_id}"
        headers = self._get_auth_header(url=url)

        logger.info(f"Listing streams in bucket: {bucket_id}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status = response.status
                text = await response.text()

                if status == 200:
                    logger.info(f"Successfully listed streams in bucket: {bucket_id}")
                    return {
                        "status": "success",
                        "bucket_id": bucket_id,
                        "data": text,
                        "message": f"Streams in bucket '{bucket_id}' listed successfully",
                        "status_code": status
                    }
                else:
                    logger.error(f"Failed to list streams in bucket: {bucket_id}, status: {status}, response: {text}")
                    return {
                        "status": "error",
                        "bucket_id": bucket_id,
                        "message": f"Failed to list streams: {text}",
                        "status_code": status
                    }
