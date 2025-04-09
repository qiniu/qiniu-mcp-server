import logging
from mcp import types

from . import utils
from .client import Client
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_OBJECT_URL_DESC = "图片的 URL，可以通过 GetObjectURL 工具获取的 URL，也可以是其他 Fop 工具生成的 url。 Length Constraints: Minimum length of 1."


class _ToolImplement:

    def __init__(self, cli: Client):
        self.client = cli

    @staticmethod
    def image_scale_by_percent_fop() -> types.Tool:
        return types.Tool(
            name="ImageScaleByPercentFop",
            description="图片缩放工具，根据缩放的百分比对图片进行缩放，返回缩放后图片的信息，信息中包含图片的缩放后的 object_url，图片必须存储在七牛云 Bucket 中。",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {"type": "string", "description": _OBJECT_URL_DESC},
                    "percent": {
                        "type": "integer",
                        "description": "缩放百分比，范围在[1,999]，比如：90 即为是图片的宽高均缩小至原来的 90%；200 即为是图片的宽高均扩大至原来的 200%",
                    },
                },
                "required": ["percent"],
            },
        )

    def image_scale_by_percent(
        self, **kwargs
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        object_url = kwargs.get("object_url", "")
        percent = kwargs.get("percent", "")
        if object_url is None or len(object_url) == 0:
            return [types.TextContent(type="text", text="object_url is required")]

        if percent is None or len(percent) == 0:
            return [types.TextContent(type="text", text="percent is required")]

        percent_int = int(percent)
        if percent_int < 1 or percent_int > 999:
            return [
                types.TextContent(type="text", text="percent must be between 1 and 999")
            ]

        fop = f"imageMogr2/thumbnail/!{percent}p"
        object_url = utils.url_add_processing_tool(object_url, fop)
        return [
            types.TextContent(
                type="text",
                text=str(
                    {
                        "object_url": object_url,
                    }
                ),
            )
        ]

    @staticmethod
    def image_scale_by_size_tool() -> types.Tool:
        return types.Tool(
            name="ImageScaleBySizeFop",
            description="图片缩放工具，可以根据新图片的宽或高对图片进行缩放，返回缩放后图片的信息，信息中包含图片的缩放后的 object_url，图片必须存储在七牛云 Bucket 中。原图格式支持： psd、jpeg、png、gif、webp、tiff、bmp、avif、heic。图片 width 和 height 不能超过3万像素，总像素不能超过1.5亿像素",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {"type": "string", "description": _OBJECT_URL_DESC},
                    "width": {
                        "type": "integer",
                        "description": "指定图片宽度进行缩放，也即图片缩放到指定的宽度，图片高度按照宽度缩放比例进行适应。",
                    },
                    "height": {
                        "type": "integer",
                        "description": "指定图片高度进行缩放，也即图片缩放到指定的高度，图片宽度按照高度缩放比例进行适应。",
                    },
                },
                "required": [],
            },
        )

    def image_scale_by_size(
        self, **kwargs
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        object_url = kwargs.get("object_url", "")
        width = kwargs.get("width", "")
        height = kwargs.get("height", "")
        if object_url is None or len(object_url) == 0:
            return [types.TextContent(type="text", text="object_url is required")]

        fop = f"{width}x{height}"
        if len(fop) == 1:
            return [
                types.TextContent(
                    type="text", text="At least one width or height must be set"
                )
            ]

        fop = f"imageMogr2/thumbnail/{fop}"
        object_url = utils.url_add_processing_tool(object_url, fop)
        return [
            types.TextContent(
                type="text",
                text=str(
                    {
                        "object_url": object_url,
                    }
                ),
            )
        ]

    @staticmethod
    def get_fop_status_tool() -> types.Tool:
        return types.Tool(
            name="GetFopStatus",
            description="获取 Fop 执行状态",
            inputSchema={
                "type": "object",
                "properties": {
                    "persistent_id": {
                        "type": "string",
                        "description": "执行 Fop 返回的操作 ID",
                    },
                },
                "required": ["persistent_id"],
            },
        )

    def get_fop_status(
        self, **kwargs
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        status = self.client.get_fop_status(**kwargs)
        return [types.TextContent(type="text", text=str(status))]


def register_tools(cli: Client):
    tool = _ToolImplement(cli)
    tools.register_tool(
        _ToolImplement.image_scale_by_percent_fop(), tool.image_scale_by_percent
    )
    tools.register_tool(
        _ToolImplement.image_scale_by_size_tool(), tool.image_scale_by_size
    )
    # tools.register_tool(_ToolImplement.get_fop_status_tool(), tool.get_fop_status)
