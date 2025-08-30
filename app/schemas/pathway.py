from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.pathway import PathwayDifficulty


class PathwayBase(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty_level: PathwayDifficulty = PathwayDifficulty.BEGINNER
    estimated_duration: Optional[int] = None


class PathwayCreate(PathwayBase):
    pass


class PathwayUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[PathwayDifficulty] = None
    estimated_duration: Optional[int] = None


class PathwayResponse(PathwayBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
