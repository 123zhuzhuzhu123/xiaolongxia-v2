"""文案生成模型。"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CopyDraft(Base):
    __tablename__ = "copy_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    creator_id: Mapped[int | None] = mapped_column(
        ForeignKey("creators.id"), nullable=True
    )
    sku_id: Mapped[int | None] = mapped_column(ForeignKey("skus.id"), nullable=True)

    goal: Mapped[str] = mapped_column(String(20))
    platform: Mapped[str] = mapped_column(String(20))
    topic: Mapped[str | None] = mapped_column(Text)
    original_copy: Mapped[str | None] = mapped_column(Text)

    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship("Project", lazy="selectin")
    creator: Mapped["Creator | None"] = relationship("Creator", lazy="selectin")
    sku: Mapped["Sku | None"] = relationship("Sku", lazy="selectin")
    versions: Mapped[list["CopyVersion"]] = relationship(
        "CopyVersion", back_populates="draft", lazy="selectin"
    )


class CopyVersion(Base):
    __tablename__ = "copy_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("copy_drafts.id"))

    formula_key: Mapped[str] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)

    scores: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    quality_review: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    evidence: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    selected: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    draft: Mapped["CopyDraft"] = relationship("CopyDraft", back_populates="versions")
