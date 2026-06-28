"""文案生产资产 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user_id, get_db
from app.schemas.copywriter import (
    FormulaCreate,
    FormulaResponse,
    HookCreate,
    HookResponse,
    SkuCreate,
    SkuResponse,
)
from app.services import project as project_service
from app.services.copywriter import assets

router = APIRouter(prefix="/copywriter", tags=["copywriter"])


@router.post("/formulas", response_model=FormulaResponse)
def create_formula(
    obj: FormulaCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=obj.project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return assets.create_formula(db=db, obj=obj)


@router.get("/formulas", response_model=list[FormulaResponse])
def list_formulas(
    project_id: int,
    goal: str | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return assets.list_formulas(db=db, project_id=project_id, goal=goal)


@router.post("/hooks", response_model=HookResponse)
def create_hook(
    obj: HookCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=obj.project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return assets.create_hook(db=db, obj=obj)


@router.get("/hooks", response_model=list[HookResponse])
def list_hooks(
    project_id: int,
    hook_type: str | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return assets.list_hooks(db=db, project_id=project_id, hook_type=hook_type)


@router.post("/skus", response_model=SkuResponse)
def create_sku(
    obj: SkuCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=obj.project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return assets.create_sku(db=db, obj=obj)


@router.get("/skus", response_model=list[SkuResponse])
def list_skus(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_active_user_id),
):
    project = project_service.get_project(db=db, project_id=project_id)
    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return assets.list_skus(db=db, project_id=project_id)
