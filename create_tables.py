#!/usr/bin/env python3
"""
Database table creation script for Knowledge Pathways Backend
This script creates all necessary tables and relationships
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models import *  # Import all models


async def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        
        async with engine.begin() as conn:
            # Drop all tables first (for development)
            print("Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            
            # Create all tables
            print("Creating new tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ All tables created successfully!")
        
        # Print table information
        print("\n📊 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


async def main():
    """Main function"""
    print("🚀 Knowledge Pathways Backend - Database Setup")
    print("=" * 50)
    
    await create_tables()
    
    print("\n🎉 Database setup completed!")
    print("\nNext steps:")
    print("1. Update your .env file with database credentials")
    print("2. Run the backend: python start.py")
    print("3. Test the API endpoints")


if __name__ == "__main__":
    asyncio.run(main())
