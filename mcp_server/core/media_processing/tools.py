import logging
from mcp import types

from . import utils
from .client import Client
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_OBJECT_URL_DESC = "图片的 URL，可以通过 GetObjectURL 工具获取的 URL，也可以是其他 Fop 工具生成的 url。"


class _ToolImplement:

    def __init__(self, cli: Client):
        self.client = cli

    @staticmethod
    def image_scale_by_percent_fop() -> types.Tool:
        return types.Tool(
            name="ImageScaleByPercentFop",
            description="""图片缩放工具，根据缩放的百分比对图片进行缩放，返回缩放后图片的信息;
            信息中包含图片的缩放后的 object_url，用户可以直接使用 object_url 进行 HTTP GET 请求来获取此图片内容，也可以在浏览器中打开 object_url 中的链接查看文件内容。
            图片必须存储在七牛云 Bucket 中。
            原图格式支持： psd、jpeg、png、gif、webp、tiff、bmp、avif、heic。图片 width 和 height 不能超过3万像素，总像素不能超过1.5亿像素。
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {"type": "string",
                                   "description": _OBJECT_URL_DESC},
                    "percent": {"type": "int",
                                "description": "缩放百分比，范围在[1,999]，比如：90 即为是图片的宽高均缩小至原来的 90%；200 即为是图片的宽高均扩大至原来的 200%"},
                },
                "required": ["percent"],
            },
        )

    def image_scale_by_percent(self, **kwargs) -> list[
        types.TextContent | types.ImageContent | types.EmbeddedResource]:
        object_url = kwargs.get("object_url", "")
        percent = kwargs.get("percent", "")
        if object_url is None or len(object_url) == 0:
            return [
                types.TextContent(
                    type="text",
                    text="object_url is required"
                )
            ]

        if percent is None:
            return [
                types.TextContent(
                    type="text",
                    text="percent is required"
                )
            ]

        func = f"imageMogr2/thumbnail/!{percent}p"
        object_url = utils.url_add_processing_func(object_url, func)
        return [
            types.TextContent(
                type="text",
                text=str({
                    "object_url": object_url,
                })
            )
        ]

    @staticmethod
    def image_scale_by_size_tool() -> types.Tool:
        return types.Tool(
            name="ImageScaleBySizeFop",
            description="""图片缩放工具，可以根据新图片的宽或高对图片进行缩放，返回缩放后图片的信息。
            信息中包含图片的缩放后的 object_url，用户可以直接使用 object_url 进行 HTTP GET 请求来获取此图片内容，也可以在浏览器中打开 object_url 中的链接查看文件内容。
            图片必须存储在七牛云 Bucket 中。
            原图格式支持： psd、jpeg、png、gif、webp、tiff、bmp、avif、heic。图片 width 和 height 不能超过3万像素，总像素不能超过1.5亿像素。
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {"type": "string",
                                   "description": _OBJECT_URL_DESC},
                    "width": {"type": "int",
                              "description": "指定图片宽度进行缩放，也即图片缩放到指定的宽度，图片高度按照宽度缩放比例进行适应。"},
                    "height": {"type": "int",
                               "description": "指定图片高度进行缩放，也即图片缩放到指定的高度，图片宽度按照高度缩放比例进行适应。"},
                },
                "required": [],
            },
        )

    def image_scale_by_size(self, **kwargs) -> list[
        types.TextContent | types.ImageContent | types.EmbeddedResource]:
        object_url = kwargs.get("object_url", "")
        width = kwargs.get("width", "")
        height = kwargs.get("height", "")
        if object_url is None or len(object_url) == 0:
            return [
                types.TextContent(
                    type="text",
                    text="object_url is required"
                )
            ]


        func = f"{width}x{height}"
        if len(func) == 1:
            return [
                types.TextContent(
                    type="text",
                    text="At least one width or height must be set"
                )
            ]

        func = f"imageMogr2/thumbnail/{func}"
        object_url = utils.url_add_processing_func(object_url, func)
        return [
            types.TextContent(
                type="text",
                text=str({
                    "object_url": object_url,
                })
            )
        ]

    @staticmethod
    def image_round_corner_tool() -> types.Tool:
        return types.Tool(
            name="ImageRoundCorner",
            description="图片圆角工具，根据图片的宽高和圆角半径对图片进行圆角处理，返回圆角处理后的图片的信息。如果 radius_x 或 radius_y 只设置一个则另外一个参数会赋值为已设置参数的值，也即水平和垂直参数相同"
                        "信息中包含图片的圆角处理后的 object_url，用户可以直接使用 object_url 进行 HTTP GET 请求来获取此图片内容，也可以在浏览器中打开 object_url 中的链接查看文件内容。"
                        "图片必须存储在七牛云 Bucket中。"
                        "原图格式支持： psd、jpeg、png、gif、webp、tiff、bmp、avif、heic。图片 width 和 height 不能超过3万像素，总像素不能超过1.5亿像素。"
                        "圆角半径支持像素和百分比，但不能为负数；像素使用数字表示，如：200 表示 200px；百分比使用 !xp， 如 !25p 表示 25%",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {"type": "string",
                                   "description": _OBJECT_URL_DESC},
                    "radius_x": {"type": "string",
                                 "description": "圆角水平大小的参数，可以使用：像素值（如: 200 代表 200px）或者百分比（如: !25p 代表 25%），均为非负值。"},
                    "radius_y": {"type": "string",
                                 "description": "圆角垂直大小的参数，可以使用：像素值（如: 200 代表 200px）或者百分比（如: !25p 代表 25%），均为非负值。"},
                },
                "required": ["object_url"],
            }
        )

    def image_round_corner(self, **kwargs) -> list[
        types.TextContent | types.ImageContent | types.EmbeddedResource]:
        object_url = kwargs.get("object_url", "")
        radius_x = kwargs.get("radius_x", "")
        radius_y = kwargs.get("radius_y", "")
        if object_url is None or len(object_url) == 0:
            return [
                types.TextContent(
                    type="text",
                    text="object_url is required"
                )
            ]

        if (radius_x is None or len(radius_x) == 0) and (radius_y is None or len(radius_y) == 0) is None:
            return [
                types.TextContent(
                    type="text",
                    text="radius_x 和 radius_y 至少设置一个"
                )
            ]

        if radius_x is None or len(radius_x) == 0:
            radius_x = radius_y
        elif radius_y is None or len(radius_y) == 0:
            radius_y = radius_x

        func = f"roundPic/radiusx/{radius_x}/radiusy/{radius_y}"
        object_url = utils.url_add_processing_func(object_url, func)
        return [
            types.TextContent(
                type="text",
                text=str({
                    "object_url": object_url,
                })
            )
        ]

    @staticmethod
    def image_info_tool() -> types.Tool:
        return types.Tool(
            name="ImageInfo",
            description="获取图片基本信息，图片基本信息包括图片格式、图片大小、色彩模型",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {"type": "string",
                                   "description": _OBJECT_URL_DESC},
                },
                "required": ["object_url"],
            },
        )


    def image_info(self, **kwargs) -> list[
        types.TextContent | types.ImageContent | types.EmbeddedResource]:
        object_url = kwargs.get("object_url", "")
        if object_url is None or len(object_url) == 0:
            return [
                types.TextContent(
                    type="text",
                    text="object_url is required"
                )
            ]

        func = f"imageInfo"
        object_url = utils.url_add_processing_func(object_url, func)
        return [
            types.TextContent(
                type="text",
                text=str({
                    "object_url": object_url,
                })
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
                    "persistent_id": {"type": "string",
                               "description": "执行 Fop 返回的操作 ID"},
                },
                "required": ["persistent_id"],
            },
        )

    def get_fop_status(self, **kwargs) -> list[
        types.TextContent | types.ImageContent | types.EmbeddedResource]:
        status = self.client.get_fop_status(**kwargs)
        return [
            types.TextContent(
                type="text",
                text=str(status)
            )
        ]


def register_tools(cli: Client):
    tool = _ToolImplement(cli)
    tools.register_tool(_ToolImplement.image_scale_by_percent_fop(), tool.image_scale_by_percent)
    tools.register_tool(_ToolImplement.image_scale_by_size_tool(), tool.image_scale_by_size)
    tools.register_tool(_ToolImplement.image_round_corner_tool(), tool.image_round_corner)
    tools.register_tool(_ToolImplement.image_info_tool(), tool.image_info)
