"""内容与评论模型。"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.creator import Creator
    from app.models.project import Project


class Content(Base):
    __tablename__ = "contents"
    __table_args__ = (
        UniqueConstraint("project_id", "platform", "platform_content_id", name="uq_content_platform"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    creator_id: Mapped[int | None] = mapped_column(
        ForeignKey("creators.id"), nullable=True
    )

    # 平台信息
    platform: Mapped[str] = mapped_column(String(20), index=True)
    platform_content_id: Mapped[str] = mapped_column(String(100), index=True)
    url: Mapped[str | None] = mapped_column(String(500))
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[str | None] = mapped_column(String(20))  # video / image_text

    # 互动数据
    likes: Mapped[int | None] = mapped_column(default=None)
    comments: Mapped[int | None] = mapped_column(default=None)
    shares: Mapped[int | None] = mapped_column(default=None)
    views: Mapped[int | None] = mapped_column(default=None)
    collections: Mapped[int | None] = mapped_column(default=None)

    # 媒体
    cover_url: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(Text)
    local_cover_path: Mapped[str | None] = mapped_column(Text)
    local_video_path: Mapped[str | None] = mapped_column(Text)

    # 时间
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    crawled_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # 分析结果
    transcript: Mapped[str | None] = mapped_column(Text)
    viral_factors: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship("Project", back_populates="contents")
    creator: Mapped["Creator | None"] = relationship("Creator", back_populates="contents")
    comment_items: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="content", lazy="selectin"
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"))

    platform_comment_id: Mapped[str | None] = mapped_column(String(100))
    platform_user_id: Mapped[str | None] = mapped_column(String(100))
    nickname: Mapped[str | None] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text)
    likes: Mapped[int | None] = mapped_column(default=None)
    replies: Mapped[int | None] = mapped_column(default=None)

    # 语义分析结果
    intent: Mapped[str | None] = mapped_column(String(50))  # buying/risk/loyal/question/price/scene
    sentiment: Mapped[str | None] = mapped_column(String(20))  # positive/negative/neutral
    confidence: Mapped[float | None] = mapped_column(default=None)

    # 元数据
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    crawled_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    content: Mapped["Content"] = relationship("Content", back_populates="comment_items")
