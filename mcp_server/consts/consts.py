from enum import Enum

__LOGGER_NAME = "qiniu-s3-mcp"


def get_logger_name() -> str:
    return __LOGGER_NAME


ToolTypesListBuckets = "ListBuckets"
ToolTypesListObjects = "ListObjects"
ToolTypesGetObject = "GetObject"


ConfigEnvKeyAccessKey = "QINIU_ACCESS_KEY"
ConfigEnvKeySecretKey = "QINIU_SECRET_KEY"
ConfigEnvKeyEndpointUrl = "QINIU_ENDPOINT_URL"
ConfigEnvKeyRegionName = "QINIU_REGION_NAME"
ConfigEnvKeyBuckets = "QINIU_BUCKETS"
ConfigEnvKeyMaxBuckets = "QINIU_MAX_BUCKETS"
