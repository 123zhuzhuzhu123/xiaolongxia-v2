"""内容爆款因子分析。"""
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.content import Content


def extract_hashtags(text: str | None) -> list[str]:
    if not text:
        return []
    return re.findall(r"#([^#\s]+)", text)


def analyze_viral_factors(content: Content) -> dict[str, Any]:
    """基于已有数据计算爆款因子分数（1-10）。"""
    likes = content.likes or 0
    comments = content.comments or 0
    shares = content.shares or 0
    views = content.views or 0
    collections = content.collections or 0

    factors = {}

    # 互动率因子
    engagement_rate = comments / likes if likes > 0 else 0
    factors["engagement_rate"] = round(engagement_rate, 4)
    factors["engagement_score"] = min(10, int(engagement_rate * 100))

    # 收藏率因子
    save_rate = collections / likes if likes > 0 else 0
    factors["save_rate"] = round(save_rate, 4)
    factors["save_score"] = min(10, int(save_rate * 100))

    # 传播率（分享/播放）
    share_rate = shares / views if views > 0 else 0
    factors["share_rate"] = round(share_rate, 4)
    factors["share_score"] = min(10, int(share_rate * 1000))

    # 标题质量
    title = content.title or ""
    factors["title_length"] = len(title)
    factors["hashtag_count"] = len(extract_hashtags(title + " " + (content.description or "")))
    factors["has_numbers"] = bool(re.search(r"\d", title))
    factors["title_score"] = min(10, max(4, 6 + factors["hashtag_count"] + (2 if factors["has_numbers"] else 0)))

    # 综合爆款分
    factors["viral_score"] = round(
        (
            factors["engagement_score"] * 0.35
            + factors["save_score"] * 0.25
            + factors["share_score"] * 0.2
            + factors["title_score"] * 0.2
        ),
        2,
    )

    return factors


def analyze_and_save(db: Session, content_id: int) -> dict[str, Any]:
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise ValueError("Content not found")
    factors = analyze_viral_factors(content)
    content.viral_factors = factors
    db.commit()
    db.refresh(content)
    return factors
