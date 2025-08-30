from firebase_functions import https_fn
import json
import os
from datetime import datetime
import hashlib

# Load environment variables from .env file
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"🔍 Looking for .env file at: {env_path}")
    
    if os.path.exists(env_path):
        print("📖 Reading .env file...")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"✅ Loaded: {key} = {value[:20]}...")
    else:
        print("❌ .env file not found!")

# Load environment variables
load_env_file()

# Initialize Supabase client
try:
    from supabase import create_client, Client
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    
    # Try to get service role key if available
    SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if SUPABASE_URL and SUPABASE_KEY:
        print(f"🔗 Creating Supabase client...")
        
        # Try service role key first (more permissions)
        if SERVICE_ROLE_KEY:
            print("🔑 Using service role key for enhanced permissions...")
            supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
        else:
            print("🔑 Using anon key...")
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            
        print("✅ Supabase client created successfully")
    else:
        print("❌ Supabase credentials missing")
        supabase = None
except Exception as e:
    print(f"❌ Error creating Supabase client: {e}")
    supabase = None

# Simple password hashing
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed_password

print("✅ Password hashing initialized with SHA-256")

# Main registration function
@https_fn.on_request()
def register(req: https_fn.Request) -> https_fn.Response:
    """Handle user registration"""
    
    # Only allow POST requests
    if req.method != 'POST':
        return https_fn.Response(
            json.dumps({"error": "Method not allowed"}),
            status=405,
            headers={"Content-Type": "application/json"}
        )
    
    try:
        print("🔍 Starting user registration...")
        
        # Parse request data
        data = req.get_json()
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        print(f"🔍 Registration data: email={email}, full_name={full_name}")
        
        # Validate required fields
        if not email or not password:
            return https_fn.Response(
                json.dumps({"error": "Email and password are required"}),
                status=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Hash password
        print("🔍 Hashing password...")
        hashed_password = hash_password(password)
        print(f"🔍 Password hashed: {hashed_password[:20]}...")
        
        # Create user data
        user_data = {
            "email": email,
            "password_hash": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"🔍 User data prepared: {user_data}")
        
        # Insert user into database
        if supabase:
            print("🔍 Supabase client available, attempting to insert user...")
            try:
                # Try to insert the user directly (table should exist)
                print("🔍 Attempting to insert user into users table...")
                try:
                    response = supabase.table('users').insert(user_data).execute()
                    print(f"🔍 Supabase response: {response}")
                except Exception as insert_error:
                    print(f"⚠️ Insert failed: {insert_error}")
                    print("🔍 Error details: The users table might not exist yet.")
                    print("🔍 Please create the table manually in your Supabase dashboard first.")
                    raise insert_error
                
                if response.data:
                    user = response.data[0]
                    print(f"✅ User created successfully: {user['id']}")
                    return https_fn.Response(
                        json.dumps({
                            "message": "User registered successfully",
                            "user": {
                                "id": user['id'],
                                "email": user['email'],
                                "full_name": user['full_name']
                            }
                        }),
                        status=201,
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    print("❌ No data returned from Supabase insert")
                    return https_fn.Response(
                        json.dumps({"error": "Failed to create user - no data returned"}),
                        status=500,
                        headers={"Content-Type": "application/json"}
                    )
            except Exception as db_error:
                print(f"❌ Database error: {db_error}")
                return https_fn.Response(
                    json.dumps({"error": f"Database error: {str(db_error)}"}),
                    status=500,
                    headers={"Content-Type": "application/json"}
                )
        else:
            print("❌ Supabase client not available")
            return https_fn.Response(
                json.dumps({"error": "Database connection not available"}),
                status=500,
                headers={"Content-Type": "application/json"}
            )
            
    except Exception as e:
        print(f"❌ Unexpected error in registration: {e}")
        import traceback
        traceback.print_exc()
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"}
        )

# Login function
@https_fn.on_request()
def login(req: https_fn.Request) -> https_fn.Response:
    """Handle user login"""
    
    # Only allow POST requests
    if req.method != 'POST':
        return https_fn.Response(
            json.dumps({"error": "Method not allowed"}),
            status=405,
            headers={"Content-Type": "application/json"}
        )
    
    try:
        print("🔍 Starting user login...")
        
        # Parse request data
        data = req.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"🔍 Login data: email={email}")
        
        # Validate required fields
        if not email or not password:
            return https_fn.Response(
                json.dumps({"error": "Email and password are required"}),
                status=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Find user by email
        if supabase:
            print("🔍 Supabase client available, attempting to find user...")
            try:
                # Query user by email
                print("🔍 Querying user by email...")
                response = supabase.table('users').select('*').eq('email', email).execute()
                print(f"🔍 Supabase response: {response}")
                
                if response.data and len(response.data) > 0:
                    user = response.data[0]
                    print(f"🔍 User found: {user['id']}")
                    
                    # Verify password
                    print("🔍 Verifying password...")
                    if verify_password(password, user['password_hash']):
                        print("✅ Password verified successfully")
                        
                        # Return user data (without password)
                        return https_fn.Response(
                            json.dumps({
                                "message": "Login successful",
                                "user": {
                                    "id": user['id'],
                                    "email": user['email'],
                                    "full_name": user['full_name'],
                                    "is_active": user['is_active'],
                                    "created_at": user['created_at']
                                }
                            }),
                            status=200,
                            headers={"Content-Type": "application/json"}
                        )
                    else:
                        print("❌ Password verification failed")
                        return https_fn.Response(
                            json.dumps({"error": "Invalid email or password"}),
                            status=401,
                            headers={"Content-Type": "application/json"}
                        )
                else:
                    print("❌ User not found")
                    return https_fn.Response(
                        json.dumps({"error": "Invalid email or password"}),
                        status=401,
                        headers={"Content-Type": "application/json"}
                    )
                    
            except Exception as db_error:
                print(f"❌ Database error: {db_error}")
                return https_fn.Response(
                    json.dumps({"error": f"Database error: {str(db_error)}"}),
                    status=500,
                    headers={"Content-Type": "application/json"}
                )
        else:
            print("❌ Supabase client not available")
            return https_fn.Response(
                json.dumps({"error": "Database connection not available"}),
                status=500,
                headers={"Content-Type": "application/json"}
            )
            
    except Exception as e:
        print(f"❌ Unexpected error in login: {e}")
        import traceback
        traceback.print_exc()
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"}
        )
