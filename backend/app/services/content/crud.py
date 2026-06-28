"""内容资产业务逻辑。"""
from sqlalchemy.orm import Session

from app.models.content import Comment, Content
from app.schemas.content import CommentCreate, ContentCreate, ContentUpdate


def create_content(db: Session, obj: ContentCreate) -> Content:
    existing = get_content_by_platform_id(
        db, obj.project_id, obj.platform, obj.platform_content_id
    )
    if existing:
        return existing
    content = Content(
        project_id=obj.project_id,
        creator_id=obj.creator_id,
        platform=obj.platform,
        platform_content_id=obj.platform_content_id,
        url=obj.url,
        title=obj.title,
        description=obj.description,
        content_type=obj.content_type,
        likes=obj.likes,
        comments=obj.comments,
        shares=obj.shares,
        views=obj.views,
        collections=obj.collections,
        cover_url=obj.cover_url,
        video_url=obj.video_url,
        published_at=obj.published_at,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def get_content(db: Session, content_id: int) -> Content | None:
    return db.query(Content).filter(Content.id == content_id).first()


def get_content_by_platform_id(
    db: Session, project_id: int, platform: str, platform_content_id: str
) -> Content | None:
    return (
        db.query(Content)
        .filter(
            Content.project_id == project_id,
            Content.platform == platform,
            Content.platform_content_id == platform_content_id,
        )
        .first()
    )


def list_contents(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> list[Content]:
    return (
        db.query(Content)
        .filter(Content.project_id == project_id)
        .order_by(Content.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_content(db: Session, content: Content, obj: ContentUpdate) -> Content:
    for field, value in obj.model_dump(exclude_unset=True).items():
        setattr(content, field, value)
    db.commit()
    db.refresh(content)
    return content


def create_comment(db: Session, obj: CommentCreate) -> Comment:
    comment = Comment(
        content_id=obj.content_id,
        platform_comment_id=obj.platform_comment_id,
        platform_user_id=obj.platform_user_id,
        nickname=obj.nickname,
        text=obj.text,
        likes=obj.likes,
        replies=obj.replies,
        intent=obj.intent,
        sentiment=obj.sentiment,
        confidence=obj.confidence,
        replied_at=obj.replied_at,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, content_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.content_id == content_id).all()
