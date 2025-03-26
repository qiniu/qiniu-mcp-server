from enum import Enum

__LOGGER_NAME = "qiniu-s3-mcp"


def get_logger_name() -> str:
    return __LOGGER_NAME


class ToolTypes(Enum):
    ListBuckets = "ListBuckets"
    ListObjects = "ListObjects"
    GetObject = "GetObject"
