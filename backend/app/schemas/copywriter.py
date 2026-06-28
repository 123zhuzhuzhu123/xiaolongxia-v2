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
    created_at: datetime
    updated_at: datetime


class CopyGenerateRequest(BaseModel):
    project_id: int
    creator_id: int
    sku_id: int | None = None
    goal: str = "conversion"  # conversion / engagement / brand
    platform: str = "douyin"
    topic: str | None = None
    version_count: int = 3


class CopyVersionResponse(BaseModel):
    id: int
    draft_id: int
    formula_key: str
    title: str | None = None
    body: str
    scores: dict
    quality_review: dict | None = None
    created_at: datetime


class StoryboardGenerateRequest(BaseModel):
    copy_version_id: int
    duration: int = 15


class StoryboardResponse(BaseModel):
    id: int
    copy_version_id: int
    shots: list
    created_at: datetime
