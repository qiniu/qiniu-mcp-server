# 七牛云 MCP 服务器

基于七牛云产品构建的 Model Context Protocol (MCP) 服务器，支持在 AI 大模型的上下文中直接访问和操作七牛云的服务。

## Keywords
七牛, Dora, Kodo, CDN

## Tools

### 存储工具

1. `ListBuckets`
   - 查询当前用户配置的 Bucket 
   - Inputs:
     - `prefix` (string, optional): Bucket 名称前缀，用于筛选特定前缀的 Bucket 
   - Returns:
     - 满足条件的 Bucket 列表及其详细信息

2. `ListObjects`
   - 列举指定 Bucket 中的文件列表
   - Inputs:
     - `bucket` (string): Bucket 名称
     - `max_keys` (integer, optional): 单次返回的最大文件数量，默认为20，最大值为100
     - `prefix` (string, optional): 文件 Key 前缀，用于筛选特定前缀的文件
     - `start_after` (string, optional): 起始标记，指定列表的开始位置，可以是上一次列举的结果中最后一个文件的 Key
   - Returns:
     - 满足条件的文件列表及其详细信息

3. `GetObject`
   - 获取 Bucket 中文件的内容
   - Inputs:
     - `bucket` (string):  Bucket 名称
     - `key` (string): 文件的 Key
   - Returns:
     - 文件内容

4. `GetObjectURL`
   - 生成文件的访问链接，注意文件存储的 Bucket 必须绑定域名，七牛云测试域名不支持 HTTPS，需要用户自己处理为 HTTP。
   - Inputs:
     - `bucket` (string):  Bucket 名称
     - `key` (string): 文件的 Key
     - `disable_ssl` (boolean, optional): 是否禁用 HTTPS，默认使用 HTTPS
     - `expires` (integer, optional): 链接有效期，单位为秒
   - Returns:
     - 对象的访问链接

### 图片处理工具

1. `ImageScaleByPercent`
   - 按照指定百分比缩放图片
   - Inputs:
     - `object_url` (string): 待处理图片的访问链接，图片必须存储在七牛云空间中
     - `percent` (integer): 缩放比例，范围为1%~999%
   - Returns:
     - `object_url`: 处理后图片的访问链接

2. `ImageScaleBySize`
   - 按照指定宽度或高度缩放图片
   - Inputs:
     - `object_url` (string): 待处理图片的访问链接，图片必须存储在七牛云空间中
     - `width` (integer, optional): 目标宽度，单位为像素
     - `height` (integer, optional): 目标高度，单位为像素
   - 注意：至少需要指定宽度或高度中的一个参数
   - Returns:
     - `object_url`: 处理后图片的访问链接

3. `ImageRoundCorner`
   - 为图片添加圆角效果
   - Inputs:
     - `object_url` (string): 待处理图片的访问链接，图片必须存储在七牛云空间中
     - `radius_x` (string, optional): 水平方向圆角半径，可使用像素值或百分比
     - `radius_y` (string, optional): 垂直方向圆角半径，可使用像素值或百分比
   - 注意：如果只指定一个参数，另一个参数将自动使用相同的值
   - Returns:
     - `object_url`: 处理后图片的访问链接

4. `ImageInfo`
   - 获取图片的基本信息
   - Inputs:
     - `object_url` (string): 图片的访问链接，图片必须存储在七牛云空间中
   - Returns:
     - `size`: 图片大小，单位为字节
     - `width`: 图片的宽度，单位为像素
     - `height`: 图片的高度，单位为像素
     - `format`: 图片的格式，如 png 等
     - `color_model`: 图片的颜色模型，如 nrgba

### CDN 工具

1. `CDNPrefetchUrls`
   - 预先将指定资源缓存到CDN节点，提高用户访问速度
   - Inputs:
     - `urls` (Array of string): 待预取资源的URL列表，最多支持60个URL
   - Returns:
     - 操作状态信息

2. `CDNRefresh`
   - 刷新CDN节点上的缓存资源，确保内容更新
   - Inputs:
     - `urls` (Array of string, optional): 需要刷新的具体URL列表，最多支持60个URL
     - `dirs` (Array of string, optional): 需要刷新的目录列表，最多支持10个目录
   - 注意：必须提供`urls`或`dirs`中的至少一项
   - Returns:
     - 操作状态信息

### 其他工具

1. `Version`
   - 获取七牛 MCP Server 的版本信息
   - Inputs: 无
   - Returns:
     - 服务器版本信息




