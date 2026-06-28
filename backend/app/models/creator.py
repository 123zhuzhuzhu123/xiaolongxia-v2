"""创作者模型。"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.content import Content
    from app.models.project import Project


class Creator(Base):
    __tablename__ = "creators"
    __table_args__ = (
        UniqueConstraint("project_id", "platform", "platform_creator_id", name="uq_creator_platform"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    # 平台信息
    platform: Mapped[str] = mapped_column(String(20), index=True)  # douyin / xhs
    platform_creator_id: Mapped[str] = mapped_column(String(100), index=True)
    nickname: Mapped[str | None] = mapped_column(String(200))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    follower_count: Mapped[int | None] = mapped_column(default=None)
    following_count: Mapped[int | None] = mapped_column(default=None)
    total_likes: Mapped[int | None] = mapped_column(default=None)

    # 画像元数据
    persona: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    voice_exemplars: Mapped[list | None] = mapped_column(JSONB, default=list)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship("Project", back_populates="creators")
    contents: Mapped[list["Content"]] = relationship(
        "Content", back_populates="creator", lazy="selectin"
    )
