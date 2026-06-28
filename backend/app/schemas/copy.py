"""文案生成相关 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CopyGenerateRequest(BaseModel):
    project_id: int
    sku_id: int | None = None
    goal: str = "conversion"
    platform: str = "douyin"


class CopyVersionResponse(BaseModel):
    id: int
    draft_id: int
    formula_key: str
    title: str | None
    body: str
    scores: dict | None
    quality_review: dict | None
    evidence: dict | None
    extra: dict | None
    selected: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CopyDraftResponse(BaseModel):
    id: int
    project_id: int
    creator_id: int | None
    sku_id: int | None
    goal: str
    platform: str
    topic: str | None
    original_copy: str | None
    extra: dict | None
    created_at: datetime
    updated_at: datetime
    versions: list[CopyVersionResponse]

    model_config = ConfigDict(from_attributes=True)


class CopyScoreResponse(BaseModel):
    version_id: int
    quality_review: dict


class StoryboardResponse(BaseModel):
    version_id: int
    storyboard: dict
