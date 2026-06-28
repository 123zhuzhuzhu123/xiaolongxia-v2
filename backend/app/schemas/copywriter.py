"""文案生产相关 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FormulaBase(BaseModel):
    formula_key: str
    name: str
    goal: str
    platform: str | None = None
    template: str
    description: str | None = None


class FormulaCreate(FormulaBase):
    project_id: int


class FormulaResponse(FormulaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    usage_count: int
    avg_score: float | None = None
    tags: list | None = None
    extra: dict | None = None
    created_at: datetime
    updated_at: datetime


class HookBase(BaseModel):
    hook_type: str
    text: str
    platform: str | None = None


class HookCreate(HookBase):
    project_id: int


class HookResponse(HookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    usage_count: int
    median_likes: int | None = None
    median_comments: int | None = None
    source_content_ids: list | None = None
    extra: dict | None = None
    created_at: datetime
    updated_at: datetime


class SkuBase(BaseModel):
    sku_name: str
    brand_name: str | None = None
    category: str | None = None
    selling_points: list | None = None
    marketing_brief: str | None = None
    price_range: str | None = None
    target_users: list | None = None


class SkuCreate(SkuBase):
    project_id: int


class SkuResponse(SkuBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    extra: dict | None = None
    created_at: datetime
    updated_at: datetime

