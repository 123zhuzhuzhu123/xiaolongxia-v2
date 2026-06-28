"""创作者声纹提取。"""
import json
import re
from collections import Counter

from sqlalchemy.orm import Session

from app.core.llm_router import generate
from app.core.logging import get_logger
from app.models.content import Content
from app.models.creator import Creator

logger = get_logger(__name__)


def _collect_texts(db: Session, creator_id: int, limit: int = 30) -> list[str]:
    """收集创作者内容文本（标题 + 描述 + 评论）。"""
    contents = (
        db.query(Content)
        .filter(Content.creator_id == creator_id)
        .order_by(Content.published_at.desc())
        .limit(limit)
        .all()
    )
    texts = []
    for c in contents:
        if c.title:
            texts.append(c.title)
        if c.description:
            texts.append(c.description)
        if c.transcript:
            texts.append(c.transcript)
        for comment in c.comment_items:
            if comment.text:
                texts.append(comment.text)
    return texts


def _build_prompt(texts: list[str]) -> str:
    sample = "\n---\n".join(texts[:15])
    return f"""你是一名短视频文案分析师。请根据下面这位创作者的真实内容样本，提炼她的"作者声纹"，输出 JSON。

样本：
{sample}

请输出：
{{
  "one_liner": "一句话人设标签",
  "tone": "语气特点，如亲切/专业/吐槽/温柔",
  "sentence_patterns": ["常用句式1", "常用句式2"],
  "opening_hooks": ["常见开场1", "常见开场2"],
  "pet_phrases": ["口头禅1", "口头禅2"],
  "emotional_intensity": "高/中/低",
  "representative_sentences": ["代表句1", "代表句2"],
  "donts": ["她不会用的表达1", "不会用的表达2"]
}}

只输出 JSON，不要解释。"""


def extract_voice_profile(db: Session, creator_id: int) -> dict:
    """提取创作者声纹并保存。"""
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise ValueError("Creator not found")

    texts = _collect_texts(db, creator_id)
    if not texts:
        return {"error": "no text samples"}

    prompt = _build_prompt(texts)
    raw, provider, model = generate(prompt, timeout=60, temperature=0.4)
    if not raw:
        return {"error": "LLM no response"}

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        profile = json.loads(match.group(0)) if match else json.loads(raw)
    except Exception as e:
        logger.warning(f"Failed to parse voice profile: {e}; raw={raw[:200]}")
        return {"error": "parse failed", "raw": raw[:500]}

    # 统计高频词作为 exemplars
    all_text = " ".join(texts)
    words = re.findall(r"[\u4e00-\u9fa5]{2,4}", all_text)
    top_words = [w for w, _ in Counter(words).most_common(20)]

    creator.persona = profile
    creator.voice_exemplars = top_words
    db.commit()
    db.refresh(creator)

    return profile
