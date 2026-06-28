"""批量评论分析。"""
from sqlalchemy.orm import Session

from app.models.content import Comment
from app.services.comment.intent import analyze_comment_intent


def analyze_content_comments(db: Session, content_id: int) -> dict:
    """分析一个内容下的所有未分析评论，返回统计摘要。

    Returns:
        {"analyzed": int, "intent_counts": dict, "sentiment_counts": dict}
    """
    comments = (
        db.query(Comment)
        .filter(Comment.content_id == content_id, Comment.intent.is_(None))
        .all()
    )

    intent_counts = {}
    sentiment_counts = {}
    analyzed = 0

    for comment in comments:
        result = analyze_comment_intent(comment.text)
        comment.intent = result["intent"]
        comment.sentiment = result["sentiment"]
        comment.confidence = result["confidence"]
        analyzed += 1

        intent_counts[result["intent"]] = intent_counts.get(result["intent"], 0) + 1
        sentiment_counts[result["sentiment"]] = sentiment_counts.get(result["sentiment"], 0) + 1

    db.commit()

    return {
        "analyzed": analyzed,
        "intent_counts": intent_counts,
        "sentiment_counts": sentiment_counts,
    }
