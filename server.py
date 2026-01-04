"""
============================================================================
教材资源 MCP (Model Context Protocol) 服务器 - Mock 版本
============================================================================

这是一个教材出版社的 MCP 服务器 Mock 实现，提供教材资料查询功能。

可用工具：
1. metadata_discovery - 了解数据库结构、内容关系、可用过滤条件和工具集
2. semantic_search    - 在指定范围内进行自然语言语义搜索
3. search_by_criteria - 通过精确条件筛选内容

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
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

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
SERVER_NAME = "textbook-mcp-server"

# 身份验证 Token（用于测试）
# 在生产环境中，应该从环境变量或安全存储中读取
AUTH_TOKEN = "fz-test-123456"

# 不需要身份验证的路径（如健康检查）
PUBLIC_PATHS = ["/health"]


# ============================================================================
# 身份验证中间件
# ============================================================================

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Bearer Token 身份验证中间件

    检查请求头中的 Authorization 字段，验证 Bearer token 是否正确。
    对于 PUBLIC_PATHS 中的路径，跳过验证。
    """

    async def dispatch(self, request: Request, call_next):
        # 检查是否是公开路径（不需要验证）
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # 获取 Authorization header
        auth_header = request.headers.get("Authorization")

        # 验证 Authorization header 格式和 token
        if not auth_header:
            return JSONResponse(
                {"error": "Missing Authorization header"},
                status_code=401
            )

        # 检查是否是 Bearer token 格式
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Invalid Authorization header format. Expected: Bearer <token>"},
                status_code=401
            )

        # 提取并验证 token
        token = auth_header[7:]  # 去掉 "Bearer " 前缀
        if token != AUTH_TOKEN:
            return JSONResponse(
                {"error": "Invalid token"},
                status_code=401
            )

        # 验证通过，继续处理请求
        return await call_next(request)

# ============================================================================
# 教材资源元数据 (Metadata Discovery)
# ============================================================================

# 元数据发现返回的数据结构
# 这是 AI 必须首先调用的工具，用于了解数据库结构
METADATA_DISCOVERY_DATA = {
    # 内容类型定义
    "content_types": [
        {
            "type": "textbook",
            "description": "教學手冊和教材",
            "key_field": "textbook_uuid",
            "display_field": "filename"
        },
        {
            "type": "knowledge_point",
            "description": "知識點內容",
            "key_field": "uuid",
            "display_field": "knowledge_point_name"
        },
        {
            "type": "question",
            "description": "練習題目",
            "key_field": "question_id",
            "display_field": "question_title"
        }
    ],

    # 内容类型之间的关系
    "relationships": [
        {
            "from": "textbook",
            "to": "knowledge_point",
            "relation": "contains",
            "description": "教冊包含多個知識點"
        },
        {
            "from": "knowledge_point",
            "to": "question",
            "relation": "has_exercises",
            "description": "知識點衍生出多個題目"
        }
    ],

    # 可用工具列表
    "available_tools": [
        {
            "name": "metadata_discovery",
            "description": "了解數據庫結構、內容關係、可用過濾條件和工具集",
            "usage_scenarios": ["首次連接時調用", "了解系統能力", "查詢可用過濾條件"]
        },
        {
            "name": "semantic_search",
            "description": "在指定範圍內進行自然語言語義搜索",
            "usage_scenarios": ["查找相關知識點", "搜索教學內容", "尋找練習題目"]
        },
        {
            "name": "search_by_criteria",
            "description": "通過精確條件篩選內容",
            "usage_scenarios": ["按年級篩選", "按難度篩選", "按科目篩選", "按題型篩選"]
        }
    ],

    # 可用的过滤条件
    "available_filters": {
        "question": {
            "difficulty": {
                "type": "enum",
                "values": ["易", "中", "難", "競賽"],
                "description": "題目難易度",
                "required": False
            },
            "question_type": {
                "type": "enum",
                "values": ["選擇題", "填空題", "問答題", "看圖回答"],
                "description": "題型分類",
                "required": False
            },
            "grade": {
                "type": "enum",
                "values": ["七年級", "八年級", "九年級"],
                "description": "適用年級",
                "required": False
            },
            "subject": {
                "type": "enum",
                "values": ["英語", "數學", "國文", "自然", "社會"],
                "description": "科目",
                "required": False
            },
            "knowledge_point_code": {
                "type": "string",
                "pattern": "^[A-Z]{3}\\d{12}$",
                "description": "知識點代碼（如 JEN000000000001）",
                "required": False
            }
        },
        "knowledge_point": {
            "grade": {
                "type": "enum",
                "values": ["七年級", "八年級", "九年級"],
                "description": "適用年級",
                "required": False
            },
            "subject": {
                "type": "enum",
                "values": ["英語", "數學", "國文", "自然", "社會"],
                "description": "科目",
                "required": False
            },
            "chapter": {
                "type": "string",
                "description": "章節編號",
                "required": False
            },
            "textbook_uuid": {
                "type": "string",
                "description": "所屬教冊的UUID",
                "required": False
            }
        },
        "textbook": {
            "grade": {
                "type": "enum",
                "values": ["七年級", "八年級", "九年級"],
                "description": "適用年級",
                "required": False
            },
            "subject": {
                "type": "enum",
                "values": ["英語", "數學", "國文", "自然", "社會"],
                "description": "科目",
                "required": False
            },
            "semester": {
                "type": "enum",
                "values": ["上學期", "下學期"],
                "description": "學期",
                "required": False
            },
            "publisher": {
                "type": "enum",
                "values": ["康軒", "南一", "翰林"],
                "description": "出版社",
                "required": False
            }
        }
    },

    # 系统限制
    "limitations": {
        "max_results_per_query": 50,
        "max_concurrent_queries": 5,
        "rate_limit": "100 requests per minute",
        "query_timeout_ms": 10000
    },

    # 使用示例和典型工作流程
    "examples": {
        "typical_workflows": [
            {
                "scenario": "學生詢問知識點",
                "steps": [
                    "1. 調用 metadata_discovery 了解系統結構",
                    "2. 使用 semantic_search 查找相關知識點",
                    "3. 使用 search_by_criteria 獲取相關題目練習"
                ]
            },
            {
                "scenario": "教師查找特定難度題目",
                "steps": [
                    "1. 調用 metadata_discovery 了解可用過濾條件",
                    "2. 使用 search_by_criteria 按難度和年級篩選題目"
                ]
            },
            {
                "scenario": "根據教材查找練習題",
                "steps": [
                    "1. 使用 semantic_search 或 search_by_criteria 查找教冊",
                    "2. 獲取教冊下的知識點列表",
                    "3. 使用 search_by_criteria 按知識點代碼查找相關題目"
                ]
            }
        ]
    }
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

# 使用 @mcp.tool() 装饰器注册工具
#
# 工具(Tool)是 MCP 的核心概念之一，它允许 AI 模型调用外部功能
#
# 装饰器会自动：
# 1. 从函数签名推断参数类型
# 2. 从 docstring 提取工具描述
# 3. 注册工具到 MCP 服务器

@mcp.tool()
def metadata_discovery() -> dict:
    """
    獲取教材資源系統的元數據信息。

    這是 AI 必須首先調用的工具，用於了解：
    - 數據庫結構和內容類型
    - 內容之間的關係
    - 可用的過濾條件
    - 可用的工具列表
    - 系統限制
    - 典型使用流程示例

    返回值:
        dict: 包含 success 狀態和完整元數據的字典

    使用示例:
        # 首次連接時調用，了解系統結構
        metadata_discovery()
    """
    return {
        "success": True,
        "data": METADATA_DISCOVERY_DATA
    }


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
        "description": "教材資源 MCP 服務器，提供教材、知識點、練習題目的查詢功能",
        "endpoints": {
            "/": "服务器信息（当前页面）",
            "/sse": "SSE 连接端点 (GET) - 建立 MCP 连接",
            "/messages": "消息端点 (POST) - 发送 MCP 消息",
            "/health": "健康检查端点 (GET)"
        },
        "tools": [
            {
                "name": "metadata_discovery",
                "description": "獲取數據庫結構、內容關係、可用過濾條件和工具集（AI 必須首先調用）",
                "parameters": None
            },
            {
                "name": "semantic_search",
                "description": "在指定範圍內進行自然語言語義搜索（待實現）",
                "parameters": "query, content_type, filters"
            },
            {
                "name": "search_by_criteria",
                "description": "通過精確條件篩選內容（待實現）",
                "parameters": "content_type, filters"
            }
        ],
        "usage": {
            "step1": "使用 GET /sse 建立 SSE 连接",
            "step2": "从 SSE 事件中获取 endpoint URL",
            "step3": "首先調用 metadata_discovery 了解系統結構",
            "step4": "使用 semantic_search 或 search_by_criteria 查詢內容"
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
    routes=custom_routes + mcp_app.routes,  # 合并自定义路由和 MCP 路由
    middleware=[
        Middleware(AuthMiddleware)  # 添加身份验证中间件
    ]
)


# ============================================================================
# 启动服务器
# ============================================================================

if __name__ == "__main__":
    # 打印启动信息
    print("=" * 60)
    print("📚 教材資源 MCP 服務器已啟動！")
    print("=" * 60)
    print(f"📡 服务器地址: http://localhost:{PORT}")
    print(f"🔗 SSE 端点:   http://localhost:{PORT}/sse")
    print(f"📨 消息端点:   http://localhost:{PORT}/messages")
    print(f"❤️  健康检查:   http://localhost:{PORT}/health")
    print("=" * 60)
    print("🔐 身份验证: 需要在请求头中添加")
    print(f"   Authorization: Bearer {AUTH_TOKEN}")
    print("   (健康检查端点不需要验证)")
    print("=" * 60)
    print("可用的 MCP 工具:")
    print("  - metadata_discovery: 獲取系統元數據（AI 必須首先調用）")
    print("  - semantic_search:    語義搜索（待實現）")
    print("  - search_by_criteria: 條件篩選（待實現）")
    print("=" * 60)

    # 使用 uvicorn 启动 ASGI 服务器
    # 参数说明：
    # - app: Starlette 应用实例
    # - host: 监听地址，"0.0.0.0" 表示接受所有网络接口的连接
    # - port: 监听端口
    uvicorn.run(app, host="0.0.0.0", port=PORT)
