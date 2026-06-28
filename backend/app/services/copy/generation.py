"""多版本文案生成服务。"""
import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.core.llm_router import generate
from app.models.content import Content
from app.models.copy import CopyDraft, CopyVersion
from app.models.formula import Formula
from app.models.hook import Hook
from app.models.sku import Sku
from app.services.comment.audience import segment_audience_by_content
from app.services.content.viral_factors import analyze_viral_factors


COPY_GENERATION_PROMPT = """你是抖音美食带货短视频的资深编导，擅长基于爆款公式为同一素材产出多条高转化口播文案。

【素材信息】
- 平台：{platform}
- 视频标题：{title}
- 视频描述/文案：{desc}
- 爆款因子：{viral}

【创作者声纹】
{voice}

【可选商品 SKU】
{skus}

【可选钩子库】
{hooks}

【可选爆款公式】
{formulas}

【评论人群洞察】
{audience}

任务要求：
1. 从评论人群洞察中提炼 1-3 个高转化切入角度（痛点、场景、价格敏感、好奇等）。
2. 结合创作者声纹，为每个角度选择最匹配的钩子类型和爆款公式，生成一条口播文案版本。
3. 每条文案 120-220 字，结构：吸睛开场 → 痛点/场景共鸣 → 卖点植入 → CTA。
4. 尽量自然融入 SKU 卖点，不要硬广。
5. 输出严格 JSON，不要 Markdown 代码块：
{{
  "versions": [
    {{
      "formula_key": "公式key",
      "hook_type": "钩子类型",
      "angle": "切入角度一句话",
      "title": "视频标题（可选）",
      "body": "完整口播文案",
      "selling_points": ["卖点1", "卖点2"],
      "cta": "引导行动话术",
      "target_scene": "适用投放场景",
      "estimated_hook_rate": 0.78,
      "why": "为什么这个版本可能爆",
      "risk_words": ["可能违规词1"]
    }}
  ],
  "summary": "本次生成策略概述"
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
        # 尝试提取第一个 JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return {}


def _format_voice(voice: dict[str, Any] | None) -> str:
    if not voice:
        return "暂无"
    return json.dumps(voice, ensure_ascii=False, indent=2)


def _format_assets(items: list[Any], label: str) -> str:
    if not items:
        return f"暂无{label}"
    parts = []
    for it in items:
        if isinstance(it, Formula):
            parts.append(
                f"- key={it.formula_key} name={it.name} goal={it.goal}: {it.template}"
            )
        elif isinstance(it, Hook):
            parts.append(f"- type={it.hook_type}: {it.text}")
        elif isinstance(it, Sku):
            points = ", ".join(it.selling_points or [])
            parts.append(
                f"- {it.sku_name}（{it.brand_name or '无品牌'}）卖点：{points}"
            )
    return "\n".join(parts)


def _format_audience(seg: dict[str, Any]) -> str:
    if not seg:
        return "暂无"
    total = seg.get("total_commenters", 0)
    segments = seg.get("segments", {})
    return f"总评论人数 {total}，人群分布：{json.dumps(segments, ensure_ascii=False)}"


def generate_copy(
    db: Session,
    content_id: int,
    project_id: int,
    goal: str = "conversion",
    platform: str = "douyin",
    sku_id: int | None = None,
) -> CopyDraft:
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise ValueError("Content not found")
    if content.project_id != project_id:
        raise ValueError("Content does not belong to project")

    voice = content.creator.persona if content.creator else None
    factors = content.viral_factors or analyze_viral_factors(content)
    audience = segment_audience_by_content(db, content_id)

    skus = db.query(Sku).filter(Sku.project_id == project_id).all()
    formulas = db.query(Formula).filter(Formula.project_id == project_id).all()
    hooks = db.query(Hook).filter(Hook.project_id == project_id).all()

    if sku_id:
        selected_sku = db.query(Sku).filter(
            Sku.id == sku_id, Sku.project_id == project_id
        ).first()
        if not selected_sku:
            raise ValueError("SKU not found or does not belong to project")
        skus = [selected_sku]

    prompt = COPY_GENERATION_PROMPT.format(
        platform=platform,
        title=content.title or "",
        desc=content.description or "",
        viral=json.dumps(factors, ensure_ascii=False, indent=2),
        voice=_format_voice(voice),
        skus=_format_assets(skus, "SKU"),
        hooks=_format_assets(hooks, "钩子"),
        formulas=_format_assets(formulas, "公式"),
        audience=_format_audience(audience),
    )

    raw, provider, model = generate(prompt, timeout=120, temperature=0.7)
    data = _extract_json(raw)
    versions = data.get("versions", [])
    summary = data.get("summary", "")

    if not versions:
        raise ValueError("LLM did not return valid copy versions")

    draft = CopyDraft(
        project_id=project_id,
        creator_id=content.creator_id,
        sku_id=sku_id,
        goal=goal,
        platform=platform,
        topic=content.title,
        original_copy=content.description,
        extra={
            "content_id": content_id,
            "summary": summary,
            "provider": provider,
            "model": model,
            "viral_factors": factors,
            "audience": audience,
        },
    )
    db.add(draft)
    db.flush()

    for v in versions:
        version = CopyVersion(
            draft_id=draft.id,
            formula_key=(v.get("formula_key") or "unknown")[:50],
            title=v.get("title"),
            body=v.get("body", ""),
            scores={
                "estimated_hook_rate": v.get("estimated_hook_rate"),
            },
            evidence={
                "hook_type": v.get("hook_type"),
                "angle": v.get("angle"),
                "selling_points": v.get("selling_points", []),
                "cta": v.get("cta"),
                "target_scene": v.get("target_scene"),
                "why": v.get("why"),
                "risk_words": v.get("risk_words", []),
            },
        )
        db.add(version)

    db.commit()
    db.refresh(draft)
    return draft
