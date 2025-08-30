from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.supabase import supabase_get_user
from app.schemas.user import UserResponse, UserUpdate

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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
) -> UserResponse:
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


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
) -> UserResponse:
    """
    Update current user information
    """
    # For now, return updated user info
    # In a full implementation, you'd update the user metadata in Supabase
    updated_full_name = user_update.full_name or current_user.user_metadata.get("full_name")
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=updated_full_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> UserResponse:
    """
    Get user by ID (only current user for now)
    """
    # For security, only allow users to access their own profile
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile"
        )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.user_metadata.get("full_name") if current_user.user_metadata else None,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
