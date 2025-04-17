import functools
import inspect
import asyncio
import logging
import fastjsonschema

from typing import List, Dict, Callable, Optional, Union, Awaitable
from dataclasses import dataclass
from mcp import types

from .. import consts

logger = logging.getLogger(consts.LOGGER_NAME)

ToolResult = list[types.TextContent | types.ImageContent | types.EmbeddedResource]
ToolFunc = Callable[..., ToolResult]
AsyncToolFunc = Callable[..., Awaitable[ToolResult]]


@dataclass
class _ToolEntry:
    meta: types.Tool
    func: Optional[ToolFunc]
    async_func: Optional[AsyncToolFunc]
    input_validator: Optional[Callable[..., None]]


# 初始化全局工具字典
_all_tools: Dict[str, _ToolEntry] = {}


def all_tools() -> List[types.Tool]:
    """获取所有工具"""
    if not _all_tools:
        raise ValueError("No tools registered")
    return list(map(lambda x: x.meta, _all_tools.values()))


def register_tool(
        meta: types.Tool,
        func: Union[ToolFunc, AsyncToolFunc],
) -> None:
    """注册工具，禁止重复名称"""
    name = meta.name
    if name in _all_tools:
        raise ValueError(f"Tool {name} already registered")

    # 判断是否为异步函数
    if inspect.iscoroutinefunction(func):
        async_func = func
        func = None
    else:
        async_func = None
    entry = _ToolEntry(
        meta=meta,
        func=func,
        async_func=async_func,
        input_validator=fastjsonschema.compile(meta.inputSchema),
    )
    _all_tools[name] = entry


def tool_meta(meta: types.Tool):
    def _add_metadata(**kwargs):
        def decorator(func):
            if inspect.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)

                wrapper = async_wrapper
            else:

                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                wrapper = sync_wrapper
            for key, value in kwargs.items():
                setattr(wrapper, key, value)
            return wrapper

        return decorator

    return _add_metadata(tool_meta=meta)


def auto_register_tools(func_list: list[Union[ToolFunc, AsyncToolFunc]]):
    """尝试自动注册带有 tool_meta 的工具"""
    for func in func_list:
        if hasattr(func, "tool_meta"):
            meta = getattr(func, "tool_meta")
            register_tool(meta=meta, func=func)
        else:
            raise ValueError("func must have tool_meta attribute")


async def call_tool(name: str, arguments: dict) -> ToolResult:
    """执行工具并处理异常"""

    # 工具存在性校验
    if (tool_entry := _all_tools.get(name)) is None:
        raise ValueError(f"Tool {name} not found")

    # 工具输入参数校验
    # 把 None 移除否则校验不过
    arguments = {k: v for k, v in arguments.items() if v is not None}
    try:
        tool_entry.input_validator(arguments)
    except fastjsonschema.JsonSchemaException as e:
        raise ValueError(f"Invalid arguments for tool {name}: {e}")

    try:
        if tool_entry.async_func is not None:
            # 异步函数直接执行
            result = await tool_entry.async_func(**arguments)
            return result
        elif tool_entry.func is not None:
            # 同步函数需要到线程池中转化为异步函数执行
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor=None,  # 使用全局线程池
                func=lambda: tool_entry.func(**arguments),
            )
            return result
        else:
            raise ValueError(f"Unexpected tool entry: {tool_entry}")
    except Exception as e:
        raise RuntimeError(f"Tool {name} execution error: {str(e)}") from e


# 明确导出接口
__all__ = [
    "all_tools",
    "register_tool",
    "call_tool",
    "tool_meta",
    "auto_register_tools",
]
