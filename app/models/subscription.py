from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from datetime import datetime
import enum

from app.core.database import Base


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Subscription details
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    
    # Payment details
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="INR")
    
    # Dates
    subscription_start = Column(DateTime, default=datetime.utcnow)
    subscription_end = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payments = relationship("PaymentVerification", back_populates="subscription", cascade="all, delete-orphan")

    @classmethod
    async def get_by_user_id(cls, db: AsyncSession, user_id: int):
        """Get subscription by user ID"""
        result = await db.execute(select(cls).where(cls.user_id == user_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_active_subscriptions(cls, db: AsyncSession):
        """Get all active subscriptions"""
        result = await db.execute(
            select(cls).where(cls.subscription_status == SubscriptionStatus.ACTIVE)
        )
        return result.scalars().all()

    def is_active(self) -> bool:
        """Check if subscription is active"""
        if self.subscription_status != SubscriptionStatus.ACTIVE:
            return False
        
        if self.subscription_end and self.subscription_end < datetime.utcnow():
            return False
            
        return True

    def is_trial_active(self) -> bool:
        """Check if trial is still active"""
        if not self.trial_end:
            return False
        return self.trial_end > datetime.utcnow()

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier='{self.subscription_tier}', status='{self.subscription_status}')>"
