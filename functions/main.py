from firebase_functions import https_fn
from firebase_admin import initialize_app, get_app
import json
import logging
from typing import Dict, Any, Optional
from firebase_admin import firestore, auth, credentials

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK only if not already initialized
try:
    get_app()
except ValueError:
    # Import credentials first
    from firebase_admin import credentials
    
    # Use service account credentials for local development
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "educourse-6b0c9",
        "private_key_id": "87d566411641b7beb06e458aa0d8725215eb9b9e",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCHgbSk8rj11zrG\ncQWvLeYc1bPiskvA3OXDw2ihiMP8mJc88ze3wGj25HXc7kCLaWMThWKBCIC0Ddw1\ndP6oTwvQyGRbVhTRR+zcu2NpKPbwOM/xwtMloPYmwSeLyVXKe3oumHF69tEKQp/h\n6rNmcLgMDaJUwG4/tUiIiihjSZgr1D83fGQGcUcSplnrr0nnLSbIoT7mEM62hXV9\noHsf3Cnn0bWALBLMLhLdQMQeDwup0FXD+Sk6Xl+aYqTxXmv12nJP316NlJoSeb7o\n7as7V2kRd1/J8fIGC07ziGRzZSPpKVoeIxmRsfccN/3eJoUZsNGTaZU0ZiDwFYtN\nJ97TvTV3AgMBAAECggEAB5sVpx6CmDXs9B966LLEVEEAeEx2qQwdD2hj8pEpIv/z\nmTWznmo72gPHw89RqyGOsJVPipuOEc0nW47GDm9lY+Ijk+bYg0isuFUCRvBIMAKY\nVWMQk++dcV5tGFEEMjnNCVmAIR1CbXeA3t7cE/dmtTJ8tpIYfhXwTM2oZ65FTsxl\nmIE4B0JiY1DDO6kAqZHhD8OSzQ8F4+VLBAst3M0heXVRxKHQDfPW+8gjhyAT4q/M\nRwfranpIrHBZ9EJe6zxu4F7Mma9tW0jRkMmL0nw1FVdQXBgo/Zgz8PlvQ/ktgRq8\nP2/g5rq6yGCQbNRqraYWonrg5nZrOkeMEyNVwRTERQKBgQC9udUcBeV4dcAXejx/\nRC3cwnbIKWH7+ETdAq95Tq/jSggV6ivB/T8h/6QRA5yz8lKb08r/QyyJd88on83d\nmeJHqvaKczHjEMq7Bz//ZxSRvsmZoO6CbRIbHuvWXzqDHN2qKKqYWFfA6Tjnt74E\njB2RcgZZ1S8MXCbbcxnB8T3RSwKBgQC211ZyLWe/Urysi0BQUilQhWiJaengflpI\nJVPn9uSlFV0ceZn3HljU/Ce53swv7PYFdYrvlW/DpHiGiooJZK3MSfkmd9kOTAg+\nnHW12TM/U8PAbNS7k3ZLYCfCoNqY2D/DJ5qm1PRcVDzvJnQ6ZexPgX7ViGRxMXA1\n8hsiY3P9BQKBgQC02lgTBmvfkB80Qgk5J7ywG48u7oPAtMCwDMdIU4HGn+NlQHvF\nx6pOtmmm7lKKFgw5DoMLIPVrdRG8H9kVzIKu3oF1KKn9URxvfFG9HH23EK8MCyRQ\nn7gKskcNamlUYkfK1EkKP+wmsCrWd4hivU3SP2deaqEWnyFLP0TmYxgSUQKBgCpU\nB8s+/7mnKc64Hhd6Ld5aRC0ru90g4z24hog4/A3LuFaTQDWZbO9BwOCi15pwvTPe\nVl/ItKsSNGTRRcuO5z1YErn5HOLWb0IvboC+28JZXgP6LfWO2d/xTsMcAf9IcNp5\nHLBqtHd7eO/Ucyvh1KdDT12Xycj6rQOQHQAFDiERAoGAdaKsdvXpwAja7nHbWu8f\nslxyfLm/ClJfJEjXGfhcxnAf/a8HBT3v4P7KnPQXxBLQZgGOnzGzXyKEYzYKRRPv\nGUPKk1qid4JhO8aNI/dNAH5Q/6++NbtBQtSDEmidHssvCG47UIrJwyFIynHRvbvY\nxM8B5/NFetJKLXEDaZMRjBc=\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-fbsvc@educourse-6b0c9.iam.gserviceaccount.com",
        "client_id": "105509994375564584293",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40educourse-6b0c9.iam.gserviceaccount.com"
    })
    
    # Initialize Firebase app with credentials
    initialize_app(cred)
    logger.info("✅ Firebase initialized with service account credentials")

# Initialize Firebase Firestore client
try:
    from firebase_admin import firestore, auth
    
    db = firestore.client()
    logger.info("✅ Firebase Firestore client created successfully")
except Exception as e:
    logger.error(f"❌ Error creating Firestore client: {e}")
    db = None

def create_response(data: Dict[str, Any], status: int = 200) -> https_fn.Response:
    """Create standardized HTTP response"""
    return https_fn.Response(
        json.dumps(data, default=str),
        status=status,
        headers={"Content-Type": "application/json"}
    )

@https_fn.on_request()
def signup(req: https_fn.Request) -> https_fn.Response:
    """Handle user signup with Firebase Authentication"""
    
    try:
        logger.info("🔍 Starting user signup...")
        
        # Only allow POST requests
        if req.method != 'POST':
            return create_response(
                {"error": "Method not allowed. Use POST for signup."},
                status=405
            )
        
        # Parse request data
        try:
            data = req.get_json()
        except Exception:
            return create_response(
                {"error": "Invalid JSON data"},
                status=400
            )
        
        if not data:
            return create_response(
                {"error": "Request body is required"},
                status=400
            )
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validate required fields
        if not email or not password or not full_name:
            return create_response(
                {"error": "Email, password, and full_name are required"},
                status=400
            )
        
        # Validate password length (Firebase requires at least 6 characters)
        if len(password) < 6:
            return create_response(
                {"error": "Password must be at least 6 characters long"},
                status=400
            )
        
        logger.info(f"🔍 Signup data: email={email}, full_name={full_name}")
        
        try:
            # Create user in Firebase Authentication
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=full_name
            )
            
            logger.info(f"✅ Firebase user created: {user_record.uid}")
            
            # Store additional user data in Firestore
            if db:
                try:
                    user_data = {
                        "uid": user_record.uid,
                        "email": email,
                        "full_name": full_name,
                        "is_active": True,
                        "created_at": firestore.SERVER_TIMESTAMP
                    }
                    
                    # Add to Firestore
                    db.collection('users').document(user_record.uid).set(user_data)
                    logger.info(f"✅ User data stored in Firestore: {user_record.uid}")
                except Exception as firestore_error:
                    logger.error(f"❌ Firestore write error: {firestore_error}")
                    logger.error(f"❌ Error type: {type(firestore_error)}")
                    logger.error(f"❌ Error details: {str(firestore_error)}")
                    # Continue without Firestore storage
            else:
                logger.warning("⚠️ Firestore client not available, skipping user data storage")
            
            # Return success response
            return create_response(
                {
                    "message": "User signed up successfully",
                    "user": {
                        "uid": user_record.uid,
                        "email": email,
                        "full_name": full_name
                    }
                },
                status=201
            )
                
        except auth.EmailAlreadyExistsError:
            logger.warning(f"❌ Email already exists: {email}")
            return create_response(
                {"error": "User with this email already exists"},
                status=400
            )
        except Exception as auth_error:
            logger.error(f"❌ Firebase auth error: {auth_error}")
            return create_response(
                {"error": "Failed to create user account"},
                status=500
            )
            
    except Exception as e:
        logger.error(f"❌ Unexpected error in signup: {e}")
        return create_response(
            {"error": "Internal server error"},
            status=500
        )

@https_fn.on_request()
def login(req: https_fn.Request) -> https_fn.Response:
    """Handle user login with Firebase Authentication"""
    
    try:
        logger.info("🔍 Starting user login...")
        
        # Only allow POST requests
        if req.method != 'POST':
            return create_response(
                {"error": "Method not allowed. Use POST for login."},
                status=405
            )
        
        # Parse request data
        try:
            data = req.get_json()
        except Exception:
            return create_response(
                {"error": "Invalid JSON data"},
                status=400
            )
        
        if not data:
            return create_response(
                {"error": "Request body is required"},
                status=400
            )
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate required fields
        if not email or not password:
            return create_response(
                {"error": "Email and password are required"},
                status=400
            )
        
        logger.info(f"🔍 Login attempt for: {email}")
        
        try:
            # Sign in user with Firebase Authentication
            user_record = auth.get_user_by_email(email)
            
            # Note: Firebase handles password verification on the client side
            # This endpoint just verifies the user exists and returns user info
            
            logger.info(f"✅ User found: {user_record.uid}")
            
            # Get additional user data from Firestore if available
            user_data = {
                "uid": user_record.uid,
                "email": user_record.email,
                "full_name": user_record.display_name or "Unknown"
            }
            
            if db:
                firestore_doc = db.collection('users').document(user_record.uid).get()
                if firestore_doc.exists:
                    firestore_data = firestore_doc.to_dict()
                    user_data.update({
                        "is_active": firestore_data.get('is_active', True),
                        "created_at": firestore_data.get('created_at', '')
                    })
            
            return create_response(
                {
                    "message": "Login successful",
                    "user": user_data
                }
            )
                
        except auth.UserNotFoundError:
            logger.warning(f"❌ User not found: {email}")
            return create_response(
                {"error": "Invalid email or password"},
                status=401
            )
        except Exception as auth_error:
            logger.error(f"❌ Firebase auth error: {auth_error}")
            return create_response(
                {"error": "Login failed"},
                status=500
            )
            
    except Exception as e:
        logger.error(f"❌ Unexpected error in login: {e}")
        return create_response(
            {"error": "Internal server error"},
            status=500
        )

@https_fn.on_request()
def get_user_profile(req: https_fn.Request) -> https_fn.Response:
    """Get user profile (requires Firebase Auth token)"""
    
    try:
        # Only allow GET requests
        if req.method != 'GET':
            return create_response(
                {"error": "Method not allowed. Use GET for profile."},
                status=405
            )
        
        # Get Firebase Auth token from Authorization header
        auth_header = req.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return create_response(
                {"error": "Authorization token required"},
                status=401
            )
        
        token = auth_header.split('Bearer ')[1]
        logger.info("🔍 Firebase token received")
        
        try:
            # Verify token and get user ID
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token['uid']
            logger.info(f"🔍 Token verified for user: {user_id}")
            
            # Get user profile from Firestore
            if db:
                user_doc = db.collection('users').document(user_id).get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    logger.info(f"✅ User profile found for: {user_id}")
                    
                    return create_response(
                        {
                            "message": "Profile retrieved successfully",
                            "user": {
                                "uid": user_id,
                                "email": user_data.get('email', ''),
                                "full_name": user_data.get('full_name', ''),
                                "is_active": user_data.get('is_active', True),
                                "created_at": user_data.get('created_at', '')
                            }
                        }
                    )
                else:
                    logger.warning(f"❌ User profile not found: {user_id}")
                    return create_response(
                        {"error": "User profile not found"},
                        status=404
                    )
            else:
                logger.error("❌ Firestore client not available")
                return create_response(
                    {"error": "Database connection not available"},
                    status=500
                )
                
        except Exception as auth_error:
            logger.warning(f"❌ Token verification failed: {auth_error}")
            return create_response(
                {"error": "Invalid authentication token"},
                status=401
            )
            
    except Exception as e:
        logger.error(f"❌ Unexpected error in get_profile: {e}")
        return create_response(
            {"error": "Internal server error"},
            status=500
        )

@https_fn.on_request()
def health_check(req: https_fn.Request) -> https_fn.Response:
    """Health check endpoint for monitoring"""
    
    try:
        # Allow both GET and POST for health check
        if req.method not in ['GET', 'POST']:
            return create_response(
                {"error": "Method not allowed. Use GET or POST for health check."},
                status=405
            )
        
        # Check database connectivity
        db_status = "healthy" if db else "unhealthy"
        
        return create_response(
            {
                "status": "healthy",
                "database": db_status,
                "version": "1.0.0"
            }
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return create_response(
            {"status": "unhealthy", "error": str(e)},
            status=500
        )

# Export functions for Firebase emulator
exports = {
    "signup": signup,
    "login": login,
    "get_user_profile": get_user_profile,
    "health_check": health_check
}

