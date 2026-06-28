"""分析 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user_id, get_db
from app.schemas.analysis import (
    AudienceSegmentResponse,
    CommentIntentRequest,
    CommentIntentResponse,
    CreatorVoiceResponse,
    ViralFactorsResponse,
)
from app.services import content as content_service
from app.services.comment.batch import analyze_content_comments
from app.services.content.viral_factors import analyze_and_save as analyze_viral
from app.services.creator import voice as voice_service
from app.services import creator as creator_service
from app.services.comment.audience import (
    segment_audience_by_content,
    segment_audience_by_project,
)
from app.services import project as project_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/comment-intent", response_model=CommentIntentResponse)
def analyze_comments(
    obj: CommentIntentRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    content = content_service.get_content(db=db, content_id=obj.content_id)
    if not content or content.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Content not found")
    result = analyze_content_comments(db=db, content_id=obj.content_id)
    return {
        "content_id": obj.content_id,
        "analyzed": result["analyzed"],
        "intent_counts": result["intent_counts"],
        "sentiment_counts": result["sentiment_counts"],
    }


@router.post("/viral-factors/{content_id}", response_model=ViralFactorsResponse)
def viral_factors(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    content = content_service.get_content(db=db, content_id=content_id)
    if not content or content.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Content not found")
    factors = analyze_viral(db=db, content_id=content_id)
    return {"content_id": content_id, "factors": factors}


@router.post("/creator-voice/{creator_id}", response_model=CreatorVoiceResponse)
def creator_voice(
    creator_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    creator = creator_service.get_creator(db=db, creator_id=creator_id)
    if not creator or creator.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Creator not found")
    profile = voice_service.extract_voice_profile(db=db, creator_id=creator_id)
    return {"creator_id": creator_id, "voice_profile": profile}


@router.get("/audience/content/{content_id}", response_model=AudienceSegmentResponse)
def audience_by_content(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    content = content_service.get_content(db=db, content_id=content_id)
    if not content or content.project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Content not found")
    return segment_audience_by_content(db=db, content_id=content_id)


@router.get("/audience/project/{project_id}", response_model=AudienceSegmentResponse)
def audience_by_project(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return segment_audience_by_project(db=db, project_id=project_id)
