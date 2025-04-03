import inspect

from typing import Optional, List, Dict, Any, Callable, Union, Awaitable

from mcp import types

ToolEntryCallback = Callable[[dict], Union[
    list[types.TextContent | types.ImageContent | types.EmbeddedResource],
    Awaitable[list[types.TextContent | types.ImageContent | types.EmbeddedResource]]
]]


class ToolEntry:
    def __init__(self, tool: types.Tool, callback: ToolEntryCallback):
        self.tool = tool
        self.callback = callback


# 初始化全局工具字典
_all_tools: Dict[str, ToolEntry] = {}

def all_tools() -> List[types.Tool]:
    """获取所有工具"""
    if not _all_tools:
        raise ValueError("No tools registered")

    tool_values = _all_tools.values()
    if not tool_values:
        raise ValueError("No tools registered")

    all_tool_items = []
    for tool in tool_values:
        all_tool_items.append(tool.tool)

    return all_tool_items

def register_tool(tool: types.Tool, callback: ToolEntryCallback) -> None:
    """注册工具，禁止重复名称"""
    name = tool.name
    if name in _all_tools:
        raise ValueError(f"Tool {name} already registered")
    _all_tools[name] = ToolEntry(tool, callback)


async def fetch_tool(
        name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """执行工具并处理异常"""
    if (tool_entry := _all_tools.get(name)) is None:
        raise ValueError(f"Tool {name} not found")

    try:
        result = tool_entry.callback(arguments)
        # 统一处理同步/异步回调
        return await result if inspect.isawaitable(result) else result
    except Exception as e:
        raise RuntimeError(f"Tool {name} execution error: {str(e)}") from e


# 明确导出接口
__all__ = ["all_tools", "register_tool", "fetch_tool"]
