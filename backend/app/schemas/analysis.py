"""分析相关 Schema。"""
from pydantic import BaseModel


class CommentIntentRequest(BaseModel):
    content_id: int


class CommentIntentResponse(BaseModel):
    content_id: int
    analyzed: int
    intent_counts: dict
    sentiment_counts: dict


class ViralFactorsResponse(BaseModel):
    content_id: int
    factors: dict


class CreatorVoiceResponse(BaseModel):
    creator_id: int
    voice_profile: dict


class AudienceSegmentResponse(BaseModel):
    content_id: int | None = None
    project_id: int | None = None
    total_commenters: int
    segments: dict
