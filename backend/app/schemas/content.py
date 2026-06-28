"""内容与评论 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    platform_comment_id: str | None = None
    platform_user_id: str | None = None
    nickname: str | None = None
    text: str
    likes: int | None = None
    replies: int | None = None
    intent: str | None = None
    sentiment: str | None = None
    confidence: float | None = None
    extra: dict | None = None


class CommentCreate(CommentBase):
    content_id: int


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    replied_at: datetime | None = None
    crawled_at: datetime


class ContentBase(BaseModel):
    platform: str
    platform_content_id: str
    url: str | None = None
    title: str | None = None
    description: str | None = None
    content_type: str | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    views: int | None = None
    collections: int | None = None
    cover_url: str | None = None
    video_url: str | None = None
    published_at: datetime | None = None


class ContentCreate(ContentBase):
    project_id: int
    creator_id: int | None = None


class ContentUpdate(BaseModel):
    title: str | None = None
    likes: int | None = None
    comments: int | None = None
    transcript: str | None = None
    viral_factors: dict | None = None


class ContentResponse(ContentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    creator_id: int | None = None
    transcript: str | None = None
    viral_factors: dict | None = None
    extra: dict | None = None
    crawled_at: datetime
    created_at: datetime
    updated_at: datetime
    comment_items: list[CommentResponse] = []
