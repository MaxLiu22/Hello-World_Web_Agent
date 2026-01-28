"""
Day 3 预备：用 FastAPI 把 agent_test 的一次运行封装成一个简单的后端接口。

当前设计非常简单：
- GET /health   用于健康检查
- POST /run     启动一次 Agent 任务（阻塞直到结束），返回简单结果信息

后面可以逐步演进为：
- 异步任务（后台执行）
- WebSocket 日志流
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from agent_test import main as run_agent


app = FastAPI(title="Mini-Manus Agent API", version="0.1.0")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/run")
def run_once() -> dict:
    """
    同步启动一次 Agent 任务。

    注意：当前版本会阻塞请求直到 agent_test.main() 运行完成。
    这是一个非常简单的 MVP，后续可以改为后台任务 + 流式日志。
    """
    run_agent()
    return {"status": "completed"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """
    一个极简的 Day 3 宿主页面：
    - 左侧：任务输入 + 按钮（当前固定触发一次 run_agent）
    - 右侧：noVNC Iframe（来自 6080 端口）
    """
    return """
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>Mini-Manus Web Agent</title>
    <style>
      body {
        margin: 0;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
        height: 100vh;
        display: flex;
        flex-direction: column;
      }
      header {
        padding: 12px 16px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      header h1 {
        margin: 0;
        font-size: 16px;
      }
      header span {
        font-size: 12px;
        color: #6b7280;
      }
      main {
        flex: 1;
        display: flex;
        min-height: 0;
      }
      .left-panel {
        width: 360px;
        border-right: 1px solid #e5e7eb;
        display: flex;
        flex-direction: column;
      }
      .left-panel-inner {
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        height: 100%;
      }
      textarea {
        width: 100%;
        flex: 1;
        resize: none;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 8px;
        font-size: 14px;
        outline: none;
      }
      textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.3);
      }
      button {
        padding: 8px 12px;
        border-radius: 999px;
        border: none;
        background: #6366f1;
        color: white;
        font-size: 14px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
      }
      button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      .status {
        font-size: 12px;
        color: #6b7280;
      }
      .log {
        font-size: 12px;
        color: #4b5563;
        background: #f3f4f6;
        border-radius: 8px;
        padding: 8px;
        max-height: 120px;
        overflow: auto;
      }
      .right-panel {
        flex: 1;
        background: #111827;
      }
      .right-panel iframe {
        width: 100%;
        height: 100%;
        border: none;
      }
    </style>
  </head>
  <body>
    <header>
      <h1>Mini-Manus Web Agent</h1>
      <span>左侧发起任务 · 右侧实时观看浏览器</span>
    </header>
    <main>
      <section class="left-panel">
        <div class="left-panel-inner">
          <label for="task-input" style="font-size: 13px; color: #374151;">
            任务指令（当前后端固定示例，暂不解析自定义文案）：
          </label>
          <textarea id="task-input" rows="4">帮我查看深圳未来14天天气，并总结适合户外活动的日期。</textarea>
          <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 4px;">
            <button id="run-btn">
              <span>🚀 启动 Agent</span>
            </button>
            <span class="status" id="status-text">状态：空闲</span>
          </div>
          <div class="log" id="log-box">
            日志会显示在这里。
          </div>
        </div>
      </section>
      <section class="right-panel">
        <!-- 直接嵌入 noVNC 的精简页面，并开启自动连接和缩放 -->
        <iframe src="http://localhost:6080/vnc_lite.html?autoconnect=1&resize=scale" title="Agent Browser View"></iframe>
      </section>
    </main>

    <script>
      const runBtn = document.getElementById('run-btn');
      const statusText = document.getElementById('status-text');
      const logBox = document.getElementById('log-box');

      function appendLog(text) {
        const ts = new Date().toLocaleTimeString();
        logBox.textContent += `\\n[${ts}] ${text}`;
        logBox.scrollTop = logBox.scrollHeight;
      }

      runBtn.addEventListener('click', async () => {
        runBtn.disabled = true;
        statusText.textContent = '状态：运行中（请在右侧屏幕查看浏览器动作）';
        appendLog('开始调用 /run 接口...');

        try {
          const res = await fetch('/run', { method: 'POST' });
          if (!res.ok) {
            appendLog(`/run 调用失败：HTTP ${res.status}`);
          } else {
            const data = await res.json();
            appendLog(`/run 调用完成：${JSON.stringify(data)}`);
          }
        } catch (err) {
          appendLog('调用 /run 接口出错：' + err);
        } finally {
          statusText.textContent = '状态：空闲';
          runBtn.disabled = false;
        }
      });
    </script>
  </body>
  </html>
    """



