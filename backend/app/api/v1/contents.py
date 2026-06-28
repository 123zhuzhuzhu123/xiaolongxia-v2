"""内容资产 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user_id, get_db
from app.schemas.content import (
    CommentCreate,
    CommentResponse,
    ContentCreate,
    ContentResponse,
    ContentUpdate,
)
from app.services import content as content_service
from app.services import project as project_service

router = APIRouter(prefix="/contents", tags=["contents"])


@router.post("", response_model=ContentResponse)
def create_content(
    obj: ContentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=obj.project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return content_service.create_content(db=db, obj=obj)


@router.get("", response_model=list[ContentResponse])
def list_contents(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return content_service.list_contents(
        db=db, project_id=project_id, skip=skip, limit=limit
    )


@router.get("/{content_id}", response_model=ContentResponse)
def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    content = content_service.get_content(db=db, content_id=content_id)
    if not content or content.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.patch("/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    obj: ContentUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    content = content_service.get_content(db=db, content_id=content_id)
    if not content or content.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Content not found")
    return content_service.update_content(db=db, content=content, obj=obj)


@router.post("/{content_id}/comments", response_model=CommentResponse)
def create_comment(
    content_id: int,
    obj: CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    content = content_service.get_content(db=db, content_id=content_id)
    if not content or content.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Content not found")
    return content_service.create_comment(
        db=db, obj=CommentCreate(**obj.model_dump(), content_id=content_id)
    )
