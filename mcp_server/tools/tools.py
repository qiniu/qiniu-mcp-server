from typing import Optional, List, Dict, Any, Callable

from mcp import types


from mcp.types import Tool

ToolEntryCallback = Callable[[dict], list[types.TextContent | types.ImageContent | types.EmbeddedResource]]


class ToolEntry:
    def __init__(self, tool: Tool, callback: ToolEntryCallback):
        self.tool = tool
        self.callback = callback


__all_tools = Dict[str, ToolEntry]()


def register_tool(tool: Tool, callback: ToolEntryCallback):
    __all_tools[tool.name] = ToolEntry(tool, callback)


async def fetch_tool(
        name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    tool_entry = __all_tools.get(name)
    if tool_entry is None:
        raise ValueError(f"Tool {name} not found")
    return await tool_entry.callback(arguments)
