from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from datetime import datetime
import enum

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PaymentMethod(str, enum.Enum):
    UPI = "upi"
    CARD = "card"
    NET_BANKING = "net_banking"
    WALLET = "wallet"


class PaymentVerification(Base):
    __tablename__ = "payment_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    # Payment details
    transaction_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="INR")
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.UPI)
    
    # Plan details
    plan_name = Column(String(255), nullable=False)
    
    # Payment verification
    payment_screenshot = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Verification details
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payments", foreign_keys=[user_id])
    subscription = relationship("Subscription", back_populates="payments")
    verifier = relationship("User", foreign_keys=[verified_by])

    @classmethod
    async def get_by_transaction_id(cls, db: AsyncSession, transaction_id: str):
        """Get payment by transaction ID"""
        result = await db.execute(select(cls).where(cls.transaction_id == transaction_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_pending_verifications(cls, db: AsyncSession):
        """Get all pending payment verifications"""
        result = await db.execute(
            select(cls).where(cls.status == PaymentStatus.PENDING)
        )
        return result.scalars().all()

    @classmethod
    async def get_by_user_id(cls, db: AsyncSession, user_id: int):
        """Get payments by user ID"""
        result = await db.execute(select(cls).where(cls.user_id == user_id))
        return result.scalars().all()

    def can_be_verified(self) -> bool:
        """Check if payment can be verified"""
        return self.status == PaymentStatus.PENDING

    def __repr__(self):
        return f"<PaymentVerification(id={self.id}, transaction_id='{self.transaction_id}', amount={self.amount}, status='{self.status}')>"
