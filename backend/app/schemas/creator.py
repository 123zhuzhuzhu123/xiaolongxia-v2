"""创作者 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreatorBase(BaseModel):
    platform: str
    platform_creator_id: str
    nickname: str | None = None
    avatar_url: str | None = None
    follower_count: int | None = None
    following_count: int | None = None
    total_likes: int | None = None


class CreatorCreate(CreatorBase):
    project_id: int


class CreatorUpdate(BaseModel):
    nickname: str | None = None
    follower_count: int | None = None
    total_likes: int | None = None
    persona: dict | None = None
    voice_exemplars: list | None = None


class CreatorResponse(CreatorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
