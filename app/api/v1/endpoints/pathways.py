from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.pathway import KnowledgePathway
from app.schemas.pathway import PathwayCreate, PathwayResponse, PathwayUpdate

router = APIRouter()


@router.post("/", response_model=PathwayResponse)
async def create_pathway(
    pathway_data: PathwayCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new knowledge pathway
    """
    pathway = KnowledgePathway(
        title=pathway_data.title,
        description=pathway_data.description,
        difficulty_level=pathway_data.difficulty_level,
        estimated_duration=pathway_data.estimated_duration,
        creator_id=current_user.id
    )
    
    db.add(pathway)
    await db.commit()
    await db.refresh(pathway)
    
    return pathway


@router.get("/", response_model=List[PathwayResponse])
async def get_pathways(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all knowledge pathways
    """
    pathways = await KnowledgePathway.get_all(db, skip=skip, limit=limit)
    return pathways


@router.get("/{pathway_id}", response_model=PathwayResponse)
async def get_pathway(
    pathway_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific knowledge pathway
    """
    pathway = await KnowledgePathway.get(db, id=pathway_id)
    if not pathway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pathway not found"
        )
    
    return pathway


@router.put("/{pathway_id}", response_model=PathwayResponse)
async def update_pathway(
    pathway_id: int,
    pathway_update: PathwayUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a knowledge pathway
    """
    pathway = await KnowledgePathway.get(db, id=pathway_id)
    if not pathway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pathway not found"
        )
    
    if pathway.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this pathway"
        )
    
    if pathway_update.title is not None:
        pathway.title = pathway_update.title
    if pathway_update.description is not None:
        pathway.description = pathway_update.description
    if pathway_update.difficulty_level is not None:
        pathway.difficulty_level = pathway_update.difficulty_level
    if pathway_update.estimated_duration is not None:
        pathway.estimated_duration = pathway_update.estimated_duration
    
    await db.commit()
    await db.refresh(pathway)
    
    return pathway


@router.delete("/{pathway_id}")
async def delete_pathway(
    pathway_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete a knowledge pathway
    """
    pathway = await KnowledgePathway.get(db, id=pathway_id)
    if not pathway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pathway not found"
        )
    
    if pathway.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this pathway"
        )
    
    await db.delete(pathway)
    await db.commit()
    
    return {"message": "Pathway deleted successfully"}
