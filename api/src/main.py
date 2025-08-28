from flask import Flask
from flask_cors import CORS
from src.routes.driver_profiles import profiles_bp
from src.supabase_client import supabase_client, test_connection
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins="*")
    
    # Register blueprints
    app.register_blueprint(profiles_bp, url_prefix='/api/v2')
    
    @app.route('/')
    def home():
        # Test Supabase connection
        connection_status, connection_message = test_connection()
        
        return {
            "message": "Driveline Driver Profile API v2",
            "status": "healthy",
            "version": "2.0",
            "database": {
                "connected": connection_status,
                "message": connection_message,
                "project": "driveline_recruit_app"
            },
            "endpoints": {
                "health": "/api/v2/health",
                "create_profile": "/api/v2/create-profile",
                "get_profiles": "/api/v2/profiles",
                "get_profile": "/api/v2/profiles/{driver_id}",
                "search_profiles": "/api/v2/profiles/search?q=term",
                "update_status": "/api/v2/profiles/{driver_id}/status",
                "statistics": "/api/v2/statistics",
                "test": "/api/v2/test"
            },
            "features": [
                "Driver profile creation from PDF",
                "Structured JSON driver profiles",
                "91+ field extraction",
                "Risk assessment and scoring",
                "Supabase integration",
                "Profile management API",
                "Search and filtering",
                "Direct Driveline Recruit integration"
            ],
            "integration": {
                "description": "Upload PDF → Get structured driver profile JSON",
                "example_usage": "POST /api/v2/create-profile with PDF file",
                "response_format": "Structured driver profile with personal, license, employment, safety data"
            }
        }
    
    @app.route('/health')
    def health():
        connection_status, connection_message = test_connection()
        
        return {
            "status": "healthy",
            "service": "Driveline Driver Profile API v2",
            "version": "2.0",
            "database": {
                "connected": connection_status,
                "message": connection_message,
                "supabase_project": "lqllzavksufpiqefwthy"
            },
            "ready_for_integration": True
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Driveline Driver Profile API v2")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

