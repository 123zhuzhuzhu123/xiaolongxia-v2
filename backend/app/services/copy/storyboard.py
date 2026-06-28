"""根据文案版本生成短视频分镜脚本。"""
import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.core.llm_router import generate
from app.models.copy import CopyVersion
from app.models.sku import Sku


STORYBOARD_PROMPT = """你是抖音短视频分镜导演。请根据以下口播文案，生成 8-12 个镜头的分镜脚本。

【文案】
{body}

【标题】
{title}

【商品信息】
{sku}

【创作者声纹】
{voice}

要求：
1. 每个镜头包含：景别（shot_type）、画面内容（visual）、口播/音效（audio）、时长秒数（duration_seconds）、所需道具（props）、备注（note）。
2. 镜头之间要有逻辑衔接，前 3 秒必须强钩子。
3. 口播内容要与文案对应，但不要完全重复，可标注分段。
4. 总时长控制在 30-60 秒。

输出严格 JSON：
{{
  "total_duration": 45,
  "shots": [
    {{
      "scene_no": 1,
      "shot_type": "特写/中景/全景/近景",
      "visual": "画面描述",
      "audio": "口播台词或音效",
      "duration_seconds": 3,
      "props": ["道具1"],
      "note": "拍摄备注"
    }}
  ]
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


def generate_storyboard(db: Session, version_id: int) -> dict[str, Any]:
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

    prompt = STORYBOARD_PROMPT.format(
        body=version.body,
        title=version.title or "",
        sku=sku_text,
        voice=voice,
    )

    raw, provider, model = generate(prompt, timeout=90, temperature=0.5)
    data = _extract_json(raw)
    if not data or "shots" not in data:
        raise ValueError("LLM did not return valid storyboard")

    extra = version.extra or {}
    extra["storyboard"] = {**data, "provider": provider, "model": model}
    version.extra = extra
    db.commit()
    db.refresh(version)
    return extra["storyboard"]
