from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure CORS properly
    if os.getenv('FLASK_ENV') == 'production':
        # Allow specific origins in production
        allowed_origins = [
            "https://personal-finance-tracker-theta-gold.vercel.app",  # Your frontend URL
            "https://finance-tracker-backend-s741.onrender.com"  # Your backend URL
        ]
    else:
        # Allow all in development
        allowed_origins = "*"
    
    CORS(app, origins=allowed_origins, supports_credentials=True)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app