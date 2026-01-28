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


