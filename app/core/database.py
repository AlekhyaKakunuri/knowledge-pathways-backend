from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Determine database URL based on configuration
def get_database_url():
    if settings.USE_SUPABASE:
        # Use the constructed Supabase DATABASE_URL
        return settings.get_database_url()
    
    # Fallback to local database or custom DATABASE_URL
    # For local development, you might want to use a different URL
    return settings.get_database_url()

# Create async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
