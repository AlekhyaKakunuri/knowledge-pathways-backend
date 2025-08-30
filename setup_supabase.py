#!/usr/bin/env python3
"""
Supabase Setup Script for Knowledge Pathways Backend
This script helps configure and test the Supabase connection.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from env.example if it doesn't exist."""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ env.example not found!")
        return False
    
    if env_file.exists():
        print("ℹ️ .env file already exists")
        return False
    
    # Copy env.example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from env.example")
    return True

def get_supabase_config():
    """Get Supabase configuration from user input."""
    print("\n🔧 Supabase Configuration Setup")
    print("=" * 50)
    
    config = {}
    
    # Project URL
    while True:
        url = input("Enter your Supabase project URL (e.g., https://abc123.supabase.co): ").strip()
        if url.startswith("https://") and "supabase.co" in url:
            config['SUPABASE_URL'] = url
            break
        print("❌ Invalid URL format. Please enter a valid Supabase URL.")
    
    # Anon Key
    anon_key = input("Enter your Supabase anon/public key: ").strip()
    if anon_key:
        config['SUPABASE_ANON_KEY'] = anon_key
    
    # Service Role Key
    service_key = input("Enter your Supabase service role key: ").strip()
    if service_key:
        config['SUPABASE_SERVICE_ROLE_KEY'] = service_key
    
    # Database Password
    db_password = input("Enter your Supabase database password (optional): ").strip()
    if db_password:
        config['SUPABASE_DB_PASSWORD'] = db_password
    
    # Enable Supabase
    enable = input("Enable Supabase? (y/n): ").strip().lower()
    config['USE_SUPABASE'] = 'true' if enable in ['y', 'yes'] else 'false'
    
    return config

def update_env_file(config):
    """Update .env file with Supabase configuration."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found! Run create_env_file() first.")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update or add configuration values
    updated_lines = []
    config_keys = set(config.keys())
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            updated_lines.append(line)
            continue
        
        if '=' in line:
            key = line.split('=')[0]
            if key in config_keys:
                updated_lines.append(f"{key}={config[key]}")
                config_keys.remove(key)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Add any remaining config keys
    for key in config_keys:
        updated_lines.append(f"{key}={config[key]}")
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Updated .env file with Supabase configuration")
    return True

def test_supabase_connection():
    """Test the Supabase connection."""
    print("\n🧪 Testing Supabase Connection")
    print("=" * 50)
    
    try:
        # Import and test Supabase connection
        from app.core.supabase import test_supabase_connection, is_supabase_available
        
        if is_supabase_available():
            if test_supabase_connection():
                print("✅ Supabase connection successful!")
                return True
            else:
                print("❌ Supabase connection test failed!")
                return False
        else:
            print("ℹ️ Supabase not configured or not available")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install requirements: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Knowledge Pathways Backend - Supabase Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Please run this script from the backend root directory")
        sys.exit(1)
    
    # Create .env file if needed
    create_env_file()
    
    # Get Supabase configuration
    config = get_supabase_config()
    
    # Update .env file
    if update_env_file(config):
        print("\n📝 Configuration updated successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test connection: python setup_supabase.py --test")
        print("3. Start the backend: python start.py")
    else:
        print("❌ Failed to update configuration")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_supabase_connection()
    else:
        main()
