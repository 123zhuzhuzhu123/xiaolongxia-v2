"""爆款公式模型。"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Formula(Base):
    __tablename__ = "formulas"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    formula_key: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(100))
    goal: Mapped[str] = mapped_column(String(20))  # conversion / engagement / brand
    platform: Mapped[str | None] = mapped_column(String(20))
    template: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)

    # 验证数据
    usage_count: Mapped[int] = mapped_column(default=0)
    avg_score: Mapped[float | None] = mapped_column(default=None)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship("Project")
