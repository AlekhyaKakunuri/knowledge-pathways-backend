from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, pathways, content

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pathways.router, prefix="/pathways", tags=["knowledge pathways"])
api_router.include_router(content.router, prefix="/content", tags=["content management"])
