"""采集任务 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user_id, get_db
from app.schemas.crawl_job import CrawlJobCreate, CrawlJobResponse
from app.services import project as project_service
from app.services.ingestion.crawl_job import create_crawl_job, get_crawl_job, list_crawl_jobs
from app.services.ingestion.sync import run_crawl_job

router = APIRouter(prefix="/crawl-jobs", tags=["crawl-jobs"])


@router.post("", response_model=CrawlJobResponse)
def create_job(
    obj: CrawlJobCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=obj.project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    job = create_crawl_job(db=db, obj=obj)
    # MVP 阶段同步执行，后续改为后台任务
    return run_crawl_job(db=db, job=job)


@router.get("", response_model=list[CrawlJobResponse])
def list_jobs(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return list_crawl_jobs(db=db, project_id=project_id, skip=skip, limit=limit)


@router.get("/{job_id}", response_model=CrawlJobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    job = get_crawl_job(db=db, job_id=job_id)
    if not job or job.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
