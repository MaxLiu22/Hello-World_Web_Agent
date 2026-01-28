#!/usr/bin/env bash
set -e

echo "==> 启动虚拟显示器 Xvfb (:99)..."
# -ac 关闭访问控制，避免 x11vnc 因为 Xauthority 权限问题连不上
Xvfb :99 -screen 0 1920x1080x24 -ac &

echo "==> 启动 x11vnc，将 :99 映射为 VNC (端口 5900)..."
x11vnc -display :99 -rfbport 5900 -nopw -forever -shared -quiet &

echo "==> 启动 noVNC（websockify 6080 -> 5900）..."
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &

echo "==> 等待桌面服务就绪..."
sleep 3

# 在 Docker 中使用有头浏览器，让画面出现在虚拟显示器上
export PLAYWRIGHT_HEADLESS=false

echo "==> 启动 FastAPI 后端（api_main:app）..."
uvicorn api_main:app --host 0.0.0.0 --port 8000


