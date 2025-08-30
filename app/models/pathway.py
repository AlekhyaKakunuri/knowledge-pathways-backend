from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, ARRAY, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from datetime import datetime
import enum

from app.core.database import Base


class PathwayDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PathwayStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class KnowledgePathway(Base):
    __tablename__ = "knowledge_pathways"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Pathway details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(Enum(PathwayDifficulty), default=PathwayDifficulty.BEGINNER)
    status = Column(Enum(PathwayStatus), default=PathwayStatus.DRAFT)
    
    # Content organization
    estimated_duration = Column(Integer, nullable=True)  # in hours
    total_modules = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)
    
    # Media and branding
    cover_image_url = Column(String(500), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # SEO and visibility
    slug = Column(String(255), unique=True, nullable=True)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Publishing
    published_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="pathways")
    pathway_contents = relationship("PathwayContent", back_populates="pathway", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="pathway", cascade="all, delete-orphan")

    @classmethod
    async def get_by_slug(cls, db: AsyncSession, slug: str):
        """Get pathway by slug"""
        result = await db.execute(select(cls).where(cls.slug == slug))
        return result.scalar_one_or_none()

    @classmethod
    async def get_published_pathways(cls, db: AsyncSession):
        """Get all published pathways"""
        result = await db.execute(select(cls).where(cls.status == PathwayStatus.PUBLISHED))
        return result.scalars().all()

    @classmethod
    async def get_by_creator(cls, db: AsyncSession, creator_id: int):
        """Get pathways by creator"""
        result = await db.execute(select(cls).where(cls.creator_id == creator_id))
        return result.scalars().all()

    def is_published(self) -> bool:
        """Check if pathway is published"""
        return self.status == PathwayStatus.PUBLISHED

    def __repr__(self):
        return f"<KnowledgePathway(id={self.id}, title='{self.title}', difficulty='{self.difficulty_level}', status='{self.status}')>"


class PathwayContent(Base):
    __tablename__ = "pathway_contents"

    id = Column(Integer, primary_key=True, index=True)
    pathway_id = Column(Integer, ForeignKey("knowledge_pathways.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("learning_content.id"), nullable=False)
    
    # Content ordering within pathway
    order_index = Column(Integer, default=0)
    is_required = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pathway = relationship("KnowledgePathway", back_populates="pathway_contents")
    content = relationship("LearningContent", back_populates="pathway_contents")

    @classmethod
    async def get_by_pathway(cls, db: AsyncSession, pathway_id: int):
        """Get all content for a pathway, ordered by order_index"""
        result = await db.execute(
            select(cls).where(cls.pathway_id == pathway_id).order_by(cls.order_index)
        )
        return result.scalars().all()

    def __repr__(self):
        return f"<PathwayContent(pathway_id={self.pathway_id}, content_id={self.content_id}, order={self.order_index})>"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pathway_id = Column(Integer, ForeignKey("knowledge_pathways.id"), nullable=True)
    content_id = Column(Integer, ForeignKey("learning_content.id"), nullable=True)
    
    # Enrollment details
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    progress_percentage = Column(Numeric(5, 2), default=0.0)  # 0.00 to 100.00
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="enrollments")
    pathway = relationship("KnowledgePathway", back_populates="enrollments")
    content = relationship("LearningContent", back_populates="enrollments")

    @classmethod
    async def get_by_user(cls, db: AsyncSession, user_id: int):
        """Get all enrollments for a user"""
        result = await db.execute(select(cls).where(cls.user_id == user_id))
        return result.scalars().all()

    @classmethod
    async def get_by_pathway(cls, db: AsyncSession, pathway_id: int):
        """Get all enrollments for a pathway"""
        result = await db.execute(select(cls).where(cls.pathway_id == pathway_id))
        return result.scalars().all()

    def is_completed(self) -> bool:
        """Check if enrollment is completed"""
        return self.completed_at is not None

    def __repr__(self):
        return f"<Enrollment(user_id={self.user_id}, pathway_id={self.pathway_id}, progress={self.progress_percentage}%)>"
