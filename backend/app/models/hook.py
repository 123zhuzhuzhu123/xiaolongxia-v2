"""高赞钩子库模型。"""
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Hook(Base):
    __tablename__ = "hooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    hook_type: Mapped[str] = mapped_column(String(50))  # pain / result / question / story / scarcity
    text: Mapped[str] = mapped_column(Text)
    platform: Mapped[str | None] = mapped_column(String(20))

    # 验证数据
    usage_count: Mapped[int] = mapped_column(default=0)
    median_likes: Mapped[int | None] = mapped_column(Integer)
    median_comments: Mapped[int | None] = mapped_column(Integer)
    source_content_ids: Mapped[list | None] = mapped_column(JSONB, default=list)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship("Project")
