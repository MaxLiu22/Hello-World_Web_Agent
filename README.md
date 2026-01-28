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
    * [x] 初始化 Python 环境，安装 `playwright`, `langchain-openai` 等基础依赖，并升级至 Python 3.11。
    * [x] 编写 `agent_test.py`，接入 Kimi API（OpenAI 兼容协议）。
    * [x] 实现第一个任务：让 Agent 自动打开浏览器，在百度中搜索“深圳未来14天天气”。
* **验证点**：
    * [x] 终端能输出 Agent 的思考过程（Kimi 生成操作步骤）。
    * [x] 本地自动弹出的浏览器能根据脚本自动输入“深圳未来14天天气”并触发搜索。
    * [x] 在搜索结果页抓取天气文本，并由 Agent 生成“未来14天天气 + 适合户外日期”的总结。

### 第二天：容器化与画面流 (Docker + VNC)
**目标**：将浏览器“云端化”，通过网页实时查看画面。
* **核心任务**：
    * [x] 编写 `Dockerfile`，集成 Playwright 运行环境及 VNC 服务（Xvfb + x11vnc + noVNC）。
    * [x] 配置 `docker-compose.yml`，映射 6080 端口（noVNC）到宿主机。
    * [x] 修改 Agent 代码，使其在 Docker 虚拟显示器（DISPLAY=:99）中运行，并兼容非交互环境。
* **验证点**：
    * [x] 在宿主机浏览器访问 `http://localhost:6080/vnc.html` 能看到容器内的桌面。
    * [x] 运行 `docker-compose up --build` 后，noVNC 窗口内能实时看到 Agent 在百度中自动搜索“深圳未来14天天气”。

> **Day 2 快速体验：**
> 1. 在项目根目录执行：`docker-compose up --build`
> 2. 打开浏览器访问：`http://localhost:8000/`
> 3. 右侧 Iframe 会自动通过 noVNC 连接容器桌面，你可以直接看到浏览器自动打开并搜索“深圳未来14天天气”。

### 第三天：前端集成与“Manus”初体验
**目标**：完成双窗交互 UI，打造完整的 Web Agent 产品体验。
* **核心任务**：
    * [x] 使用 FastAPI 封装后端接口，提供同步启动 Agent 任务的 `/run` API（后续可演进为异步）。
    * [x] 编写前端宿主页面（由 FastAPI `/` 提供），左侧集成任务输入与“启动 Agent”按钮，右侧嵌入 noVNC 的 `<iframe>`。
    * [x] 实现联动：点击左侧“启动 Agent”按钮 -> 后端调用 `/run` -> 右侧 Iframe 中的浏览器自动加载并执行任务。
* **验证点**：
    * [x] 用户在 Web UI 点击按钮，无需操作终端即可在右侧看到 Agent 自动干活。
    * [x] 任务完成后，终端日志中能看到 Agent 总结的天气报告（后续可将总结回传到前端页面展示）。

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

---

### （可选）第四天：browser-use 内核重构与分支实验
**目标**：在保留现有 Playwright 手写 Agent 的前提下，引入 browser-use 作为新的 Web Agent 内核，并为未来接入 Qwen-VL 做准备。  
* **建议分支策略**：
    * 在当前基础上创建一个长期保留分支（例如 `playwright-baseline`），完整保存 Day 1–3 的实现。
    * 在主分支上开始 browser-use 版本的重构与实验，必要时可随时对比或回滚。
* **核心任务（browser-use 路线）**：
    * [ ] 新增 `browser_use_agent.py`，用 Kimi + browser-use 跑通“打开百度”的最小 Demo（先在本机验证）。
    * [ ] 在 FastAPI 中为 browser-use 版本新增独立的 `/run_browser_use` 接口，便于与现有 `/run` 对比。
    * [ ] 将 browser-use Agent 挂载到 Docker + VNC 链路中，在 noVNC 画面中观察其自动操作过程。
    * [ ] 设计并实现一个“视觉点击”工具，将 Qwen-VL 接入 browser-use 的 tool 体系，用截图 + 坐标方式完成复杂点击。
* **验证点**：
    * [ ] 同一套 UI 下，可以分别触发 Playwright-baseline 与 browser-use 版本，对比行为差异。
    * [ ] 在复杂页面结构下，browser-use + Qwen-VL 能成功完成传统 DOM 选择困难的点击与操作。