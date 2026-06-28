"""基于评论的人群分层。"""
from sqlalchemy.orm import Session

from app.models.content import Comment


PERSONA_RULES = {
    ("buying", "positive"): "高意向购买者",
    ("buying", "neutral"): "潜在购买者",
    ("loyal", "positive"): "忠诚口碑传播者",
    ("loyal", "neutral"): "老用户",
    ("risk", "negative"): "风险厌恶者",
    ("risk", "neutral"): "谨慎观望者",
    ("question", "neutral"): "信息求证者",
    ("question", "positive"): "兴趣求证者",
    ("price", "negative"): "价格敏感者",
    ("price", "neutral"): "促销等待者",
    ("scene", "positive"): "场景共鸣者",
    ("scene", "neutral"): "场景观察者",
    ("other", "positive"): "泛好评用户",
    ("other", "negative"): "泛负面用户",
    ("other", "neutral"): "路人围观者",
}


def segment_audience_by_content(db: Session, content_id: int) -> dict:
    """基于单个内容的评论进行人群分层。"""
    comments = db.query(Comment).filter(Comment.content_id == content_id).all()

    segments = {}
    for c in comments:
        key = (c.intent or "other", c.sentiment or "neutral")
        persona = PERSONA_RULES.get(key, "未分类")
        segments[persona] = segments.get(persona, 0) + 1

    # 按人数排序
    sorted_segments = dict(sorted(segments.items(), key=lambda x: x[1], reverse=True))

    return {
        "content_id": content_id,
        "total_commenters": len(comments),
        "segments": sorted_segments,
    }


def segment_audience_by_project(db: Session, project_id: int) -> dict:
    """基于项目下所有评论进行人群分层。"""
    from app.models.content import Content

    comments = (
        db.query(Comment)
        .join(Content, Comment.content_id == Content.id)
        .filter(Content.project_id == project_id)
        .all()
    )

    segments = {}
    for c in comments:
        key = (c.intent or "other", c.sentiment or "neutral")
        persona = PERSONA_RULES.get(key, "未分类")
        segments[persona] = segments.get(persona, 0) + 1

    sorted_segments = dict(sorted(segments.items(), key=lambda x: x[1], reverse=True))

    return {
        "project_id": project_id,
        "total_commenters": len(comments),
        "segments": sorted_segments,
    }
