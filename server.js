/**
 * ============================================================================
 * 简单的 MCP (Model Context Protocol) 服务器示例
 * ============================================================================
 *
 * 什么是 MCP？
 * MCP (Model Context Protocol) 是由 Anthropic 开发的一个开放协议，
 * 用于让 AI 模型（如 Claude）与外部工具、数据源进行标准化交互。
 *
 * MCP 的核心概念：
 * 1. Tools (工具)     - 可以被 AI 调用的函数，类似于 API 接口
 * 2. Resources (资源) - 可以被读取的数据源，如文件、数据库等
 * 3. Prompts (提示)   - 预定义的提示模板
 *
 * 本示例实现了一个简单的 Tool，返回"超人"的基本信息。
 *
 * 传输方式：
 * MCP 支持多种传输方式：stdio、HTTP+SSE 等
 * 本示例使用 HTTP + SSE (Server-Sent Events) 方式
 * ============================================================================
 */

// ============================================================================
// 导入依赖模块
// ============================================================================

// MCP SDK - 提供 MCP 协议的核心实现
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

// SSE 服务器传输层 - 用于通过 HTTP+SSE 与客户端通信
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

// Express - 流行的 Node.js Web 框架，用于创建 HTTP 服务器
import express from 'express';

// ============================================================================
// 配置常量
// ============================================================================

// 服务器监听端口
const PORT = 3000;

// 服务器名称和版本（会在 MCP 握手时发送给客户端）
const SERVER_NAME = 'superman-mcp-server';
const SERVER_VERSION = '1.0.0';

// ============================================================================
// 超人的基本信息数据
// ============================================================================

/**
 * 超人的详细信息对象
 * 在实际应用中，这些数据可能来自数据库或外部 API
 */
const supermanInfo = {
  // 基本身份信息
  name: 'Superman',                           // 超级英雄名称
  realName: 'Clark Kent',                     // 真实姓名
  alias: 'Kal-El',                           // 氪星名字

  // 出版信息
  publisher: 'DC Comics',                     // 出版商
  firstAppearance: 'Action Comics #1 (1938)', // 首次登场
  creators: ['Jerry Siegel', 'Joe Shuster'],  // 创作者

  // 外貌特征
  appearance: {
    height: '6\'3" (191 cm)',                 // 身高
    weight: '235 lbs (107 kg)',               // 体重
    eyeColor: 'Blue',                         // 眼睛颜色
    hairColor: 'Black'                        // 头发颜色
  },

  // 超能力列表
  powers: [
    'Super strength (超级力量)',
    'Flight (飞行)',
    'Invulnerability (刀枪不入)',
    'Super speed (超级速度)',
    'Heat vision (热视线)',
    'Freeze breath (冰冻呼吸)',
    'X-ray vision (透视眼)',
    'Super hearing (超级听力)',
    'Super stamina (超级耐力)'
  ],

  // 弱点
  weaknesses: [
    'Kryptonite (氪石)',
    'Magic (魔法)',
    'Red sun radiation (红太阳辐射)'
  ],

  // 背景故事
  origin: '来自氪星(Krypton)的外星人，在氪星毁灭前被父母送往地球。' +
          '在地球上被堪萨斯州的肯特夫妇收养，以Clark Kent的身份长大。' +
          '地球的黄色太阳赋予了他超凡的能力，他决定用这些能力保护人类。',

  // 关联角色
  associates: {
    loveInterest: 'Lois Lane',                // 爱人
    bestFriend: 'Batman',                     // 挚友
    team: 'Justice League'                    // 所属团队
  },

  // 著名口号
  motto: 'Truth, Justice, and a Better Tomorrow (真理、正义与更美好的明天)'
};

// ============================================================================
// 创建 MCP 服务器实例
// ============================================================================

/**
 * McpServer 是 MCP SDK 提供的核心类
 * 它负责处理 MCP 协议的所有通信细节
 *
 * 构造参数：
 * - name: 服务器名称，用于标识这个 MCP 服务器
 * - version: 服务器版本号
 */
const mcpServer = new McpServer({
  name: SERVER_NAME,
  version: SERVER_VERSION
});

// ============================================================================
// 注册 MCP Tool (工具)
// ============================================================================

/**
 * 使用 mcpServer.tool() 方法注册一个工具
 *
 * 工具(Tool)是 MCP 的核心概念之一，它允许 AI 模型调用外部功能
 * 当 AI 需要获取超人信息时，它可以调用这个工具
 *
 * 参数说明：
 * @param {string} name - 工具名称，AI 模型通过这个名称调用工具
 * @param {string} description - 工具描述，帮助 AI 理解何时使用此工具
 * @param {object} inputSchema - 输入参数的 JSON Schema 定义
 * @param {function} handler - 工具的处理函数，执行实际逻辑
 */
mcpServer.tool(
  // 工具名称 - AI 会通过这个名称来调用此工具
  'get_superman_info',

  // 工具描述 - 详细说明这个工具的功能，帮助 AI 决定何时使用它
  '获取超人(Superman)的详细信息，包括真实身份、超能力、弱点、背景故事等',

  // 输入参数的 JSON Schema
  // 这里定义了工具接受哪些参数
  {
    // 使用 JSON Schema 规范定义参数
    type: 'object',
    properties: {
      // category 参数：指定要获取的信息类别
      category: {
        type: 'string',
        // enum 限制只能是这些值之一
        enum: ['all', 'basic', 'powers', 'origin', 'weaknesses'],
        // 参数描述，帮助 AI 理解如何使用此参数
        description: '要获取的信息类别：all(全部)、basic(基本信息)、powers(超能力)、origin(起源故事)、weaknesses(弱点)'
      }
    },
    // 必填参数列表（这里 category 是可选的，所以 required 为空数组）
    required: []
  },

  // 工具处理函数 - 当工具被调用时执行的逻辑
  // params 包含调用时传入的参数
  async (params) => {
    // 获取 category 参数，默认为 'all'
    const category = params.category || 'all';

    // 用于存储返回结果的变量
    let result;

    // 根据请求的类别返回不同的信息
    switch (category) {
      case 'basic':
        // 只返回基本身份信息
        result = {
          name: supermanInfo.name,
          realName: supermanInfo.realName,
          alias: supermanInfo.alias,
          publisher: supermanInfo.publisher,
          firstAppearance: supermanInfo.firstAppearance,
          creators: supermanInfo.creators,
          appearance: supermanInfo.appearance,
          associates: supermanInfo.associates,
          motto: supermanInfo.motto
        };
        break;

      case 'powers':
        // 只返回超能力列表
        result = {
          name: supermanInfo.name,
          powers: supermanInfo.powers
        };
        break;

      case 'origin':
        // 只返回起源故事
        result = {
          name: supermanInfo.name,
          alias: supermanInfo.alias,
          origin: supermanInfo.origin
        };
        break;

      case 'weaknesses':
        // 只返回弱点信息
        result = {
          name: supermanInfo.name,
          weaknesses: supermanInfo.weaknesses
        };
        break;

      case 'all':
      default:
        // 返回全部信息
        result = supermanInfo;
        break;
    }

    // 返回结果
    // MCP 工具的返回格式要求包含 content 数组
    // 每个 content 项包含 type 和对应的数据
    return {
      content: [
        {
          // type: 'text' 表示返回文本内容
          type: 'text',
          // 将结果对象转换为格式化的 JSON 字符串
          // null, 2 参数使输出更易读（缩进2空格）
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
);

// ============================================================================
// 创建 Express HTTP 服务器
// ============================================================================

/**
 * Express 应用实例
 * 用于处理 HTTP 请求，提供 MCP 协议的 HTTP 传输层
 */
const app = express();

// 解析 JSON 请求体
// 这是处理 POST 请求中 JSON 数据所必需的中间件
app.use(express.json());

// ============================================================================
// 存储活跃的 SSE 传输连接
// ============================================================================

/**
 * 使用 Map 存储所有活跃的 SSE 传输实例
 * key: 会话ID (sessionId)
 * value: SSEServerTransport 实例
 *
 * 为什么需要这个？
 * MCP 使用 SSE (Server-Sent Events) 进行实时双向通信
 * 客户端首先通过 /sse 端点建立连接，获得 sessionId
 * 然后通过 /messages 端点发送消息，需要用 sessionId 找到对应的传输实例
 */
const transports = new Map();

// ============================================================================
// SSE 端点 - 建立 SSE 连接
// ============================================================================

/**
 * GET /sse - SSE 连接端点
 *
 * 这是 MCP HTTP 传输的入口点
 * 客户端通过这个端点建立 SSE 连接
 *
 * SSE (Server-Sent Events) 是一种服务器向客户端推送事件的技术
 * 与 WebSocket 不同，SSE 是单向的（服务器→客户端）
 * MCP 使用 SSE 发送响应，使用 POST 请求接收消息
 */
app.get('/sse', async (req, res) => {
  console.log('[SSE] 新的客户端连接请求');

  // 创建 SSE 服务器传输实例
  // 参数说明：
  // - '/messages': 消息端点的路径，客户端将向此路径发送请求
  // - res: Express 响应对象，用于发送 SSE 事件
  const transport = new SSEServerTransport('/messages', res);

  // 将传输实例存储到 Map 中
  // transport.sessionId 是自动生成的唯一会话标识符
  transports.set(transport.sessionId, transport);

  console.log(`[SSE] 已建立连接，会话ID: ${transport.sessionId}`);

  // 监听连接关闭事件
  // 当客户端断开连接时，清理相关资源
  res.on('close', () => {
    console.log(`[SSE] 连接关闭，会话ID: ${transport.sessionId}`);
    // 从 Map 中移除已关闭的传输实例
    transports.delete(transport.sessionId);
  });

  // 将 MCP 服务器与此传输实例连接
  // 这样 MCP 服务器就可以通过这个传输实例与客户端通信
  await mcpServer.connect(transport);

  console.log(`[SSE] MCP 服务器已连接到传输层，会话ID: ${transport.sessionId}`);
});

// ============================================================================
// Messages 端点 - 接收客户端消息
// ============================================================================

/**
 * POST /messages - 消息接收端点
 *
 * 客户端通过这个端点向服务器发送 MCP 协议消息
 * 消息包括：工具调用请求、资源读取请求等
 *
 * 查询参数：
 * - sessionId: 会话标识符，用于找到对应的 SSE 连接
 */
app.post('/messages', async (req, res) => {
  // 从查询参数中获取会话ID
  const sessionId = req.query.sessionId;

  console.log(`[Messages] 收到消息，会话ID: ${sessionId}`);
  console.log(`[Messages] 消息内容:`, JSON.stringify(req.body, null, 2));

  // 根据会话ID查找对应的传输实例
  const transport = transports.get(sessionId);

  // 如果找不到对应的传输实例，返回 404 错误
  if (!transport) {
    console.error(`[Messages] 未找到会话: ${sessionId}`);
    return res.status(404).json({
      error: '会话未找到',
      message: `会话ID ${sessionId} 不存在或已过期，请重新建立 SSE 连接`
    });
  }

  // 将消息传递给传输层处理
  // handlePostMessage 方法会解析消息并交给 MCP 服务器处理
  // 然后通过 SSE 连接返回响应
  await transport.handlePostMessage(req, res);
});

// ============================================================================
// 健康检查端点
// ============================================================================

/**
 * GET /health - 健康检查端点
 *
 * 用于检查服务器是否正常运行
 * 这是一个常见的最佳实践，方便监控和负载均衡器使用
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    server: SERVER_NAME,
    version: SERVER_VERSION,
    timestamp: new Date().toISOString(),
    activeSessions: transports.size  // 当前活跃的会话数
  });
});

// ============================================================================
// 根路径 - 服务器信息
// ============================================================================

/**
 * GET / - 根路径，显示服务器基本信息和使用说明
 */
app.get('/', (req, res) => {
  res.json({
    name: SERVER_NAME,
    version: SERVER_VERSION,
    description: '这是一个简单的 MCP 服务器示例，提供超人信息查询功能',
    endpoints: {
      '/': '服务器信息（当前页面）',
      '/sse': 'SSE 连接端点 (GET) - 建立 MCP 连接',
      '/messages': '消息端点 (POST) - 发送 MCP 消息',
      '/health': '健康检查端点 (GET)'
    },
    tool: {
      name: 'get_superman_info',
      description: '获取超人的详细信息',
      parameters: {
        category: {
          type: 'string',
          options: ['all', 'basic', 'powers', 'origin', 'weaknesses'],
          default: 'all'
        }
      }
    },
    usage: {
      step1: '使用 GET /sse 建立 SSE 连接',
      step2: '从 SSE 事件中获取 sessionId',
      step3: '使用 POST /messages?sessionId=xxx 发送 MCP 消息'
    }
  });
});

// ============================================================================
// 启动服务器
// ============================================================================

/**
 * 启动 HTTP 服务器，监听指定端口
 */
app.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log(`🦸 超人 MCP 服务器已启动！`);
  console.log('='.repeat(60));
  console.log(`📡 服务器地址: http://localhost:${PORT}`);
  console.log(`🔗 SSE 端点:   http://localhost:${PORT}/sse`);
  console.log(`📨 消息端点:   http://localhost:${PORT}/messages`);
  console.log(`❤️  健康检查:   http://localhost:${PORT}/health`);
  console.log('='.repeat(60));
  console.log('可用的 MCP 工具:');
  console.log('  - get_superman_info: 获取超人的详细信息');
  console.log('    参数 category: all | basic | powers | origin | weaknesses');
  console.log('='.repeat(60));
});
