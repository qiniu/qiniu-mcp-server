
from mcp import types

from . import version
from ...tools import tools


class _ToolImpl:
    def __init__(self):
        pass

    @tools.tool_meta(
        types.Tool(
            name="version",
            description="qiniu mcp server version info.",
            inputSchema={
                "type": "object",
                "required": [],
            }
        )
    )
    def version(self, **kwargs) -> list[types.TextContent]:
        return [types.TextContent(type="text", text=version.VERSION)]

def register_tools():
    tool_impl = _ToolImpl()
    tools.auto_register_tools(
        [
            tool_impl.version,
        ]
    )