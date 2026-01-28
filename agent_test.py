"""
一个极简的 Web Agent 骨架，帮助你理解“指令 -> 思考 -> 操作”三阶段结构。

这版：
- 用 Playwright 打开一个真实的浏览器页面
- 用 Kimi（通过 OpenAI 兼容接口）来生成“操作计划”
"""

import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from playwright.sync_api import sync_playwright

from visual_tool import visual_inspect


def get_user_instruction() -> str:
    """模拟从用户那里接收一个自然语言指令。"""
    # 真实情况：未来这里会从命令行参数 / Web 接口 / 前端传进来
    return "帮我查看深圳未来14天天气，并总结适合户外活动的日期。"


def _load_kimi_client() -> ChatOpenAI:
    """
    加载 .env 中的 Kimi 配置，并返回一个 LangChain 的 ChatOpenAI 客户端。

    这里假设你在项目根目录下创建了 `.env` 文件，并配置了：
    - KIMI_API_KEY
    - KIMI_BASE_URL
    - KIMI_MODEL（可选，有默认值）
    """
    load_dotenv()

    api_key = os.getenv("KIMI_API_KEY")
    base_url = os.getenv("KIMI_BASE_URL")
    model = os.getenv("KIMI_MODEL", "moonshot-v1-8k")

    if not api_key or not base_url:
        raise RuntimeError(
            "缺少 Kimi 配置：请在项目根目录创建 `.env` 文件，并设置 "
            "KIMI_API_KEY 和 KIMI_BASE_URL（可参考你自己的 Kimi 文档）。"
        )

    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.2,
    )


def think_about_plan(instruction: str) -> list[str]:
    """
    使用 Kimi 来思考“如何在浏览器里完成这个任务”，并返回一个步骤列表。

    为了简单起见，我们让模型输出多行文本，每行一个步骤，然后按行拆分。
    """
    print("🧠 [思考中] 调用 Kimi 规划浏览器操作步骤...")
    llm = _load_kimi_client()

    prompt = (
        "你是一个需要通过普通浏览器完成任务的智能体。\n"
        "用户指令如下，请你规划一份在浏览器中执行的操作步骤。\n"
        "要求：\n"
        "1. 用简体中文回答。\n"
        "2. 每行只写一个步骤，可以带编号也可以不带，但尽量简短清晰。\n"
        "3. 步骤里只描述“我要在浏览器里做什么”，不要给最终天气结论。\n\n"
        f"用户指令：{instruction}\n"
    )

    response = llm.invoke(prompt)
    text = getattr(response, "content", str(response))

    # 按行拆分成步骤列表，过滤掉空行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    print("🧠 [Kimi 返回的原始步骤文本]:")
    for line in lines:
        print("  ", line)

    return lines


def execute_plan(plan: list[str]) -> None:
    """
    “操作”阶段的最小可运行版本：
    - 先打印出计划步骤
    - 然后用 Playwright 打开一个真实浏览器页面
    """
    print("🖱️ [执行中] 下面是理论上要在浏览器里执行的步骤：")
    for i, step in enumerate(plan, start=1):
        print(f"  Step {i}: {step}")

    print("\n🌐 [Playwright] 准备打开一个真实浏览器页面（百度首页示例）...")
    with sync_playwright() as p:
        # 在本机开发时用有头模式；在 Docker 等无显示环境中可以通过环境变量切到 headless 模式
        headless_env = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower()
        headless = headless_env in ("1", "true", "yes")

        browser = p.chromium.launch(headless=headless)  # 本地默认 False，容器中可设为 True
        page = browser.new_page()
        page.goto("https://www.baidu.com", wait_until="load")
        print("✅ 浏览器已打开百度首页，你可以看到一个新窗口弹出。")

        # 这里做一件非常具体的事：在搜索框输入“深圳 未来14天天气”并回车
        try:
            print("⌨️ [Playwright] 正在自动输入搜索内容并回车：深圳 未来14天天气")

            # 等待页面上的搜索输入框真正可用（容器内网络/渲染可能更慢）
            page.wait_for_timeout(2000)

            # 你提供的 DOM 里，真正可编辑的是 id="chat-textarea" 的 textarea
            # 我们优先直接用这个元素；如果找不到，再回退到传统搜索框。
            chat_textarea = page.locator("#chat-textarea")
            if chat_textarea.count() > 0:
                print("🔍 使用 #chat-textarea 作为搜索输入。")
                search_box = chat_textarea.first
            else:
                print("🔍 未找到 #chat-textarea，回退到 input[name=\"wd\"]。")
                search_box = page.locator('input[name="wd"]')

            search_box.click()
            # 用 type 而不是 fill，更接近“真实键盘输入”，也便于你肉眼观察
            page.keyboard.type("深圳 未来14天天气")
            page.keyboard.press("Enter")

            # 等待搜索结果页面加载稳定
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            print("📄 [Playwright] 尝试提取结果页文本用于天气总结...")
            # 阶段一：调用视觉工具占位实现（截图 + 占位回答），先打通调用路径
            visual_answer = visual_inspect(
                page,
                "请粗略描述当前搜索结果页面的布局结构（这是占位实现，未来会用 Qwen-VL 回答）。",
            )
            print("👁️ [visual_inspect 占位回答]:")
            print(visual_answer)

            try:
                # 简单策略：抓取 body 文本，并截断到一定长度，避免 prompt 过长
                raw_text = page.inner_text("body")
            except Exception:
                raw_text = ""

            if raw_text:
                snippet = raw_text[:4000]  # 简单截断，防止上下文过大
                print("📄 [Playwright] 已获取结果页文本片段，调用 Kimi 进行总结...")

                llm = _load_kimi_client()
                summary_prompt = (
                    "下面是一段网页上关于深圳未来天气的信息文本（可能包含额外内容）。\n"
                    "请你基于其中与“深圳未来14天天气”相关的部分，做一个简洁的总结：\n"
                    "1. 用中文回答。\n"
                    "2. 列出未来14天中适合户外活动的日期，并说明原因（例如晴天、温度适宜等）。\n"
                    "3. 如果无法严格得到14天的逐日信息，可以基于可用信息做合理的概括。\n\n"
                    f"网页文本片段如下：\n{snippet}\n"
                )
                summary_resp = llm.invoke(summary_prompt)
                summary_text = getattr(summary_resp, "content", str(summary_resp))

                print("\n📝 [Kimi 总结的深圳未来14天天气报告]:")
                print(summary_text)
            else:
                print("⚠️ 未能从结果页提取到文本，跳过天气总结。")

        except Exception as e:
            print(f"⚠️ 自动搜索或提取结果过程中出现异常：{e}")

        # 本地开发时允许用户按回车后再关闭浏览器；
        # 在 Docker 等非交互环境中，直接关闭浏览器避免 EOFError。
        if sys.stdin.isatty():
            input("按下回车键后关闭浏览器并结束脚本...")
        else:
            print("⌛ 非交互环境（例如 Docker），自动关闭浏览器并结束脚本。")
        browser.close()


def main() -> None:
    """串起 整个 ‘指令 -> 思考 -> 操作’ 的最小闭环。"""
    print("==== Mini-Manus Day 1 骨架 Demo ====")

    # 1. 指令
    instruction = get_user_instruction()
    print(f"📥 [指令] {instruction}")

    # 2. 思考
    plan = think_about_plan(instruction)

    # 3. 操作
    execute_plan(plan)

    print("✅ Demo 结束（Kimi 负责思考步骤，Playwright 负责真实浏览器操作）")


if __name__ == "__main__":
    main()

