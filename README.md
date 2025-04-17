# Qiniu MCP Server

## 概述

基于七牛云产品构建的 Model Context Protocol (MCP) Server，支持用户在 AI 大模型客户端的上下文中通过该 MCP
Server 来访问七牛云存储、智能多媒体服务等。

关于访问七牛云存储详细情况请参考 [基于 MCP 使用大模型访问七牛云存储](https://developer.qiniu.com/kodo/12914/mcp-aimodel-kodo)。

## 环境要求

- Python 3.12 或更高版本
- uv 包管理器

如果还没有安装 uv，可以使用以下命令安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 在 Cline 中使用：

步骤：

1. 在 vscode 下载 Cline 插件（下载后 Cline 插件后在侧边栏会增加 Cline 的图标）
2. 配置大模型
3. 配置 qiniu MCP
    1. 点击 Cline 图标进入 Cline 插件，选择 MCP Server 模块
    2. 选择 installed，点击 Advanced MCP Settings 配置 MCP Server，参考下面配置信息
   ```
   {
     "mcpServers": {
       "qiniu": {
         "command": "uvx",
         "args": [
           "qiniu-mcp-server"
         ],
         "env": {
           "QINIU_ACCESS_KEY": "YOUR_ACCESS_KEY",
           "QINIU_SECRET_KEY": "YOUR_SECRET_KEY",
           "QINIU_REGION_NAME": "YOUR_REGION_NAME",
           "QINIU_ENDPOINT_URL": "YOUR_ENDPOINT_URL",
           "QINIU_BUCKETS": "YOUR_BUCKET_A,YOUR_BUCKET_B"
        },
         "disabled": false
       }
     }
   }
   ```
    3. 点击 qiniu MCP Server 的链接开关进行连接
4. 在 Cline 中创建一个聊天窗口，此时我们可以和 AI 进行交互来使用 qiniu-mcp-server ，下面给出几个示例：
    - 列举 qiniu 的资源信息
    - 列举 qiniu 中所有的 Bucket
    - 列举 qiniu 中 xxx Bucket 的文件
    - 读取 qiniu xxx Bucket 中 yyy 的文件内容
    - 对 qiniu xxx Bucket 中 yyy 的图片切个宽200像素的圆角
    - 刷新下 qiniu 的这个 CDN 链接：https://developer.qiniu.com/test.txt

注：
cursor 中创建 MCP Server 可直接使用上述配置。

## 开发
1. 克隆仓库：

```bash
# 克隆项目并进入目录
git clone git@github.com:qiniu/qiniu-mcp-server.git
cd qiniu-mcp-server
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

4. 配置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：
```bash
# S3/Kodo 认证信息
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key

# 区域信息
QINIU_REGION_NAME=your_region
QINIU_ENDPOINT_URL=endpoint_url # eg:https://s3.your_region.qiniucs.com

# 配置 bucket，多个 bucket 使用逗号隔开，建议最多配置 20 个 bucket
QINIU_BUCKETS=bucket1,bucket2,bucket3
```

扩展功能，首先在 core 目录下新增一个业务包目录（eg: 存储 -> storage），在此业务包目录下完成功能拓展。
在业务包目录下的 `__init__.py` 文件中定义 load 函数用于注册业务工具或者资源，最后在 `core` 目录下的 `__init__.py`
中调用此 load 函数完成工具或资源的注册。

```shell
core
├── __init__.py # 各个业务工具或者资源加载
└── storage # 存储业务目录
    ├── __init__.py # 加载存储工具或者资源
    ├── resource.py # 存储资源扩展
    ├── storage.py # 存储工具类
    └── tools.py # 存储工具扩展
```

## 测试

### 使用 Model Control Protocol Inspector 测试

强烈推荐使用 [Model Control Protocol Inspector](https://github.com/modelcontextprotocol/inspector) 进行测试。

```shell
# node 版本为：v22.4.0
npx @modelcontextprotocol/inspector uv --directory . run qiniu-mcp-server
```

### 本地启动 MCP Server 示例

1. 使用标准输入输出（stdio）模式启动（默认）：

```bash
uv --directory . run qiniu-mcp-server
```

2. 使用 SSE 模式启动（用于 Web 应用）：

```bash
uv --directory . run qiniu-mcp-server --transport sse --port 8000
```




