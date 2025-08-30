from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.supabase import (
    supabase_sign_up, 
    supabase_sign_in, 
    supabase_sign_out, 
    supabase_get_user,
    supabase_reset_password
)
from app.schemas.auth import (
    Token, 
    UserCreate, 
    UserLogin, 
    UserResponse, 
    PasswordReset,
    UserUpdate
)

router = APIRouter()
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from access token."""
    access_token = credentials.credentials
    user = await supabase_get_user(access_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate) -> Any:
    """
    Register a new user using Supabase authentication
    """
    try:
        # Prepare user metadata for Supabase
        user_metadata = {
            "full_name": user_data.full_name,
            "email": user_data.email
        }
        
        # Create user with Supabase
        result = await supabase_sign_up(
            email=user_data.email,
            password=user_data.password,
            user_data=user_metadata
        )
        
        # Extract user info and create response
        user = result["user"]
        
        # Check if session exists (user might need email confirmation)
        if result.get("session") and result.get("access_token"):
            return {
                "access_token": result["access_token"],
                "token_type": "bearer",
                "refresh_token": result["refresh_token"],
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user_data.full_name,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
            }
        else:
            # User created but needs email confirmation
            return {
                "access_token": None,
                "token_type": "bearer",
                "refresh_token": None,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user_data.full_name,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                },
                "message": result.get("message", "User created successfully. Please check your email for confirmation.")
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin) -> Any:
    """
    Sign in user using Supabase authentication
    """
    try:
        # Sign in with Supabase
        result = await supabase_sign_in(
            email=credentials.email,
            password=credentials.password
        )
        
        # Extract user info and create response
        user = result["user"]
        
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "refresh_token": result["refresh_token"],
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.user_metadata.get("full_name") if user.user_metadata else None,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Sign out current user
    """
    try:
        # Note: Supabase handles sign out automatically when token expires
        # This endpoint is mainly for client-side cleanup
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.user_metadata.get("full_name") if current_user.user_metadata else None,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/reset-password")
async def request_password_reset(reset_data: PasswordReset) -> dict:
    """
    Request password reset email
    """
    try:
        success = await supabase_reset_password(reset_data.email)
        if success:
            return {"message": "Password reset email sent"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset request failed: {str(e)}"
        )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
) -> UserResponse:
    """
    Update user profile information
    """
    try:
        # For now, return current user info
        # In a full implementation, you'd update the user metadata in Supabase
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=profile_data.full_name or current_user.user_metadata.get("full_name"),
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profile update failed: {str(e)}"
        )
