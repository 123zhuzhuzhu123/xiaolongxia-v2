"""项目 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user_id, get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
def create_project(
    obj: ProjectCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    return project_service.create_project(db=db, obj=obj, owner_id=user_id)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    return project_service.list_projects(db=db, owner_id=user_id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    obj: ProjectUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_service.update_project(db=db, project=project, obj=obj)
