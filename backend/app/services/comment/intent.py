"""评论意图语义分析。"""
import json
import re

from app.core.llm_router import generate
from app.core.logging import get_logger

logger = get_logger(__name__)

INTENT_CATEGORIES = ["buying", "risk", "loyal", "question", "price", "scene", "other"]
SENTIMENT_CATEGORIES = ["positive", "negative", "neutral"]


PROMPT_TEMPLATE = """你是一名电商评论分析专家。请分析下面这条短视频/图文评论，输出一个 JSON 对象。

评论内容：
"{text}"

意图类别（必选其一）：
- buying：明确购买意向，如"已下单""准备买""加购了""想试试"
- risk：顾虑或风险，如"担心不好用""怕过敏""不敢买""智商税"
- loyal：忠诚口碑，如"一直在用""回购多次""推荐给朋友"
- question：功能/使用疑问，如"适合多大宝宝""怎么用""成分是什么"
- price：价格敏感，如"太贵""等活动""有优惠吗""性价比"
- scene：使用场景分享，如"给宝宝擦嘴""出门带很方便"
- other：以上都不是

情感（必选其一）：positive / negative / neutral

输出格式（只输出 JSON，不要任何解释）：
{{"intent": "...", "sentiment": "...", "reason": "简短理由"}}
"""


def analyze_comment_intent(text: str) -> dict:
    """分析单条评论的意图和情感。

    Returns:
        {"intent": str, "sentiment": str, "confidence": float, "reason": str}
    """
    if not text or not text.strip():
        return {"intent": "other", "sentiment": "neutral", "confidence": 0.0, "reason": "空评论"}

    prompt = PROMPT_TEMPLATE.format(text=text.strip())
    raw, provider, model = generate(prompt, timeout=30, temperature=0.2)
    if not raw:
        logger.warning("LLM returned empty for comment intent analysis")
        return {"intent": "other", "sentiment": "neutral", "confidence": 0.0, "reason": "LLM无响应"}

    try:
        # 尝试提取 JSON
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
        else:
            parsed = json.loads(raw)
    except Exception as e:
        logger.warning(f"Failed to parse LLM response as JSON: {e}; raw={raw[:200]}")
        return {"intent": "other", "sentiment": "neutral", "confidence": 0.0, "reason": "解析失败"}

    intent = parsed.get("intent", "other")
    sentiment = parsed.get("sentiment", "neutral")
    reason = parsed.get("reason", "")

    if intent not in INTENT_CATEGORIES:
        intent = "other"
    if sentiment not in SENTIMENT_CATEGORIES:
        sentiment = "neutral"

    # 简单置信度：类别明确且理由非空给 0.9，否则 0.7
    confidence = 0.9 if reason else 0.7

    return {"intent": intent, "sentiment": sentiment, "confidence": confidence, "reason": reason}
