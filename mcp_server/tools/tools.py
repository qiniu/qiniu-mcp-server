from typing import Optional, List, Dict, Any

from mcp_server.resource import resource


class Tools:

    def __init__(self, resource: resource.Resource):
        self.resource = resource

    async def list_buckets(self, prefix: Optional[str] = None) -> List[dict]:
        return await self.resource.list_buckets(prefix)

    async def list_objects(self, bucket_name: str, prefix: Optional[str] = None) -> List[dict]:
        return await self.resource.list_objects(bucket_name, prefix)

    async def get_object(self, bucket_name: str, key: str) -> Dict[str, Any]:
        return await self.resource.get_object(bucket_name, key)
