from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.supabase import supabase_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Knowledge Pathways Backend...")
    
    # Initialize Supabase if configured
    if settings.USE_SUPABASE:
        print("🔧 Initializing Supabase connection...")
        if supabase_manager.is_available():
            print("✅ Supabase client ready")
        else:
            print("⚠️ Supabase not available")
    else:
        print("ℹ️ Using local database configuration")
    
    print("🎉 Backend startup complete!")
    yield
    
    # Shutdown
    print("🔄 Shutting down...")
    print("✅ Backend shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Knowledge Pathways Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Knowledge Pathways Backend API"}


@app.get("/health")
async def health_check():
    """Health check endpoint with Supabase status."""
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "database": {
            "type": "supabase" if settings.USE_SUPABASE else "local_postgresql",
            "status": "configured"
        }
    }
    
    # Add Supabase status if configured
    if settings.USE_SUPABASE:
        health_status["supabase"] = {
            "url": settings.SUPABASE_URL,
            "available": supabase_manager.is_available(),
            "connection_test": supabase_manager.test_connection() if supabase_manager.is_available() else False
        }
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
