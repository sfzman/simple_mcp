# ============================================================================
# Dockerfile for Superman MCP Server
# 适用于 Google Cloud Run 部署
# ============================================================================

# 使用官方 Python 3.11 slim 镜像作为基础
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# - PYTHONDONTWRITEBYTECODE: 不生成 .pyc 文件
# - PYTHONUNBUFFERED: 禁用输出缓冲，确保日志实时输出
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY server.py .

# Cloud Run 会设置 PORT 环境变量，默认 8080
ENV PORT=8080

# 暴露端口（文档用途，Cloud Run 会自动检测）
EXPOSE ${PORT}

# 启动命令
CMD ["python", "server.py"]
