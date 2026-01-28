# 🚀 Mini-Manus: Open-Source Web Agent Implementation

这是一个受 Manus AI 启发而开发的 Web Agent 原型项目。该项目旨在通过 **Kimi (LLM)** 进行逻辑推理，并结合 **browser-use** 与 **noVNC** 实现在 Web 前端实时观测 Agent 的自动化浏览器操作。

## 🏗️ 技术架构
* **大脑 (Reasoning):** Kimi API (OpenAI 兼容协议)
* **执行器 (Driver):** Python + Playwright + [browser-use](https://github.com/browser-use/browser-use)
* **实时画面 (Streaming):** Docker + Xvfb + x11vnc + noVNC
* **交互界面 (UI):** FastAPI + React / Simple HTML (双 Iframe 架构)

---

## 📅 3-Day Sprint 冲刺计划

### 第一天：核心大脑与执行驱动 (MVP)
**目标**：实现“指令 -> 思考 -> 操作”的闭环。
* **核心任务**：
    * [ ] 初始化 Python 环境，安装 `browser-use`, `langchain-openai`。
    * [ ] 编写 `agent_test.py`，接入 Kimi API。
    * [ ] 实现第一个任务：让 Agent 自动打开浏览器搜索“深圳未来14天天气”。
* **验证点**：
    * 终端能输出 Agent 的思考过程。
    * 本地自动弹出的浏览器正确执行了搜索指令并获取了数据。

### 第二天：容器化与画面流 (Docker + VNC)
**目标**：将浏览器“云端化”，通过网页实时查看画面。
* **核心任务**：
    * [ ] 编写 `Dockerfile`，集成 Playwright 运行环境及 VNC 服务。
    * [ ] 配置 `docker-compose.yml`，映射 6080 端口（noVNC）到宿主机。
    * [ ] 修改 Agent 代码，使其在 Docker 虚拟显示器（DISPLAY=:99）中运行。
* **验证点**：
    * 在宿主机浏览器访问 `localhost:6080` 能看到容器内的桌面。
    * 运行脚本后，noVNC 窗口内能实时看到 Agent 的操作过程。

### 第三天：前端集成与“Manus”初体验
**目标**：完成双窗交互 UI，打造完整的 Web Agent 产品体验。
* **核心任务**：
    * [ ] 使用 FastAPI 封装后端接口，支持异步启动 Agent 任务。
    * [ ] 编写前端宿主页面，左侧集成聊天输入框，右侧嵌入 noVNC 的 `<iframe>`。
    * [ ] 实现联动：点击发送指令 -> 后端启动任务 -> 前端 Iframe 自动加载画面。
* **验证点**：
    * 用户在 UI 输入指令，无需操作终端即可在右侧看到 Agent 自动干活。
    * 任务完成后，对话框显示 Agent 总结的天气报告。

---

## 🛠️ 开始之前
在开始第一天任务前，请确保你已准备好：
1.  **Python 3.10+**
2.  **Docker Desktop**
3.  **Kimi API Key** (BASE_URL 请指向 Kimi 官方或中转地址)

---

## 📈 未来路线图
- [ ] 支持文件上传并从宿主机挂载至容器。
- [ ] 接入 Qwen-VL 实现基于视觉的坐标点击优化（解决复杂 DOM 定位问题）。
- [ ] 多会话隔离与浏览器容器动态调度。