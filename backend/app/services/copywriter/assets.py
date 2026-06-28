"""文案生产资产服务：Formula / Hook / Sku。"""
from sqlalchemy.orm import Session

from app.models.formula import Formula
from app.models.hook import Hook
from app.models.sku import Sku
from app.schemas.copywriter import FormulaCreate, HookCreate, SkuCreate


def create_formula(db: Session, obj: FormulaCreate) -> Formula:
    formula = Formula(
        project_id=obj.project_id,
        formula_key=obj.formula_key,
        name=obj.name,
        goal=obj.goal,
        platform=obj.platform,
        template=obj.template,
        description=obj.description,
    )
    db.add(formula)
    db.commit()
    db.refresh(formula)
    return formula


def list_formulas(db: Session, project_id: int, goal: str | None = None) -> list[Formula]:
    q = db.query(Formula).filter(Formula.project_id == project_id)
    if goal:
        q = q.filter(Formula.goal == goal)
    return q.order_by(Formula.avg_score.desc()).all()


def get_formula(db: Session, formula_id: int) -> Formula | None:
    return db.query(Formula).filter(Formula.id == formula_id).first()


def create_hook(db: Session, obj: HookCreate) -> Hook:
    hook = Hook(
        project_id=obj.project_id,
        hook_type=obj.hook_type,
        text=obj.text,
        platform=obj.platform,
    )
    db.add(hook)
    db.commit()
    db.refresh(hook)
    return hook


def list_hooks(db: Session, project_id: int, hook_type: str | None = None) -> list[Hook]:
    q = db.query(Hook).filter(Hook.project_id == project_id)
    if hook_type:
        q = q.filter(Hook.hook_type == hook_type)
    return q.order_by(Hook.median_likes.desc()).all()


def create_sku(db: Session, obj: SkuCreate) -> Sku:
    sku = Sku(
        project_id=obj.project_id,
        sku_name=obj.sku_name,
        brand_name=obj.brand_name,
        category=obj.category,
        selling_points=obj.selling_points,
        marketing_brief=obj.marketing_brief,
        price_range=obj.price_range,
        target_users=obj.target_users,
    )
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku


def list_skus(db: Session, project_id: int) -> list[Sku]:
    return db.query(Sku).filter(Sku.project_id == project_id).all()


def get_sku(db: Session, sku_id: int) -> Sku | None:
    return db.query(Sku).filter(Sku.id == sku_id).first()
