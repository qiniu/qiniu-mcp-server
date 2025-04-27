import aioboto3
import logging
import qiniu

from typing import List, Dict, Any, Optional
from botocore.config import Config as S3Config

from ...config import config
from ...consts import consts

logger = logging.getLogger(consts.LOGGER_NAME)


class StorageService:
    def __init__(self, cfg: config.Config = None):
        # Configure boto3 with retries and timeouts
        self.s3_config = S3Config(
            retries=dict(max_attempts=3, mode="adaptive"),
            connect_timeout=5,
            read_timeout=60,
            max_pool_connections=50,
        )
        self.config = cfg
        self.s3_session = aioboto3.Session()
        self.auth = qiniu.Auth(cfg.access_key, cfg.secret_key)
        self.bucket_manager = qiniu.BucketManager(self.auth, preferred_scheme="https")

    def get_object_url(
            self, bucket: str, key: str, disable_ssl: bool = False, expires: int = 3600
    ) -> list[dict[str:Any]]:
        # 获取下载域名
        domains_getter = getattr(self.bucket_manager, "_BucketManager__uc_do_with_retrier")
        domains_list, domain_response = domains_getter('/v3/domains?tbl={0}'.format(bucket))
        if domain_response.status_code != 200:
            raise Exception(
                f"get bucket domain error：{domain_response.exception} reqId:{domain_response.req_id}"
            )

        if not domains_list or len(domains_list) == 0:
            raise Exception(
                f"get bucket domain error：domains_list is empty reqId:{domain_response.req_id}"
            )

        http_schema = "https" if not disable_ssl else "http"
        object_public_urls = []
        for domain in domains_list:
            # 被冻结
            freeze_types = domain.get("freeze_types")
            if freeze_types is not None:
                continue

            domain_url = domain.get("domain")
            if domain_url is None:
                continue

            object_public_urls.append({
                "object_url": f"{http_schema}://{domain_url}/{key}",
                "domain_type": "cdn" if domain.get("domaintype") is None or domain.get("domaintype") == 0 else "origin"
            })

        object_urls = []
        bucket_info, bucket_info_response = self.bucket_manager.bucket_info(bucket)
        if domain_response.status_code != 200:
            raise Exception(
                f"get bucket domain error：{bucket_info_response.exception} reqId:{bucket_info_response.req_id}"
            )
        if bucket_info["private"] != 0:
            for url_info in object_public_urls:
                public_url = url_info.get("object_url")
                if public_url is None:
                    continue
                url_info["object_url"] = self.auth.private_download_url(public_url, expires=expires)
                object_urls.append(url_info)
        else:
            for url_info in object_public_urls:
                object_urls.append(url_info)
        return object_urls

    async def list_buckets(self, prefix: Optional[str] = None) -> List[dict]:
        if not self.config.buckets or len(self.config.buckets) == 0:
            return []

        max_buckets = 50

        async with self.s3_session.client(
                "s3",
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                endpoint_url=self.config.endpoint_url,
                region_name=self.config.region_name,
        ) as s3:
            # If buckets are configured, only return those
            response = await s3.list_buckets()
            all_buckets = response.get("Buckets", [])

            configured_bucket_list = [
                bucket
                for bucket in all_buckets
                if bucket["Name"] in self.config.buckets
            ]

            if prefix:
                configured_bucket_list = [
                    b for b in configured_bucket_list if b["Name"] > prefix
                ]

            return configured_bucket_list[:max_buckets]

    async def list_objects(
            self, bucket: str, prefix: str = "", max_keys: int = 20, start_after: str = ""
    ) -> List[dict]:
        if self.config.buckets and bucket not in self.config.buckets:
            logger.warning(f"Bucket {bucket} not in configured bucket list")
            return []

        if isinstance(max_keys, str):
            max_keys = int(max_keys)

        if max_keys > 100:
            max_keys = 100

        async with self.s3_session.client(
                "s3",
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                endpoint_url=self.config.endpoint_url,
                region_name=self.config.region_name,
        ) as s3:
            response = await s3.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys,
                StartAfter=start_after,
            )
            return response.get("Contents", [])

    async def get_object(self, bucket: str, key: str) -> Dict[str, Any]:
        if self.config.buckets and bucket not in self.config.buckets:
            logger.warning(f"Bucket {bucket} not in configured bucket list")
            return {}

        async with self.s3_session.client(
                "s3",
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                endpoint_url=self.config.endpoint_url,
                region_name=self.config.region_name,
                config=self.s3_config,
        ) as s3:
            # Get the object and its stream
            response = await s3.get_object(Bucket=bucket, Key=key)
            stream = response["Body"]

            # Read the entire stream in chunks
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)

            # Replace the stream with the complete data
            response["Body"] = b"".join(chunks)
            return response

    def upload_text_data(self, bucket: str, key: str, data: str, overwrite: bool = False) -> list[dict[str:Any]]:
        policy = {
            "insertOnly": 1,
        }

        if overwrite:
            policy["insertOnly"] = 0
            policy["scope"] = f"{bucket}:{key}"

        token = self.auth.upload_token(bucket=bucket, key=key, policy=policy)
        ret, info = qiniu.put_data(up_token=token, key=key, data=bytes(data, encoding="utf-8"))
        if info.status_code != 200:
            raise Exception(f"Failed to upload object: {info}")

        return self.get_object_url(bucket, key)

    def upload_local_file(self, bucket: str, key: str, file_path: str, overwrite: bool = False) -> list[dict[str:Any]]:
        policy = {
            "insertOnly": 1,
        }

        if overwrite:
            policy["insertOnly"] = 0
            policy["scope"] = f"{bucket}:{key}"

        token = self.auth.upload_token(bucket=bucket, key=key, policy=policy)
        ret, info = qiniu.put_file(up_token=token, key=key, file_path=file_path)
        if info.status_code != 200:
            raise Exception(f"Failed to upload object: {info}")

        return self.get_object_url(bucket, key)

    def fetch_object(self, bucket: str, key: str, url: str):
        ret, info = self.bucket_manager.fetch(url, bucket, key=key)
        if info.status_code != 200:
            raise Exception(f"Failed to fetch object: {info}")

        return self.get_object_url(bucket, key)

    def is_text_file(self, key: str) -> bool:
        text_extensions = {
            ".ini",
            ".conf",
            ".py",
            ".js",
            ".xml",
            ".yml",
            ".properties",
            ".txt",
            ".log",
            ".json",
            ".yaml",
            ".md",
            ".csv",
            ".html",
            ".css",
            ".sh",
            ".bash",
            ".cfg",
        }
        return any(key.lower().endswith(ext) for ext in text_extensions)


    def is_image_file(self, key: str) -> bool:
        """Determine if a file is text-based by its extension"""
        text_extensions = {
            ".gif",
            ".png",
            ".jpg",
            ".bmp",
            ".jpeg",
            ".tiff",
            ".webp",
            ".svg",
        }
        return any(key.lower().endswith(ext) for ext in text_extensions)


    def is_markdown_file(self, key: str) -> bool:
        text_extensions = {
            ".md",
        }
        return any(key.lower().endswith(ext) for ext in text_extensions)
