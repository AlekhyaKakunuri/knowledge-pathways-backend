from firebase_functions import https_fn
from firebase_admin import initialize_app, get_app

# Initialize Firebase Admin SDK only if not already initialized
try:
    get_app()
except ValueError:
    initialize_app()

# Import the functions
from api import register, login

# Export the functions
exports = {
    "register": register,
    "login": login
}
