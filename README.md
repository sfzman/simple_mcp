# Simple MCP Server - 超人信息服务 (Python 版)

一个简单的 MCP (Model Context Protocol) 服务器示例，用于学习和测试 MCP 协议。

## 什么是 MCP？

MCP (Model Context Protocol) 是由 Anthropic 开发的开放协议，用于让 AI 模型与外部工具和数据源进行标准化交互。

## 功能

本服务器提供一个 MCP Tool：`get_superman_info`，用于获取超人（Superman）的详细信息。

### 可查询的信息类别

| 类别 | 说明 |
|------|------|
| `all` | 返回全部信息（默认） |
| `basic` | 基本身份信息 |
| `powers` | 超能力列表 |
| `origin` | 起源故事 |
| `weaknesses` | 弱点信息 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python server.py
```

服务器将在 `http://localhost:3000` 启动。

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务器信息和使用说明 |
| `/sse` | GET | 建立 SSE 连接（MCP 入口） |
| `/messages` | POST | 发送 MCP 消息 |
| `/health` | GET | 健康检查 |

## 使用示例

### 1. 检查服务器状态

```bash
curl http://localhost:3000/health
```

### 2. 查看服务器信息

```bash
curl http://localhost:3000/
```

## 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "superman": {
      "command": "python",
      "args": ["/path/to/simple_mcp/server.py"]
    }
  }
}
```

## 项目结构

```
simple_mcp/
├── requirements.txt  # Python 依赖配置
├── server.py         # MCP 服务器主文件（含详细注释）
└── README.md         # 本说明文件
```

## 技术栈

- **Python 3.8+** - 编程语言
- **FastAPI** - Web 框架
- **uvicorn** - ASGI 服务器
- **mcp** - MCP 官方 Python SDK

## 代码结构说明

`server.py` 中包含详细的中文注释，解释了：

1. **MCP 基本概念** - Tools、Resources、Prompts 的作用
2. **FastMCP 使用** - 如何使用装饰器注册工具
3. **SSE 传输机制** - HTTP + Server-Sent Events 通信方式
4. **工具实现** - 如何定义参数和返回值

## 学习资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

## License

MIT
