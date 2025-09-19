from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "https://personal-finance-tracker-theta-gold.vercel.app",
                "https://finance-tracker-backend-s741.onrender.com"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app