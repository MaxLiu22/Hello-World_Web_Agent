"""
视觉工具实现：阶段二引入 Qwen-VL（走 OpenAI 兼容接口），否则回退到占位实现。

统一接口：

    visual_inspect(page, question) -> str

调用路径已经在 agent_test.py 中打通：
- 在浏览器完成搜索后调用本函数：
  - 先截图
  - 如检测到 Qwen-VL 配置（VL_MODEL/VL_BASE_URL/VL_API_KEY），则通过 ChatOpenAI 调用多模态接口
  - 否则返回占位回答
"""

import base64
import os
from datetime import datetime
from typing import Any, Optional

from langchain_openai import ChatOpenAI


def _create_openai_llm(
    model: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    **kwargs,
) -> ChatOpenAI:
    """
    复用你提供的 create_openai_llm 思路：
    - 只在 base_url / api_key 非空时注入参数
    """
    llm_kwargs: dict[str, Any] = {"model": model, "temperature": temperature, **kwargs}

    if base_url:
        llm_kwargs["base_url"] = base_url
    if api_key:
        llm_kwargs["api_key"] = api_key

    return ChatOpenAI(**llm_kwargs)


def _call_qwen_vl(image_path: str, question: str) -> str:
    """
    使用 OpenAI 兼容接口调用 Qwen-VL：
    - 依赖环境变量：VL_MODEL / VL_BASE_URL / VL_API_KEY
    - 要求后端网关支持多模态消息格式（image_url + text）
    """
    model = os.getenv("VL_MODEL") or os.getenv(
        "QWEN_VL_MODEL", "qwen-vl-max-latest"
    )
    base_url = os.getenv("VL_BASE_URL")
    api_key = os.getenv("VL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "未检测到 VL_API_KEY，暂时无法真实调用 Qwen-VL（OpenAI 兼容接口）。"
        )

    llm = _create_openai_llm(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0.0,
    )

    # 将图片转成 data URL 形式，按 OpenAI 多模态格式构造消息
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": question},
            ],
        }
    ]

    resp = llm.invoke(messages)
    # ChatOpenAI 返回对象通常有 .content 字段
    return getattr(resp, "content", str(resp))


def visual_inspect(page: Any, question: str) -> str:
    """
    “视觉检查”工具：
    - 使用 Playwright 的 page.screenshot 保存当前页面截图
    - 如检测到并正确配置 Qwen-VL（DashScope），则真实调用 Qwen-VL
    - 否则打印提示，返回占位回答
    """
    # 确保截图目录存在
    screenshots_dir = os.path.join(os.getcwd(), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screen_{timestamp}.png"
    filepath = os.path.join(screenshots_dir, filename)

    try:
        page.screenshot(path=filepath, full_page=True)
        print(f"👁️ [visual_inspect] 已保存当前页面截图到: {filepath}")
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ [visual_inspect] 截图失败（占位实现继续执行）：{e}")

    # 尝试真实调用 Qwen-VL，多模态接口
    try:
        answer = _call_qwen_vl(filepath, question)
        print("👁️ [visual_inspect] 成功调用 Qwen-VL。")
        return answer
    except RuntimeError as e:
        print(f"⚠️ [visual_inspect] Qwen-VL 未配置或调用失败，使用占位回答：{e}")
        return (
            "这是视觉工具的占位实现。截图已保存，未来会在这里调用 Qwen-VL "
            f"来回答问题：{question}"
        )


