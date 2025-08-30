from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from datetime import datetime
import enum

from app.core.database import Base


class ContentType(str, enum.Enum):
    BLOG = "blog"
    COURSE = "course"
    VIDEO = "video"
    ARTICLE = "article"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class LearningContent(Base):
    __tablename__ = "learning_content"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content details
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    
    # Media and attachments
    featured_image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    attachments = Column(ARRAY(String), nullable=True)
    
    # Metadata
    tags = Column(ARRAY(String), nullable=True)
    difficulty_level = Column(String(50), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    is_premium = Column(Boolean, default=False)
    
    # SEO and visibility
    slug = Column(String(255), unique=True, nullable=True)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Publishing
    published_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="content")
    pathway_contents = relationship("PathwayContent", back_populates="content", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="content", cascade="all, delete-orphan")

    @classmethod
    async def get_by_slug(cls, db: AsyncSession, slug: str):
        """Get content by slug"""
        result = await db.execute(select(cls).where(cls.slug == slug))
        return result.scalar_one_or_none()

    @classmethod
    async def get_published_content(cls, db: AsyncSession, content_type: ContentType = None):
        """Get all published content, optionally filtered by type"""
        query = select(cls).where(cls.status == ContentStatus.PUBLISHED)
        if content_type:
            query = query.where(cls.content_type == content_type)
        
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_creator(cls, db: AsyncSession, creator_id: int):
        """Get content by creator"""
        result = await db.execute(select(cls).where(cls.creator_id == creator_id))
        return result.scalars().all()

    def is_published(self) -> bool:
        """Check if content is published"""
        return self.status == ContentStatus.PUBLISHED

    def is_premium_content(self) -> bool:
        """Check if content requires premium subscription"""
        return self.is_premium

    def __repr__(self):
        return f"<LearningContent(id={self.id}, title='{self.title}', type='{self.content_type}', status='{self.status}')>"
