from flask import Blueprint, request, jsonify
import os
import tempfile
import json
import traceback
import logging
from werkzeug.utils import secure_filename
from src.enhanced_pdf_parser import EnhancedTenstreetPDFParser
from src.services.profile_service import profile_service
from src.models.driver_profile import DriverProfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

profiles_bp = Blueprint('profiles', __name__)

# Initialize the PDF parser
pdf_parser = EnhancedTenstreetPDFParser()

def assess_driver_risk(profile_data):
    """Assess risk level based on driver profile data"""
    risk_factors = []
    risk_score = 0
    
    # Check criminal record
    criminal_status = str(profile_data.get('criminal_record_status', '')).lower()
    if 'felony' in criminal_status or 'conviction' in criminal_status:
        risk_factors.append("Criminal record found")
        risk_score += 3
    elif 'misdemeanor' in criminal_status:
        risk_factors.append("Minor criminal record")
        risk_score += 1
    
    # Check accident history
    accident_history = str(profile_data.get('accident_history', '')).lower()
    if 'accident' in accident_history or 'collision' in accident_history:
        risk_factors.append("Accident history reported")
        risk_score += 2
    
    # Check license issues
    license_issues = str(profile_data.get('license_suspensions', '')).lower()
    if 'suspended' in license_issues or 'revoked' in license_issues:
        risk_factors.append("License suspension/revocation")
        risk_score += 3
    
    # Check drug test failures
    drug_test = str(profile_data.get('drug_test_results', '')).lower()
    if 'failed' in drug_test or 'positive' in drug_test:
        risk_factors.append("Drug test failure")
        risk_score += 3
    
    # Check traffic violations
    violations = str(profile_data.get('traffic_violations', '')).lower()
    if 'violation' in violations or 'ticket' in violations:
        risk_factors.append("Traffic violations")
        risk_score += 1
    
    # Determine risk level
    if risk_score >= 5:
        risk_level = "High"
        risk_color = "red"
    elif risk_score >= 2:
        risk_level = "Medium" 
        risk_color = "yellow"
    else:
        risk_level = "Low"
        risk_color = "green"
    
    recommendations = {
        "Low": "Candidate appears to have a clean record. Proceed with standard hiring process.",
        "Medium": "Some concerns identified. Consider additional screening or interview questions.",
        "High": "Significant risk factors present. Thorough review and additional verification recommended."
    }
    
    return {
        "level": risk_level,
        "score": risk_score,
        "color": risk_color,
        "factors": risk_factors,
        "recommendation": recommendations.get(risk_level, "Review candidate information carefully.")
    }

@profiles_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Driveline Driver Profile API v2",
        "version": "2.0",
        "database": "Connected to Driveline Recruit Supabase",
        "features": [
            "Driver profile creation from PDF",
            "Structured JSON driver profiles",
            "Risk assessment and scoring",
            "Supabase integration",
            "Profile management API",
            "Search and filtering",
            "Direct Driveline Recruit integration"
        ]
    })

@profiles_bp.route('/create-profile', methods=['POST'])
def create_driver_profile():
    """Create a driver profile from uploaded PDF"""
    temp_path = None
    try:
        logger.info("Starting driver profile creation from PDF")
        
        # Check if file was uploaded
        if 'pdf_file' not in request.files:
            logger.warning("No PDF file provided in request")
            return jsonify({
                "success": False,
                "error": "No PDF file provided",
                "message": "Please upload a PDF file"
            }), 400
        
        file = request.files['pdf_file']
        
        # Check if file is selected
        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({
                "success": False,
                "error": "No file selected",
                "message": "Please select a PDF file to upload"
            }), 400
        
        # Check file type
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                "success": False,
                "error": "Invalid file type",
                "message": "Only PDF files are supported"
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        logger.info(f"Processing file: {filename}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Parse the PDF
            logger.info("Starting PDF parsing")
            parse_result = pdf_parser.parse_pdf(temp_path)
            logger.info(f"PDF parsing completed with result: {parse_result.get('success', False)}")
            
            if not parse_result['success']:
                return jsonify({
                    "success": False,
                    "error": "PDF parsing failed",
                    "message": parse_result.get('error', 'Unknown error occurred during parsing'),
                    "details": parse_result.get('details', {})
                }), 500
            
            # Extract parsed data
            parsed_data = parse_result['data']
            
            # Create metadata
            metadata = {
                "filename": filename,
                "api_version": "2.0",
                "parser_type": "enhanced_driver_profile",
                "total_fields_extracted": len([v for v in parsed_data.values() if v]),
                "confidence_score": parse_result.get('confidence', 0),
                "processing_time": parse_result.get('processing_time', 'N/A')
            }
            
            # Assess risk
            risk_assessment = assess_driver_risk(parsed_data)
            
            # Create driver profile
            logger.info("Creating driver profile from parsed data")
            driver_profile = profile_service.create_profile_from_pdf_data(
                parsed_data, metadata, risk_assessment
            )
            
            if not driver_profile:
                return jsonify({
                    "success": False,
                    "error": "Profile creation failed",
                    "message": "Failed to create driver profile from parsed data"
                }), 500
            
            # Return the created profile
            response_data = {
                "success": True,
                "message": "Driver profile created successfully",
                "driver_profile": {
                    "driver_id": driver_profile.driver_id,
                    "profile_id": driver_profile.profile_id,
                    "personal": driver_profile.personal.__dict__,
                    "license": driver_profile.license.__dict__,
                    "employment": {
                        "years_experience": driver_profile.employment.years_experience,
                        "current_status": driver_profile.employment.current_employment_status,
                        "previous_positions": [pos.__dict__ for pos in driver_profile.employment.previous_positions]
                    },
                    "safety": driver_profile.safety.__dict__,
                    "education": driver_profile.education.__dict__,
                    "compliance": driver_profile.compliance.__dict__,
                    "risk_assessment": driver_profile.risk_assessment.__dict__,
                    "status": driver_profile.status,
                    "created_at": driver_profile.created_at
                },
                "metadata": {
                    "confidence_score": metadata["confidence_score"],
                    "total_fields_extracted": metadata["total_fields_extracted"],
                    "processing_time": metadata["processing_time"],
                    "filename": filename
                },
                "database": {
                    "stored": True,
                    "table": "driver_profiles",
                    "database": "driveline_recruit_app"
                }
            }
            
            logger.info(f"Successfully created driver profile {driver_profile.profile_id} for {driver_profile.personal.full_name}")
            return jsonify(response_data)
            
        except Exception as parse_error:
            logger.error(f"PDF processing error: {str(parse_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return jsonify({
                "success": False,
                "error": "PDF processing error",
                "message": f"Error processing PDF: {str(parse_error)}",
                "details": {"parse_error": str(parse_error)}
            }), 500
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": "Server error",
            "message": f"Internal server error: {str(e)}",
            "details": {"server_error": str(e)}
        }), 500
    
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.info("Temporary file cleaned up")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temp file: {str(cleanup_error)}")

@profiles_bp.route('/profiles', methods=['GET'])
def get_all_profiles():
    """Get all driver profiles with pagination"""
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        profiles = profile_service.get_all_profiles(limit=limit, offset=offset)
        
        return jsonify({
            "success": True,
            "count": len(profiles),
            "profiles": profiles,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(profiles) == limit
            },
            "database": "driveline_recruit_app"
        })
    except Exception as e:
        logger.error(f"Error fetching profiles: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Database error",
            "message": f"Error fetching profiles: {str(e)}"
        }), 500

@profiles_bp.route('/profiles/<driver_id>', methods=['GET'])
def get_profile(driver_id):
    """Get a specific driver profile by ID"""
    try:
        profile = profile_service.get_profile_by_id(driver_id)
        if profile:
            return jsonify({
                "success": True,
                "profile": profile.to_json_safe(),
                "database": "driveline_recruit_app"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Not found",
                "message": f"Driver profile {driver_id} not found"
            }), 404
    except Exception as e:
        logger.error(f"Error fetching profile {driver_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Database error",
            "message": f"Error fetching profile: {str(e)}"
        }), 500

@profiles_bp.route('/profiles/search', methods=['GET'])
def search_profiles():
    """Search driver profiles"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({
                "success": False,
                "error": "Missing search term",
                "message": "Please provide a search term using the 'q' parameter"
            }), 400
        
        profiles = profile_service.search_profiles(search_term)
        
        return jsonify({
            "success": True,
            "count": len(profiles),
            "search_term": search_term,
            "profiles": profiles,
            "database": "driveline_recruit_app"
        })
    except Exception as e:
        logger.error(f"Error searching profiles: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Search error",
            "message": f"Error searching profiles: {str(e)}"
        }), 500

@profiles_bp.route('/profiles/<driver_id>/status', methods=['PUT'])
def update_profile_status(driver_id):
    """Update driver profile status"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                "success": False,
                "error": "Missing status",
                "message": "Please provide a status in the request body"
            }), 400
        
        status = data['status']
        valid_statuses = ['pending', 'reviewed', 'approved', 'rejected']
        if status not in valid_statuses:
            return jsonify({
                "success": False,
                "error": "Invalid status",
                "message": f"Status must be one of: {', '.join(valid_statuses)}"
            }), 400
        
        success = profile_service.update_profile_status(driver_id, status)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Profile status updated to {status}",
                "driver_id": driver_id,
                "new_status": status
            })
        else:
            return jsonify({
                "success": False,
                "error": "Update failed",
                "message": "Failed to update profile status"
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating profile status: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Update error",
            "message": f"Error updating profile status: {str(e)}"
        }), 500

@profiles_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get driver profile statistics"""
    try:
        stats = profile_service.get_profile_statistics()
        return jsonify({
            "success": True,
            "statistics": stats
        })
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Statistics error",
            "message": f"Error fetching statistics: {str(e)}"
        }), 500

@profiles_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        "message": "Driveline Driver Profile API v2 is working!",
        "status": "success",
        "timestamp": "2024-08-28",
        "database": "Connected to Driveline Recruit Supabase",
        "endpoints": {
            "create_profile": "POST /api/v2/create-profile",
            "get_profiles": "GET /api/v2/profiles",
            "get_profile": "GET /api/v2/profiles/{driver_id}",
            "search_profiles": "GET /api/v2/profiles/search?q=term",
            "update_status": "PUT /api/v2/profiles/{driver_id}/status",
            "statistics": "GET /api/v2/statistics"
        },
        "features": [
            "Driver profile creation from PDF",
            "Structured JSON profiles",
            "Risk assessment",
            "Profile management",
            "Search and filtering",
            "Supabase integration"
        ]
    })

