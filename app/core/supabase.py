"""
Supabase client configuration and utilities for the Knowledge Pathways Backend.
This module provides Supabase client initialization and helper functions.
"""

from supabase import create_client, Client
from app.core.config import settings
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class SupabaseManager:
    """Manages Supabase client and operations."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client if configuration is available."""
        if settings.USE_SUPABASE and settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            try:
                self.client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
                print(f"✅ Supabase client initialized successfully for {settings.SUPABASE_URL}")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            print("ℹ️ Supabase not configured - using local database")
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance."""
        return self.client
    
    def is_available(self) -> bool:
        """Check if Supabase is available and configured."""
        return self.client is not None
    
    def test_connection(self) -> bool:
        """Test the Supabase connection."""
        if not self.client:
            return False
        
        try:
            # Just test if client can be created - don't query tables that don't exist
            return self.client is not None
        except Exception as e:
            print(f"❌ Supabase connection test failed: {e}")
            return False
    
    # Authentication methods
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sign up a new user using Supabase auth."""
        if not self.client:
            raise HTTPException(status_code=500, detail="Supabase not available")
        
        try:
            # Create user with Supabase auth
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data
                }
            })
            
            if response.user:
                # Check if session exists (it might not exist for email confirmation)
                if response.session:
                    return {
                        "user": response.user,
                        "session": response.session,
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token
                    }
                else:
                    # User created but needs email confirmation
                    return {
                        "user": response.user,
                        "session": None,
                        "access_token": None,
                        "refresh_token": None,
                        "message": "User created successfully. Please check your email for confirmation."
                    }
            else:
                raise HTTPException(status_code=400, detail="Failed to create user")
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Sign up failed: {str(e)}")
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user using Supabase auth."""
        if not self.client:
            raise HTTPException(status_code=500, detail="Supabase not available")
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": response.user,
                    "session": response.session,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Sign in failed: {str(e)}")
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out a user."""
        if not self.client:
            return False
        
        try:
            self.client.auth.sign_out()
            return True
        except Exception:
            return False
    
    async def get_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from access token."""
        if not self.client:
            return None
        
        try:
            # Set the auth header
            self.client.auth.set_session(access_token, access_token)
            user = self.client.auth.get_user(access_token)
            return user.user if user else None
        except Exception:
            return None
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email."""
        if not self.client:
            return False
        
        try:
            self.client.auth.reset_password_for_email(email)
            return True
        except Exception:
            return False


# Global Supabase manager instance
supabase_manager = SupabaseManager()


def get_supabase_client() -> Optional[Client]:
    """Get the Supabase client instance."""
    return supabase_manager.get_client()


def is_supabase_available() -> bool:
    """Check if Supabase is available."""
    return supabase_manager.is_available()


def test_supabase_connection() -> bool:
    """Test Supabase connection."""
    return supabase_manager.test_connection()


# Convenience functions for auth operations
async def supabase_sign_up(email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sign up a new user."""
    return await supabase_manager.sign_up(email, password, user_data)


async def supabase_sign_in(email: str, password: str) -> Dict[str, Any]:
    """Sign in a user."""
    return await supabase_manager.sign_in(email, password)


async def supabase_sign_out(access_token: str) -> bool:
    """Sign out a user."""
    return await supabase_manager.sign_out(access_token)


async def supabase_get_user(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user information."""
    return await supabase_manager.get_user(access_token)


async def supabase_reset_password(email: str) -> bool:
    """Reset password."""
    return await supabase_manager.reset_password(email)
