# Qiniu MCP Server

一个基于 MCP (Model Control Protocol) 的 S3 资源服务器，支持访问和管理七牛云 Kodo 存储服务。

## 功能特性

- 支持列举存储桶（Buckets）
- 支持列举对象（Objects）
- 支持读取对象内容

## 前置要求

- Python 3.12 或更高版本
- uv 包管理器

如果还没有安装 uv，可以使用以下命令安装：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 安装

1. 克隆仓库：
```bash
# 克隆项目并进入目录
git clone git@github.com:qiniu/mcp-server.git
cd qiniu-mcp
```

2. 创建并激活虚拟环境：
```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
uv pip install -e .
```

## 配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置以下参数：
```bash
# S3/Kodo 认证信息
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
# 区域信息
QINIU_REGION_NAME=your_region
QINIU_ENDPOINT_URL=endpoint_url # eg:https://s3.your_region.qiniucs.com
# 配置 bucket，多个 bucket 使用逗号隔开
QINIU_BUCKETS=bucket1,bucket2,bucket3
```

## 使用方法

### 启动服务器

1. 使用标准输入输出（stdio）模式启动（默认）：
```bash
uv --directory . run qiniu-mcp-server
```

2. 使用 SSE 模式启动（用于 Web 应用）：
```bash
uv --directory . run qiniu-mcp-server --transport sse --port 8000
```

### 可用工具

服务器提供以下工具：

1. **ListBuckets**
   - 列举所有可用的存储桶
   - 参数：
     - `prefix`：（可选）存储桶名称前缀

2. **ListObjectsV2**
   - 列举存储桶中的对象
   - 参数：
     - `bucket`：（必需）存储桶名称
     - `prefix`：（可选）对象键前缀
     - `max_keys`：（可选）返回的最大对象数量
     - `start_after`：（可选）从指定键名之后开始列举

3. **GetObject**
   - 获取对象内容
   - 参数：
     - `bucket`：（必需）存储桶名称
     - `key`：（必需）对象键名

## 返回数据结构

服务器根据内容类型返回不同的数据结构：

1. **TextContent**
   - 用于文本类型文件
   - 结构：
     ```
     {
       "type": "text",
       "text": "文本内容"
     }
     ```

2. **ImageContent**
   - 用于图片类型文件
   - 结构：
     ```
     {
       "type": "image",
       "data": "base64编码的图片数据",
       "mimeType": "图片的MIME类型，如image/png"
     }
     ```

## 支持的文件类型

服务器支持以下文件类型的处理：

1. 文本文件
   - Markdown 文件（text/markdown）
   - 纯文本文件（text/plain）
   - 其他文本格式

2. 图片文件
   - 所有标准图片格式（image/*）
   - 自动处理为 Base64 编码

## 测试
强烈推荐使用 [Model Control Protocol Inspector](https://github.com/modelcontextprotocol/inspector) 进行测试。
```shell
# node 版本为：v22.4.0
npx @modelcontextprotocol/inspector uv --directory . run qiniu-mcp-server
```


