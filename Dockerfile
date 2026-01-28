# Day 2 - 基础容器（先跑通 Playwright + Kimi，在容器里执行 agent_test.py）
#
# 这一版暂时不加 VNC/noVNC，只验证：
# - 可以在 Docker 里安装依赖
# - 可以在 Docker 里调用 Kimi + Playwright（默认用无头浏览器）

FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

WORKDIR /app

# 安装 Xvfb + x11vnc + noVNC + websockify，用于虚拟显示和远程桌面
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      xvfb \
      x11vnc \
      novnc \
      websockify \
    && rm -rf /var/lib/apt/lists/*

# 先复制 Docker 专用的依赖清单并安装，利用 Docker 缓存（只包含 Playwright + Kimi 相关）
COPY requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

# 再复制项目代码
COPY . .

# 显示相关环境变量
ENV DISPLAY=:99

# 启动脚本：负责启动 Xvfb、x11vnc、noVNC，然后运行 agent
CMD ["bash", "start.sh"]


