"""采集任务 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CrawlJobBase(BaseModel):
    platform: str
    target_type: str
    target_value: str
    strategy: str = "content_detail"


class CrawlJobCreate(CrawlJobBase):
    project_id: int


class CrawlJobResponse(CrawlJobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    status: str
    error_message: str | None = None
    items_crawled: int | None = None
    result_summary: dict | None = None
    extra: dict | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
