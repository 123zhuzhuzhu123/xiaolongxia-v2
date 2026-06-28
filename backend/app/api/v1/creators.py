"""创作者 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user_id, get_db
from app.schemas.creator import CreatorCreate, CreatorResponse, CreatorUpdate
from app.services import creator as creator_service
from app.services import project as project_service

router = APIRouter(prefix="/creators", tags=["creators"])


@router.post("", response_model=CreatorResponse)
def create_creator(
    obj: CreatorCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=obj.project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return creator_service.create_creator(db=db, obj=obj)


@router.get("", response_model=list[CreatorResponse])
def list_creators(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return creator_service.list_creators(db=db, project_id=project_id)


@router.get("/{creator_id}", response_model=CreatorResponse)
def get_creator(
    creator_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    creator = creator_service.get_creator(db=db, creator_id=creator_id)
    if not creator or creator.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator


@router.patch("/{creator_id}", response_model=CreatorResponse)
def update_creator(
    creator_id: int,
    obj: CreatorUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    creator = creator_service.get_creator(db=db, creator_id=creator_id)
    if not creator or creator.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator_service.update_creator(db=db, creator=creator, obj=obj)
