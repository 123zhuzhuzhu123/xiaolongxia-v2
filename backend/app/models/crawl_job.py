"""采集任务模型。"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    # 任务定义
    platform: Mapped[str] = mapped_column(String(20))  # douyin / xhs
    target_type: Mapped[str] = mapped_column(String(50))  # content / creator / keyword
    target_value: Mapped[str] = mapped_column(Text)  # url / creator_id / keyword
    strategy: Mapped[str] = mapped_column(String(50), default="content_detail")

    # 状态
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/running/completed/failed
    error_message: Mapped[str | None] = mapped_column(Text)

    # 结果摘要
    items_crawled: Mapped[int | None] = mapped_column(default=None)
    result_summary: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column()
    finished_at: Mapped[datetime | None] = mapped_column()
