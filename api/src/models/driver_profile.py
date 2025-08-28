from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class PersonalInfo:
    """Personal information for driver profile"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    social_security: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

@dataclass
class LicenseInfo:
    """Driver license information"""
    license_number: Optional[str] = None
    license_class: Optional[str] = None
    license_state: Optional[str] = None
    license_expiration: Optional[str] = None
    endorsements: Optional[str] = None
    restrictions: Optional[str] = None

@dataclass
class EmploymentRecord:
    """Single employment record"""
    employer_name: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    reason_for_leaving: Optional[str] = None
    supervisor_name: Optional[str] = None
    supervisor_contact: Optional[str] = None

@dataclass
class EmploymentHistory:
    """Complete employment history"""
    years_experience: Optional[str] = None
    current_employment_status: Optional[str] = None
    previous_positions: List[EmploymentRecord] = None
    
    def __post_init__(self):
        if self.previous_positions is None:
            self.previous_positions = []

@dataclass
class SafetyRecord:
    """Safety and compliance records"""
    criminal_record_status: Optional[str] = None
    accident_history: Optional[str] = None
    traffic_violations: Optional[str] = None
    drug_test_results: Optional[str] = None
    license_suspensions: Optional[str] = None
    dui_convictions: Optional[str] = None

@dataclass
class Education:
    """Education and training information"""
    trucking_school: Optional[str] = None
    graduation_status: Optional[str] = None
    training_hours: Optional[str] = None
    gpa: Optional[str] = None
    certifications: Optional[str] = None

@dataclass
class ComplianceInfo:
    """Compliance and authorization information"""
    fcra_authorization: Optional[str] = None
    background_check_consent: Optional[str] = None
    psp_disclosure: Optional[str] = None
    clearinghouse_consent: Optional[str] = None
    drug_testing_consent: Optional[str] = None

@dataclass
class RiskAssessment:
    """Risk assessment results"""
    level: str = "Unknown"  # Low, Medium, High, Unknown
    score: int = 0
    color: str = "gray"  # green, yellow, red, gray
    factors: List[str] = None
    recommendation: str = ""
    
    def __post_init__(self):
        if self.factors is None:
            self.factors = []

@dataclass
class ApplicationMetadata:
    """Metadata about the application processing"""
    filename: Optional[str] = None
    confidence_score: float = 0.0
    total_fields_extracted: int = 0
    processing_time: Optional[str] = None
    api_version: str = "2.0"
    processed_at: Optional[str] = None

@dataclass
class DriverProfile:
    """Complete driver profile structure"""
    # Unique identifiers
    driver_id: str = None
    profile_id: str = None
    
    # Core profile sections
    personal: PersonalInfo = None
    license: LicenseInfo = None
    employment: EmploymentHistory = None
    safety: SafetyRecord = None
    education: Education = None
    compliance: ComplianceInfo = None
    
    # Assessment and metadata
    risk_assessment: RiskAssessment = None
    metadata: ApplicationMetadata = None
    
    # Status and timestamps
    status: str = "pending"  # pending, reviewed, approved, rejected
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        # Generate IDs if not provided
        if self.driver_id is None:
            self.driver_id = str(uuid.uuid4())
        if self.profile_id is None:
            self.profile_id = f"DRV-{self.driver_id[:8].upper()}"
        
        # Initialize nested objects if None
        if self.personal is None:
            self.personal = PersonalInfo()
        if self.license is None:
            self.license = LicenseInfo()
        if self.employment is None:
            self.employment = EmploymentHistory()
        if self.safety is None:
            self.safety = SafetyRecord()
        if self.education is None:
            self.education = Education()
        if self.compliance is None:
            self.compliance = ComplianceInfo()
        if self.risk_assessment is None:
            self.risk_assessment = RiskAssessment()
        if self.metadata is None:
            self.metadata = ApplicationMetadata()
        
        # Set timestamps
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert driver profile to dictionary"""
        return asdict(self)
    
    def to_json_safe(self) -> Dict[str, Any]:
        """Convert to JSON-safe dictionary with clean structure"""
        profile_dict = self.to_dict()
        
        # Clean up None values and empty lists
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items() if v is not None and v != [] and v != ""}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d if item is not None]
            else:
                return d
        
        return clean_dict(profile_dict)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary view of the driver profile"""
        return {
            "driver_id": self.driver_id,
            "profile_id": self.profile_id,
            "name": self.personal.full_name,
            "email": self.personal.email,
            "phone": self.personal.phone,
            "license_class": self.license.license_class,
            "experience": self.employment.years_experience,
            "risk_level": self.risk_assessment.level,
            "risk_score": self.risk_assessment.score,
            "confidence": self.metadata.confidence_score,
            "status": self.status,
            "created_at": self.created_at
        }

def create_driver_profile_from_parsed_data(parsed_data: Dict[str, Any], metadata: Dict[str, Any], risk_assessment: Dict[str, Any]) -> DriverProfile:
    """Create a DriverProfile from parsed PDF data"""
    
    # Extract employment records from parsed data
    employment_records = []
    if parsed_data.get('previous_employers'):
        # Try to parse structured employment data
        employers = str(parsed_data.get('previous_employers', '')).split(',')
        positions = str(parsed_data.get('positions_held', '')).split(',')
        dates = str(parsed_data.get('employment_dates', '')).split(',')
        reasons = str(parsed_data.get('reasons_for_leaving', '')).split(',')
        supervisors = str(parsed_data.get('supervisor_contacts', '')).split(',')
        
        max_records = max(len(employers), len(positions), len(dates))
        for i in range(min(max_records, 5)):  # Limit to 5 records
            record = EmploymentRecord(
                employer_name=employers[i].strip() if i < len(employers) else None,
                position=positions[i].strip() if i < len(positions) else None,
                start_date=dates[i].strip() if i < len(dates) else None,
                reason_for_leaving=reasons[i].strip() if i < len(reasons) else None,
                supervisor_contact=supervisors[i].strip() if i < len(supervisors) else None
            )
            if record.employer_name:  # Only add if we have at least employer name
                employment_records.append(record)
    
    # Create the driver profile
    profile = DriverProfile(
        personal=PersonalInfo(
            full_name=parsed_data.get('full_name'),
            email=parsed_data.get('email'),
            phone=parsed_data.get('phone'),
            address=parsed_data.get('address'),
            date_of_birth=parsed_data.get('date_of_birth'),
            social_security=parsed_data.get('social_security'),
            emergency_contact_name=parsed_data.get('emergency_contact_name'),
            emergency_contact_phone=parsed_data.get('emergency_contact_phone')
        ),
        license=LicenseInfo(
            license_number=parsed_data.get('license_number'),
            license_class=parsed_data.get('license_class'),
            license_state=parsed_data.get('license_state'),
            license_expiration=parsed_data.get('license_expiration'),
            endorsements=parsed_data.get('endorsements'),
            restrictions=parsed_data.get('restrictions')
        ),
        employment=EmploymentHistory(
            years_experience=parsed_data.get('years_experience'),
            current_employment_status=parsed_data.get('employment_status'),
            previous_positions=employment_records
        ),
        safety=SafetyRecord(
            criminal_record_status=parsed_data.get('criminal_record_status'),
            accident_history=parsed_data.get('accident_history'),
            traffic_violations=parsed_data.get('traffic_violations'),
            drug_test_results=parsed_data.get('drug_test_results'),
            license_suspensions=parsed_data.get('license_suspensions')
        ),
        education=Education(
            trucking_school=parsed_data.get('trucking_school'),
            graduation_status=parsed_data.get('graduation_status'),
            training_hours=parsed_data.get('training_hours'),
            gpa=parsed_data.get('gpa')
        ),
        compliance=ComplianceInfo(
            fcra_authorization=parsed_data.get('fcra_authorization'),
            background_check_consent=parsed_data.get('background_check_consent'),
            psp_disclosure=parsed_data.get('psp_disclosure'),
            clearinghouse_consent=parsed_data.get('clearinghouse_consent')
        ),
        risk_assessment=RiskAssessment(
            level=risk_assessment.get('level', 'Unknown'),
            score=risk_assessment.get('score', 0),
            color=risk_assessment.get('color', 'gray'),
            factors=risk_assessment.get('factors', []),
            recommendation=risk_assessment.get('recommendation', '')
        ),
        metadata=ApplicationMetadata(
            filename=metadata.get('filename'),
            confidence_score=metadata.get('confidence_score', 0.0),
            total_fields_extracted=metadata.get('total_fields_extracted', 0),
            processing_time=metadata.get('processing_time'),
            api_version=metadata.get('api_version', '2.0'),
            processed_at=datetime.utcnow().isoformat()
        )
    )
    
    return profile

