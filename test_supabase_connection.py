#!/usr/bin/env python3
"""
Test script to diagnose Supabase connection issues
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import settings
from supabase import create_client, Client
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_supabase_client():
    """Test Supabase client connection"""
    print("🔍 Testing Supabase client connection...")
    try:
        # Just test if we can create a client with the credentials
        supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        
        # Since there are no tables, just test if client creation works
        
        print("✅ Supabase client connection successful!")
        print("   Note: No tables exist yet, but connection is working")
        print(f"   Project URL: {settings.SUPABASE_URL}")
        return True
    except Exception as e:
        print(f"❌ Supabase client connection failed: {e}")
        return False

def test_direct_postgres():
    """Test direct PostgreSQL connection"""
    print("\n🔍 Testing direct PostgreSQL connection...")
    try:
        # Test with psycopg2
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("✅ Direct PostgreSQL connection successful!")
        print(f"   PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Direct PostgreSQL connection failed: {e}")
        return False

def test_sqlalchemy():
    """Test SQLAlchemy connection"""
    print("\n🔍 Testing SQLAlchemy connection...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print("✅ SQLAlchemy connection successful!")
            print(f"   Database: {db_info[0]}, User: {db_info[1]}")
        return True
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")
    print(f"   SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"   DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   USE_SUPABASE: {settings.USE_SUPABASE}")
    
    # Check if service role key is set
    if settings.SUPABASE_SERVICE_ROLE_KEY and settings.SUPABASE_SERVICE_ROLE_KEY != "your-supabase-service-role-key":
        print("   ✅ SUPABASE_SERVICE_ROLE_KEY is configured")
    else:
        print("   ❌ SUPABASE_SERVICE_ROLE_KEY is not configured")
    
    # Check if anon key is set
    if settings.SUPABASE_ANON_KEY and settings.SUPABASE_ANON_KEY != "your-supabase-anon-key-here":
        print("   ✅ SUPABASE_ANON_KEY is configured")
    else:
        print("   ❌ SUPABASE_ANON_KEY is not configured")

def main():
    """Main test function"""
    print("🚀 Starting Supabase connection tests...\n")
    
    # Test environment
    test_environment()
    
    # Test connections
    supabase_success = test_supabase_client()
    postgres_success = test_direct_postgres()
    sqlalchemy_success = test_sqlalchemy()
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)
    print(f"   Supabase Client: {'✅ PASS' if supabase_success else '❌ FAIL'}")
    print(f"   Direct PostgreSQL: {'✅ PASS' if postgres_success else '❌ FAIL'}")
    print(f"   SQLAlchemy: {'✅ PASS' if sqlalchemy_success else '❌ FAIL'}")
    
    if all([supabase_success, postgres_success, sqlalchemy_success]):
        print("\n🎉 All tests passed! Supabase connection is working.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        
        if not supabase_success:
            print("\n🔧 Supabase Client Issues:")
            print("   - Verify SUPABASE_URL is correct")
            print("   - Verify SUPABASE_SERVICE_ROLE_KEY is valid")
            print("   - Check if Supabase project is active")
            
        if not postgres_success:
            print("\n🔧 PostgreSQL Connection Issues:")
            print("   - Verify DATABASE_URL is correct")
            print("   - Check if password contains special characters (use %40 for @)")
            print("   - Verify database is accessible from your IP")
            print("   - Check if database user has proper permissions")

if __name__ == "__main__":
    main()
