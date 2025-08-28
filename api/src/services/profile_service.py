import logging
from typing import Dict, List, Optional, Any
from src.models.driver_profile import DriverProfile, create_driver_profile_from_parsed_data
from src.supabase_client import supabase_client

logger = logging.getLogger(__name__)

class DriverProfileService:
    """Service for managing driver profiles"""
    
    def __init__(self):
        self.supabase = supabase_client
    
    def create_profile_from_pdf_data(self, parsed_data: Dict[str, Any], metadata: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Optional[DriverProfile]:
        """Create a driver profile from parsed PDF data"""
        try:
            # Create the driver profile object
            profile = create_driver_profile_from_parsed_data(parsed_data, metadata, risk_assessment)
            
            # Store in Supabase
            stored_profile = self.store_profile(profile)
            
            if stored_profile:
                logger.info(f"Successfully created driver profile {profile.profile_id} for {profile.personal.full_name}")
                return profile
            else:
                logger.error(f"Failed to store driver profile for {profile.personal.full_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating driver profile: {str(e)}")
            return None
    
    def store_profile(self, profile: DriverProfile) -> Optional[Dict[str, Any]]:
        """Store driver profile in Supabase"""
        try:
            if not self.supabase:
                raise Exception("Supabase client not initialized")
            
            # Prepare data for Supabase storage
            profile_data = {
                # Identifiers
                'driver_id': profile.driver_id,
                'profile_id': profile.profile_id,
                
                # Personal Information
                'full_name': profile.personal.full_name,
                'email': profile.personal.email,
                'phone': profile.personal.phone,
                'address': profile.personal.address,
                'date_of_birth': profile.personal.date_of_birth,
                'social_security': profile.personal.social_security,
                'emergency_contact_name': profile.personal.emergency_contact_name,
                'emergency_contact_phone': profile.personal.emergency_contact_phone,
                
                # License Information
                'license_number': profile.license.license_number,
                'license_class': profile.license.license_class,
                'license_state': profile.license.license_state,
                'license_expiration': profile.license.license_expiration,
                'endorsements': profile.license.endorsements,
                'restrictions': profile.license.restrictions,
                
                # Employment
                'years_experience': profile.employment.years_experience,
                'current_employment_status': profile.employment.current_employment_status,
                'employment_history': [record.__dict__ for record in profile.employment.previous_positions],
                
                # Safety Records
                'criminal_record_status': profile.safety.criminal_record_status,
                'accident_history': profile.safety.accident_history,
                'traffic_violations': profile.safety.traffic_violations,
                'drug_test_results': profile.safety.drug_test_results,
                'license_suspensions': profile.safety.license_suspensions,
                
                # Education
                'trucking_school': profile.education.trucking_school,
                'graduation_status': profile.education.graduation_status,
                'training_hours': profile.education.training_hours,
                'gpa': profile.education.gpa,
                
                # Compliance
                'fcra_authorization': profile.compliance.fcra_authorization,
                'background_check_consent': profile.compliance.background_check_consent,
                'psp_disclosure': profile.compliance.psp_disclosure,
                'clearinghouse_consent': profile.compliance.clearinghouse_consent,
                
                # Risk Assessment
                'risk_level': profile.risk_assessment.level,
                'risk_score': profile.risk_assessment.score,
                'risk_factors': profile.risk_assessment.factors,
                'risk_recommendation': profile.risk_assessment.recommendation,
                
                # Metadata
                'filename': profile.metadata.filename,
                'confidence_score': profile.metadata.confidence_score,
                'total_fields_extracted': profile.metadata.total_fields_extracted,
                'processing_time': profile.metadata.processing_time,
                'api_version': profile.metadata.api_version,
                'processed_at': profile.metadata.processed_at,
                
                # Complete profile as JSON
                'profile_data': profile.to_json_safe(),
                
                # Status
                'status': profile.status,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at
            }
            
            # Insert into Supabase
            result = self.supabase.table('driver_profiles').insert(profile_data).execute()
            
            if result.data:
                logger.info(f"Successfully stored driver profile {profile.profile_id}")
                return result.data[0]
            else:
                logger.error("Failed to store driver profile - no data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error storing driver profile: {str(e)}")
            return None
    
    def get_profile_by_id(self, driver_id: str) -> Optional[DriverProfile]:
        """Get driver profile by ID"""
        try:
            if not self.supabase:
                raise Exception("Supabase client not initialized")
            
            result = self.supabase.table('driver_profiles').select('*').eq('driver_id', driver_id).execute()
            
            if result.data:
                profile_data = result.data[0]
                return self._create_profile_from_db_data(profile_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error fetching driver profile {driver_id}: {str(e)}")
            return None
    
    def get_all_profiles(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all driver profiles with pagination"""
        try:
            if not self.supabase:
                raise Exception("Supabase client not initialized")
            
            result = self.supabase.table('driver_profiles').select('*').order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching driver profiles: {str(e)}")
            return []
    
    def search_profiles(self, search_term: str) -> List[Dict[str, Any]]:
        """Search driver profiles by name, email, or phone"""
        try:
            if not self.supabase:
                raise Exception("Supabase client not initialized")
            
            # Search across multiple fields
            result = self.supabase.table('driver_profiles').select('*').or_(
                f"full_name.ilike.%{search_term}%,"
                f"email.ilike.%{search_term}%,"
                f"phone.ilike.%{search_term}%,"
                f"profile_id.ilike.%{search_term}%"
            ).order('created_at', desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error searching driver profiles: {str(e)}")
            return []
    
    def update_profile_status(self, driver_id: str, status: str) -> bool:
        """Update driver profile status"""
        try:
            if not self.supabase:
                raise Exception("Supabase client not initialized")
            
            result = self.supabase.table('driver_profiles').update({
                'status': status,
                'updated_at': 'now()'
            }).eq('driver_id', driver_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating driver profile status: {str(e)}")
            return False
    
    def get_profile_statistics(self) -> Dict[str, Any]:
        """Get statistics about driver profiles"""
        try:
            if not self.supabase:
                raise Exception("Supabase client not initialized")
            
            # Get total count
            total_result = self.supabase.table('driver_profiles').select('id', count='exact').execute()
            total_count = total_result.count if total_result.count else 0
            
            # Get risk level distribution
            risk_result = self.supabase.table('driver_profiles').select('risk_level').execute()
            risk_data = risk_result.data if risk_result.data else []
            
            risk_distribution = {
                'low': len([r for r in risk_data if r.get('risk_level') == 'Low']),
                'medium': len([r for r in risk_data if r.get('risk_level') == 'Medium']),
                'high': len([r for r in risk_data if r.get('risk_level') == 'High']),
                'unknown': len([r for r in risk_data if r.get('risk_level') == 'Unknown'])
            }
            
            # Get recent profiles (last 24 hours)
            recent_result = self.supabase.table('driver_profiles').select('id', count='exact').gte('created_at', 'now() - interval \'24 hours\'').execute()
            recent_count = recent_result.count if recent_result.count else 0
            
            return {
                'total_profiles': total_count,
                'risk_distribution': risk_distribution,
                'recent_profiles_24h': recent_count,
                'database': 'driveline_recruit_app'
            }
            
        except Exception as e:
            logger.error(f"Error getting profile statistics: {str(e)}")
            return {
                'total_profiles': 0,
                'risk_distribution': {'low': 0, 'medium': 0, 'high': 0, 'unknown': 0},
                'recent_profiles_24h': 0,
                'database': 'driveline_recruit_app'
            }
    
    def _create_profile_from_db_data(self, db_data: Dict[str, Any]) -> DriverProfile:
        """Create DriverProfile object from database data"""
        # This would reconstruct the DriverProfile from stored data
        # For now, return the stored profile_data JSON
        profile_data = db_data.get('profile_data', {})
        
        # Create a new DriverProfile with the stored data
        # This is a simplified version - you might want to fully reconstruct the object
        profile = DriverProfile()
        profile.driver_id = db_data.get('driver_id')
        profile.profile_id = db_data.get('profile_id')
        profile.status = db_data.get('status')
        profile.created_at = db_data.get('created_at')
        profile.updated_at = db_data.get('updated_at')
        
        return profile

# Global service instance
profile_service = DriverProfileService()

