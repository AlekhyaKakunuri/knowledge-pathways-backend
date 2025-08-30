from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.content import LearningContent
from app.schemas.content import ContentCreate, ContentResponse, ContentUpdate

router = APIRouter()


@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new learning content
    """
    content = LearningContent(
        title=content_data.title,
        description=content_data.description,
        content_type=content_data.content_type,
        content_url=content_data.content_url,
        pathway_id=content_data.pathway_id,
        creator_id=current_user.id
    )
    
    db.add(content)
    await db.commit()
    await db.refresh(content)
    
    return content


@router.get("/", response_model=List[ContentResponse])
async def get_content(
    pathway_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get learning content, optionally filtered by pathway
    """
    if pathway_id:
        content_list = await LearningContent.get_by_pathway(db, pathway_id=pathway_id, skip=skip, limit=limit)
    else:
        content_list = await LearningContent.get_all(db, skip=skip, limit=limit)
    
    return content_list


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_by_id(
    content_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get specific learning content by ID
    """
    content = await LearningContent.get(db, id=content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_update: ContentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update learning content
    """
    content = await LearningContent.get(db, id=content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    if content.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this content"
        )
    
    if content_update.title is not None:
        content.title = content_update.title
    if content_update.description is not None:
        content.description = content_update.description
    if content_update.content_type is not None:
        content.content_type = content_update.content_type
    if content_update.content_url is not None:
        content.content_url = content_update.content_url
    
    await db.commit()
    await db.refresh(content)
    
    return content


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete learning content
    """
    content = await LearningContent.get(db, id=content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    if content.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this content"
        )
    
    await db.delete(content)
    await db.commit()
    
    return {"message": "Content deleted successfully"}
