"""采集任务业务逻辑。"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.crawl_job import CrawlJob
from app.schemas.crawl_job import CrawlJobCreate


def create_crawl_job(db: Session, obj: CrawlJobCreate) -> CrawlJob:
    job = CrawlJob(
        project_id=obj.project_id,
        platform=obj.platform,
        target_type=obj.target_type,
        target_value=obj.target_value,
        strategy=obj.strategy,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_crawl_job(db: Session, job_id: int) -> CrawlJob | None:
    return db.query(CrawlJob).filter(CrawlJob.id == job_id).first()


def list_crawl_jobs(
    db: Session, project_id: int, skip: int = 0, limit: int = 100
) -> list[CrawlJob]:
    return (
        db.query(CrawlJob)
        .filter(CrawlJob.project_id == project_id)
        .order_by(CrawlJob.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_job_status(
    db: Session,
    job: CrawlJob,
    status: str,
    items_crawled: int | None = None,
    result_summary: dict | None = None,
    error_message: str | None = None,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> CrawlJob:
    job.status = status
    if items_crawled is not None:
        job.items_crawled = items_crawled
    if result_summary is not None:
        job.result_summary = result_summary
    if error_message is not None:
        job.error_message = error_message
    if started_at is not None:
        job.started_at = started_at
    if finished_at is not None:
        job.finished_at = finished_at
    db.commit()
    db.refresh(job)
    return job
