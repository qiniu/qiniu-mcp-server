import logging
from mcp import types

from . import utils
from .processing import MediaProcessingService
from ...consts import consts
from ...tools import tools

logger = logging.getLogger(consts.LOGGER_NAME)

_OBJECT_URL_DESC = "The URL of the image. This can be a URL obtained via the GetObjectURL tool or a URL generated by other Fop tools. Length Constraints: Minimum length of 1."


class _ToolImpl:
    def __init__(self, cli: MediaProcessingService):
        self.client = cli

    @tools.tool_meta(
        types.Tool(
            name="ImageScaleByPercent",
            description="""Image scaling tool that resizes images based on a percentage and returns information about the scaled image.
            The information includes the object_url of the scaled image, which users can directly use for HTTP GET requests to retrieve the image content or open in a browser to view the file.
            The image must be stored in a Qiniu Cloud Bucket.
            Supported original image formats: psd, jpeg, png, gif, webp, tiff, bmp, avif, heic. Image width and height cannot exceed 30,000 pixels, and total pixels cannot exceed 150 million.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {
                        "type": "string", 
                        "description": _OBJECT_URL_DESC
                    },
                    "percent": {
                        "type": "integer",
                        "description": "Scaling percentage, range [1,999]. For example: 90 means the image width and height are reduced to 90% of the original; 200 means the width and height are enlarged to 200% of the original.",
                        "minimum": 1,
                        "maximum": 999
                    },
                },
                "required": ["object_url", "percent"],
            },
        )
    )
    def image_scale_by_percent(
            self, **kwargs
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        object_url = kwargs.get("object_url", "")
        percent = kwargs.get("percent", "")
        if object_url is None or len(object_url) == 0:
            return [types.TextContent(type="text", text="object_url is required")]

        percent_int = int(percent)
        if percent_int < 1 or percent_int > 999:
            return [
                types.TextContent(type="text", text="percent must be between 1 and 999")
            ]

        fop = f"imageMogr2/thumbnail/!{percent}p"
        object_url = utils.url_add_processing_func(object_url, fop)
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

    @tools.tool_meta(
        types.Tool(
            name="ImageScaleBySize",
            description="""Image scaling tool that resizes images based on a specified width or height and returns information about the scaled image.
            The information includes the object_url of the scaled image, which users can directly use for HTTP GET requests to retrieve the image content or open in a browser to view the file.
            The image must be stored in a Qiniu Cloud Bucket.
            Supported original image formats: psd, jpeg, png, gif, webp, tiff, bmp, avif, heic. Image width and height cannot exceed 30,000 pixels, and total pixels cannot exceed 150 million.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {
                        "type": "string", 
                        "description": _OBJECT_URL_DESC
                    },
                    "width": {
                        "type": "integer",
                        "description": "Specifies the width for image scaling. The image will be scaled to the specified width, and the height will be adjusted proportionally.",
                        "minimum": 1
                    },
                    "height": {
                        "type": "integer",
                        "description": "Specifies the height for image scaling. The image will be scaled to the specified height, and the width will be adjusted proportionally.",
                        "minimum": 1
                    },
                },
                "required": ["object_url"],
                "anyOf": [
                    {"required": ["width"]},
                    {"required": ["height"]}
                ]
            },
        )
    )
    def image_scale_by_size(
            self, **kwargs
    ) -> list[types.TextContent]:
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
        object_url = utils.url_add_processing_func(object_url, fop)
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

    @tools.tool_meta(
        types.Tool(
            name="ImageRoundCorner",
            description="""Image rounded corner tool that processes images based on width, height, and corner radius, returning information about the processed image.
            If only radius_x or radius_y is set, the other parameter will be assigned the same value, meaning horizontal and vertical parameters will be identical.
            The information includes the object_url of the processed image, which users can directly use for HTTP GET requests to retrieve the image content or open in a browser to view the file.
            The image must be stored in a Qiniu Cloud Bucket.
            Supported original image formats: psd, jpeg, png, gif, webp, tiff, bmp, avif, heic. Image width and height cannot exceed 30,000 pixels, and total pixels cannot exceed 150 million.
            Corner radius supports pixels and percentages, but cannot be negative. Pixels are represented by numbers, e.g., 200 means 200px; percentages use !xp, e.g., !25p means 25%.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {
                        "type": "string",
                        "description": _OBJECT_URL_DESC
                    },
                    "radius_x": {
                        "type": "string",
                        "description": "Parameter for horizontal corner size. Can use: pixel values (e.g., 200 for 200px) or percentages (e.g., !25p for 25%), all non-negative values."
                    },
                    "radius_y": {
                        "type": "string",
                        "description": "Parameter for vertical corner size. Can use: pixel values (e.g., 200 for 200px) or percentages (e.g., !25p for 25%), all non-negative values."
                    },
                },
                "required": ["object_url"],
                "anyOf": [
                    {"required": ["radius_x"]},
                    {"required": ["radius_y"]}
                ]
            }
        )
    )
    def image_round_corner(self, **kwargs) -> list[types.TextContent]:
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
                    text="At least one of radius_x or radius_y must be set"
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

    @tools.tool_meta(
        types.Tool(
            name="ImageInfo",
            description="Retrieves basic image information, including image format, size, and color model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_url": {
                        "type": "string",
                        "description": _OBJECT_URL_DESC
                    },
                },
                "required": ["object_url"],
            },
        )
    )
    def image_info(self, **kwargs) -> list[types.TextContent]:
        object_url = kwargs.get("object_url", "")
        if object_url is None or len(object_url) == 0:
            return [
                types.TextContent(
                    type="text",
                    text="object_url is required"
                )
            ]

        func = "imageInfo"
        object_url = utils.url_add_processing_func(object_url, func)
        return [
            types.TextContent(
                type="text",
                text=str({
                    "object_url": object_url,
                })
            )
        ]

    @tools.tool_meta(
        types.Tool(
            name="GetFopStatus",
            description="Retrieves the execution status of a Fop operation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "persistent_id": {
                        "type": "string",
                        "description": "Operation ID returned from executing a Fop operation",
                    },
                },
                "required": ["persistent_id"],
            },
        )
    )
    def get_fop_status(self, **kwargs) -> list[types.TextContent]:
        status = self.client.get_fop_status(**kwargs)
        return [types.TextContent(type="text", text=str(status))]


def register_tools(cli: MediaProcessingService):
    tool_impl = _ToolImpl(cli)
    tools.auto_register_tools(
        [
            tool_impl.image_scale_by_percent,
            tool_impl.image_scale_by_size,
            tool_impl.image_round_corner,
            tool_impl.image_info,
        ]
    )
