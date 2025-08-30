from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.content import ContentType


class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    content_url: Optional[str] = None
    pathway_id: int


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    content_url: Optional[str] = None
    order_index: Optional[int] = None


class ContentResponse(ContentBase):
    id: int
    creator_id: int
    order_index: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
