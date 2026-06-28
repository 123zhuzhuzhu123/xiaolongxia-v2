"""SKU 商品库模型。"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Sku(Base):
    __tablename__ = "skus"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    sku_name: Mapped[str] = mapped_column(String(200))
    brand_name: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(100))
    selling_points: Mapped[list | None] = mapped_column(JSONB, default=list)
    marketing_brief: Mapped[str | None] = mapped_column(Text)
    price_range: Mapped[str | None] = mapped_column(String(50))
    target_users: Mapped[list | None] = mapped_column(JSONB, default=list)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship("Project")
