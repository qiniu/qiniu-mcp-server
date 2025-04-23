import logging
from abc import abstractmethod
from typing import Dict, AsyncGenerator, Iterable

from mcp import types
from mcp.server.lowlevel.helper_types import ReadResourceContents

from ..consts import consts

logger = logging.getLogger(consts.LOGGER_NAME)

ResourceContents = str | bytes | Iterable[ReadResourceContents]

class ResourceProvider:
    def __init__(self, scheme: str):
        self.scheme = scheme

    @abstractmethod
    async def list_resources(self, **kwargs) -> list[types.Resource]:
        pass

    @abstractmethod
    async def read_resource(self, uri: types.AnyUrl, **kwargs) -> ResourceContents:
        pass


_all_resource_providers: Dict[str, ResourceProvider] = {}


async def list_resources(**kwargs) -> AsyncGenerator[types.Resource, None]:
    if len(_all_resource_providers) == 0:
        return

    for provider in _all_resource_providers.values():
        resources = await provider.list_resources(**kwargs)
        for resource in resources:
            yield resource
    return


async def read_resource(uri: types.AnyUrl, **kwargs) -> ResourceContents:
    if len(_all_resource_providers) == 0:
        return ""

    provider = _all_resource_providers.get(uri.scheme)
    return await provider.read_resource(uri=uri, **kwargs)


def register_resource_provider(provider: ResourceProvider):
    """注册工具，禁止重复名称"""
    name = provider.scheme
    if name in _all_resource_providers:
        raise ValueError(f"Resource Provider {name} already registered")
    _all_resource_providers[name] = provider


__all__ = [
    "ResourceContents",
    "ResourceProvider",
    "list_resources",
    "read_resource",
    "register_resource_provider",
]
