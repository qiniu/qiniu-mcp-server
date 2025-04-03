from abc import abstractmethod
from typing import Dict, Optional

from mcp import types


class ResourceProvider:

    def __init__(self, scheme: str):
        self.scheme = scheme

    @abstractmethod
    async def list_resources(self, prefix: Optional[str], max_keys: int = 20, **kwargs) -> list[types.Resource]:
        pass

    @abstractmethod
    async def read_resource(self, uri: types.AnyUrl, **kwargs) -> str:
        pass


_all_resource_providers: Dict[str, ResourceProvider] = {}


async def list_resources(prefix: Optional[str], max_keys: int = 20, **kwargs) -> list[types.Resource]:
    if len(_all_resource_providers) == 0:
        yield []
        return

    for provider in _all_resource_providers.values():
        resources = await provider.list_resources(prefix=prefix, max_keys=max_keys, **kwargs)
        for resource in resources:
            yield resource


async def read_resource(uri: types.AnyUrl, **kwargs) -> str:
    if len(_all_resource_providers) == 0:
        yield ""
        return

    provider = _all_resource_providers.get(uri.scheme)
    yield await provider.read_resource(uri=uri, **kwargs)
    return


def register_resource_provider(provider: ResourceProvider):
    """注册工具，禁止重复名称"""
    name = provider.scheme
    if name in _all_resource_providers:
        raise ValueError(f"Resource Provider {name} already registered")
    _all_resource_providers[name] = provider


__all__ = [
    "ResourceProvider",
    "list_resources",
    "read_resource",
    "register_resource_provider",
]
