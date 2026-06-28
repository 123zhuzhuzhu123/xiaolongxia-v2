"""文案质量门控评分。"""
import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.core.llm_router import generate
from app.models.copy import CopyVersion
from app.models.sku import Sku


QUALITY_PROMPT = """你是短视频内容审核与效果预测专家。请对以下口播文案进行多维度评分。

【文案】
{body}

【标题】
{title}

【关联 SKU】
{sku}

【创作者声纹】
{voice}

【备注信息】
{evidence}

请从 1-10 分对以下维度打分，并给出整体综合分与优化建议：
- hook：开头 3 秒是否足够抓人
- relevance：与目标场景/人群是否相关
- cta：行动引导是否明确
- brand_voice：是否符合创作者声纹
- risk：是否存在违规/限流风险（分值越高风险越低）
- viral_potential：整体爆款潜力

输出严格 JSON：
{{
  "overall": 7.8,
  "pass": true,
  "dimensions": {{
    "hook": 8,
    "relevance": 7,
    "cta": 8,
    "brand_voice": 7,
    "risk": 9,
    "viral_potential": 8
  }},
  "suggestions": ["建议1", "建议2"],
  "risk_words": ["检测到的风险词"]
}}
"""


def _extract_json(text: str | None) -> dict[str, Any]:
    if not text:
        return {}
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text)
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return {}


def score_version(db: Session, version_id: int) -> dict[str, Any]:
    version = db.query(CopyVersion).filter(CopyVersion.id == version_id).first()
    if not version:
        raise ValueError("CopyVersion not found")

    draft = version.draft
    sku_text = "暂无"
    if draft.sku_id:
        sku = db.query(Sku).filter(Sku.id == draft.sku_id).first()
        if sku:
            points = ", ".join(sku.selling_points or [])
            sku_text = f"{sku.sku_name}（{sku.brand_name or '无品牌'}）卖点：{points}"

    voice = "暂无"
    if draft.creator_id and draft.creator and draft.creator.persona:
        voice = json.dumps(draft.creator.persona, ensure_ascii=False)

    evidence = json.dumps(version.evidence or {}, ensure_ascii=False)

    prompt = QUALITY_PROMPT.format(
        body=version.body,
        title=version.title or "",
        sku=sku_text,
        voice=voice,
        evidence=evidence,
    )

    raw, provider, model = generate(prompt, timeout=60, temperature=0.3)
    data = _extract_json(raw)
    if not data:
        data = {
            "overall": 0,
            "pass": False,
            "dimensions": {},
            "suggestions": ["LLM 未返回有效评分"],
            "risk_words": [],
        }

    version.quality_review = {
        **data,
        "provider": provider,
        "model": model,
    }
    version.scores = {
        **(version.scores or {}),
        "overall": data.get("overall"),
        "dimensions": data.get("dimensions", {}),
    }
    db.commit()
    db.refresh(version)
    return version.quality_review
