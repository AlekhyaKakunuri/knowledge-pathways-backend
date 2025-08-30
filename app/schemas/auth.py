from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: Optional[str] = None
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    user: dict
    message: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: str


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str


class UserUpdate(BaseModel):
    """Schema for user profile update."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
