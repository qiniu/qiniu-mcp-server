import logging
from contextlib import aclosing

import mcp.types as types
from mcp.types import EmptyResult

from mcp import LoggingLevel
from mcp.server.lowlevel import Server
from mcp.types import Tool, AnyUrl

from . import core
from .consts import consts
from .resource import resource
from .tools import tools


logger = logging.getLogger(consts.LOGGER_NAME)

core.load()
server = Server("qiniu-mcp-server")


@server.set_logging_level()
async def set_logging_level(level: LoggingLevel) -> EmptyResult:
    logger.setLevel(level.lower())
    await server.request_context.session.send_log_message(
        level="warning", data=f"Log level set to {level}", logger=consts.LOGGER_NAME
    )
    return EmptyResult()


@server.list_resources()
async def list_resources(**kwargs) -> list[types.Resource]:
    resource_list = []
    async with aclosing(resource.list_resources(**kwargs)) as results:
        async for result in results:
            resource_list.append(result)
    return resource_list


@server.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    return await resource.read_resource(uri)


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return tools.all_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    return await tools.call_tool(name, arguments)
