"""创作者业务逻辑。"""
from sqlalchemy.orm import Session

from app.models.creator import Creator
from app.schemas.creator import CreatorCreate, CreatorUpdate


def create_creator(db: Session, obj: CreatorCreate) -> Creator:
    existing = get_creator_by_platform_id(
        db, obj.project_id, obj.platform, obj.platform_creator_id
    )
    if existing:
        return existing
    creator = Creator(
        project_id=obj.project_id,
        platform=obj.platform,
        platform_creator_id=obj.platform_creator_id,
        nickname=obj.nickname,
        avatar_url=obj.avatar_url,
        follower_count=obj.follower_count,
        following_count=obj.following_count,
        total_likes=obj.total_likes,
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)
    return creator


def get_creator(db: Session, creator_id: int) -> Creator | None:
    return db.query(Creator).filter(Creator.id == creator_id).first()


def get_creator_by_platform_id(
    db: Session, project_id: int, platform: str, platform_creator_id: str
) -> Creator | None:
    return (
        db.query(Creator)
        .filter(
            Creator.project_id == project_id,
            Creator.platform == platform,
            Creator.platform_creator_id == platform_creator_id,
        )
        .first()
    )


def list_creators(db: Session, project_id: int) -> list[Creator]:
    return db.query(Creator).filter(Creator.project_id == project_id).all()


def update_creator(db: Session, creator: Creator, obj: CreatorUpdate) -> Creator:
    for field, value in obj.model_dump(exclude_unset=True).items():
        setattr(creator, field, value)
    db.commit()
    db.refresh(creator)
    return creator
