"""
============================================================================
简单的 MCP (Model Context Protocol) 服务器示例 - Python 版本
============================================================================

什么是 MCP？
MCP (Model Context Protocol) 是由 Anthropic 开发的一个开放协议，
用于让 AI 模型（如 Claude）与外部工具、数据源进行标准化交互。

MCP 的核心概念：
1. Tools (工具)     - 可以被 AI 调用的函数，类似于 API 接口
2. Resources (资源) - 可以被读取的数据源，如文件、数据库等
3. Prompts (提示)   - 预定义的提示模板

本示例实现了一个简单的 Tool，返回"超人"的基本信息。

传输方式：
MCP 支持多种传输方式：stdio、HTTP+SSE 等
本示例使用 HTTP + SSE (Server-Sent Events) 方式

运行方式：
    python server.py

============================================================================
"""

# ============================================================================
# 导入依赖模块
# ============================================================================

# Starlette - 轻量级 ASGI 框架（FastAPI 的底层框架）
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# MCP SDK - 提供 MCP 协议的核心实现
from mcp.server.fastmcp import FastMCP

# uvicorn - ASGI 服务器，用于运行 Starlette/FastAPI 应用
import uvicorn

# 类型注解支持
from typing import Literal

# 日期时间
from datetime import datetime

# 环境变量
import os

# ============================================================================
# 配置常量
# ============================================================================

# 服务器监听端口（支持 Cloud Run 的 PORT 环境变量）
PORT = int(os.environ.get("PORT", 3000))

# 服务器名称（会在 MCP 握手时发送给客户端）
SERVER_NAME = "superman-mcp-server"

# ============================================================================
# 超人的基本信息数据
# ============================================================================

# 超人的详细信息字典
# 在实际应用中，这些数据可能来自数据库或外部 API
SUPERMAN_INFO = {
    # 基本身份信息
    "name": "Superman",                           # 超级英雄名称
    "realName": "Clark Kent",                     # 真实姓名
    "alias": "Kal-El",                           # 氪星名字

    # 出版信息
    "publisher": "DC Comics",                     # 出版商
    "firstAppearance": "Action Comics #1 (1938)", # 首次登场
    "creators": ["Jerry Siegel", "Joe Shuster"],  # 创作者

    # 外貌特征
    "appearance": {
        "height": "6'3\" (191 cm)",               # 身高
        "weight": "235 lbs (107 kg)",             # 体重
        "eyeColor": "Blue",                       # 眼睛颜色
        "hairColor": "Black"                      # 头发颜色
    },

    # 超能力列表
    "powers": [
        "Super strength (超级力量)",
        "Flight (飞行)",
        "Invulnerability (刀枪不入)",
        "Super speed (超级速度)",
        "Heat vision (热视线)",
        "Freeze breath (冰冻呼吸)",
        "X-ray vision (透视眼)",
        "Super hearing (超级听力)",
        "Super stamina (超级耐力)"
    ],

    # 弱点
    "weaknesses": [
        "Kryptonite (氪石)",
        "Magic (魔法)",
        "Red sun radiation (红太阳辐射)"
    ],

    # 背景故事
    "origin": (
        "来自氪星(Krypton)的外星人，在氪星毁灭前被父母送往地球。"
        "在地球上被堪萨斯州的肯特夫妇收养，以Clark Kent的身份长大。"
        "地球的黄色太阳赋予了他超凡的能力，他决定用这些能力保护人类。"
    ),

    # 关联角色
    "associates": {
        "loveInterest": "Lois Lane",              # 爱人
        "bestFriend": "Batman",                   # 挚友
        "team": "Justice League"                  # 所属团队
    },

    # 著名口号
    "motto": "Truth, Justice, and a Better Tomorrow (真理、正义与更美好的明天)"
}


# ============================================================================
# 创建 MCP 服务器实例
# ============================================================================

# FastMCP 是 MCP Python SDK 提供的便捷类
# 它简化了 MCP 服务器的创建过程，内置了 HTTP/SSE 支持
#
# 参数说明：
# - name: 服务器名称，用于标识这个 MCP 服务器
# - host: 设置为 "0.0.0.0" 禁用默认的 DNS rebinding protection
#         （默认 "127.0.0.1" 会限制只允许 localhost 相关的 Host header）
mcp = FastMCP(SERVER_NAME, host="0.0.0.0")


# ============================================================================
# 注册 MCP Tool (工具)
# ============================================================================

# 使用 @mcp.tool() 装饰器注册一个工具
#
# 工具(Tool)是 MCP 的核心概念之一，它允许 AI 模型调用外部功能
# 当 AI 需要获取超人信息时，它可以调用这个工具
#
# 装饰器会自动：
# 1. 从函数签名推断参数类型
# 2. 从 docstring 提取工具描述
# 3. 注册工具到 MCP 服务器

@mcp.tool()
def get_superman_info(
    category: Literal["all", "basic", "powers", "origin", "weaknesses"] = "all"
) -> dict:
    """
    获取超人(Superman)的详细信息，包括真实身份、超能力、弱点、背景故事等。

    这是一个 MCP Tool，可以被 AI 模型调用来获取超人的各类信息。

    参数说明:
        category: 要获取的信息类别
            - "all": 返回全部信息（默认值）
            - "basic": 返回基本身份信息（姓名、外貌、关联角色等）
            - "powers": 返回超能力列表
            - "origin": 返回起源故事
            - "weaknesses": 返回弱点信息

    返回值:
        dict: 包含请求类别信息的字典

    使用示例:
        # 获取全部信息
        get_superman_info()

        # 只获取超能力
        get_superman_info(category="powers")
    """

    # 根据请求的类别返回不同的信息
    if category == "basic":
        # 只返回基本身份信息
        return {
            "name": SUPERMAN_INFO["name"],
            "realName": SUPERMAN_INFO["realName"],
            "alias": SUPERMAN_INFO["alias"],
            "publisher": SUPERMAN_INFO["publisher"],
            "firstAppearance": SUPERMAN_INFO["firstAppearance"],
            "creators": SUPERMAN_INFO["creators"],
            "appearance": SUPERMAN_INFO["appearance"],
            "associates": SUPERMAN_INFO["associates"],
            "motto": SUPERMAN_INFO["motto"]
        }

    elif category == "powers":
        # 只返回超能力列表
        return {
            "name": SUPERMAN_INFO["name"],
            "powers": SUPERMAN_INFO["powers"]
        }

    elif category == "origin":
        # 只返回起源故事
        return {
            "name": SUPERMAN_INFO["name"],
            "alias": SUPERMAN_INFO["alias"],
            "origin": SUPERMAN_INFO["origin"]
        }

    elif category == "weaknesses":
        # 只返回弱点信息
        return {
            "name": SUPERMAN_INFO["name"],
            "weaknesses": SUPERMAN_INFO["weaknesses"]
        }

    else:  # category == "all" 或其他情况
        # 返回全部信息
        return SUPERMAN_INFO


# ============================================================================
# 自定义 HTTP 端点处理函数
# ============================================================================

async def root(request):
    """
    根路径 - 显示服务器基本信息和使用说明

    这个端点提供了服务器的概览信息，帮助用户了解如何使用此 MCP 服务器
    """
    return JSONResponse({
        "name": SERVER_NAME,
        "version": "1.0.0",
        "description": "这是一个简单的 MCP 服务器示例，提供超人信息查询功能",
        "endpoints": {
            "/": "服务器信息（当前页面）",
            "/sse": "SSE 连接端点 (GET) - 建立 MCP 连接",
            "/messages": "消息端点 (POST) - 发送 MCP 消息",
            "/health": "健康检查端点 (GET)"
        },
        "tool": {
            "name": "get_superman_info",
            "description": "获取超人的详细信息",
            "parameters": {
                "category": {
                    "type": "string",
                    "options": ["all", "basic", "powers", "origin", "weaknesses"],
                    "default": "all"
                }
            }
        },
        "usage": {
            "step1": "使用 GET /sse 建立 SSE 连接",
            "step2": "从 SSE 事件中获取 endpoint URL",
            "step3": "使用 POST /messages 发送 MCP 消息"
        }
    })


async def health_check(request):
    """
    健康检查端点

    用于检查服务器是否正常运行
    这是一个常见的最佳实践，方便监控和负载均衡器使用
    """
    return JSONResponse({
        "status": "ok",
        "server": SERVER_NAME,
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


# ============================================================================
# 创建 Starlette 应用并集成 MCP
# ============================================================================

# 获取 FastMCP 内置的 SSE 应用
# mcp.sse_app() 返回一个配置好 MCP SSE 传输的 Starlette 应用
# 它自动处理 /sse 和 /messages 端点
mcp_app = mcp.sse_app()

# 定义自定义路由
# 这些路由提供额外的 HTTP 端点，用于服务器信息和健康检查
custom_routes = [
    Route("/", root),           # 根路径 - 服务器信息
    Route("/health", health_check),  # 健康检查端点
]

# 创建主应用
# 将自定义路由添加到 MCP 应用的路由列表中
# 这样可以在同一个服务器上同时提供 MCP 功能和自定义 HTTP 端点
app = Starlette(
    routes=custom_routes + mcp_app.routes  # 合并自定义路由和 MCP 路由
)


# ============================================================================
# 启动服务器
# ============================================================================

if __name__ == "__main__":
    # 打印启动信息
    print("=" * 60)
    print("🦸 超人 MCP 服务器已启动！")
    print("=" * 60)
    print(f"📡 服务器地址: http://localhost:{PORT}")
    print(f"🔗 SSE 端点:   http://localhost:{PORT}/sse")
    print(f"📨 消息端点:   http://localhost:{PORT}/messages")
    print(f"❤️  健康检查:   http://localhost:{PORT}/health")
    print("=" * 60)
    print("可用的 MCP 工具:")
    print("  - get_superman_info: 获取超人的详细信息")
    print("    参数 category: all | basic | powers | origin | weaknesses")
    print("=" * 60)

    # 使用 uvicorn 启动 ASGI 服务器
    # 参数说明：
    # - app: Starlette 应用实例
    # - host: 监听地址，"0.0.0.0" 表示接受所有网络接口的连接
    # - port: 监听端口
    uvicorn.run(app, host="0.0.0.0", port=PORT)
