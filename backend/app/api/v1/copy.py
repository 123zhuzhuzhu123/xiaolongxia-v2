"""文案生成与质量门控 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user_id, get_db
from app.models.copy import CopyDraft, CopyVersion
from app.schemas.copy import (
    CopyDraftResponse,
    CopyGenerateRequest,
    CopyScoreResponse,
    CopyVersionResponse,
    StoryboardResponse,
)
from app.services import content as content_service
from app.services import project as project_service
from app.services.copy.generation import generate_copy
from app.services.copy.quality import score_version
from app.services.copy.storyboard import generate_storyboard

router = APIRouter(prefix="/copy", tags=["copy"])


def _check_project(db: Session, project_id: int, user_id: int):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _check_draft(db: Session, draft_id: int, user_id: int) -> CopyDraft:
    draft = db.query(CopyDraft).filter(CopyDraft.id == draft_id).first()
    if not draft or draft.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


def _check_version(db: Session, version_id: int, user_id: int) -> CopyVersion:
    version = db.query(CopyVersion).filter(CopyVersion.id == version_id).first()
    if not version or version.draft.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post("/generate/{content_id}", response_model=CopyDraftResponse)
def generate_copy_endpoint(
    content_id: int,
    req: CopyGenerateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    content = content_service.get_content(db=db, content_id=content_id)
    if not content or content.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Content not found")
    _check_project(db=db, project_id=req.project_id, user_id=user_id)
    try:
        draft = generate_copy(
            db=db,
            content_id=content_id,
            project_id=req.project_id,
            goal=req.goal,
            platform=req.platform,
            sku_id=req.sku_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return draft


@router.get("/drafts", response_model=list[CopyDraftResponse])
def list_drafts(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    _check_project(db=db, project_id=project_id, user_id=user_id)
    drafts = (
        db.query(CopyDraft)
        .filter(CopyDraft.project_id == project_id)
        .order_by(CopyDraft.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return drafts


@router.get("/drafts/{draft_id}", response_model=CopyDraftResponse)
def get_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    return _check_draft(db=db, draft_id=draft_id, user_id=user_id)


@router.get("/drafts/{draft_id}/versions", response_model=list[CopyVersionResponse])
def list_versions(
    draft_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    draft = _check_draft(db=db, draft_id=draft_id, user_id=user_id)
    return draft.versions


@router.post("/versions/{version_id}/score", response_model=CopyScoreResponse)
def score_version_endpoint(
    version_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    version = _check_version(db=db, version_id=version_id, user_id=user_id)
    try:
        review = score_version(db=db, version_id=version.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"version_id": version.id, "quality_review": review}


@router.post("/versions/{version_id}/storyboard", response_model=StoryboardResponse)
def generate_storyboard_endpoint(
    version_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    version = _check_version(db=db, version_id=version_id, user_id=user_id)
    try:
        storyboard = generate_storyboard(db=db, version_id=version.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"version_id": version.id, "storyboard": storyboard}


@router.post("/versions/{version_id}/select", response_model=CopyVersionResponse)
def select_version(
    version_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    version = _check_version(db=db, version_id=version_id, user_id=user_id)
    version.selected = True
    db.commit()
    db.refresh(version)
    return version
