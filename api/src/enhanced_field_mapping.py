"""
Enhanced Field Mapping for Comprehensive Tenstreet PDF Parsing
Covers all sections from pages 1-30 including employment history, criminal history, etc.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class FieldType(Enum):
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    BOOLEAN = "boolean"
    NUMBER = "number"
    ADDRESS = "address"
    SSN = "ssn"
    ARRAY = "array"
    OBJECT = "object"

@dataclass
class FieldMapping:
    field_name: str
    field_type: FieldType
    patterns: List[str]
    required: bool = False
    section: str = "general"

# COMPREHENSIVE FIELD MAPPINGS FOR ALL SECTIONS

# Personal Information Section
PERSONAL_INFO_FIELDS = [
    FieldMapping("referral_code", FieldType.TEXT, [
        r"Referral Code[:\s]*([^\n\r]+)",
        r"Referral[:\s]*([^\n\r]+)"
    ], section="personal"),
    
    FieldMapping("full_name", FieldType.TEXT, [
        r"Name\s+([A-Za-z\s\.]+?)(?:\n|$)",
        r"Full Name[:\s]*([^\n\r]+)"
    ], required=True, section="personal"),
    
    FieldMapping("current_address", FieldType.ADDRESS, [
        r"Current Address\s+([^\n\r]+)",
        r"Address[:\s]*([^\n\r]+)"
    ], section="personal"),
    
    FieldMapping("city_state_zip", FieldType.TEXT, [
        r"City, State/Province Zip/Postal\s+([^\n\r]+)",
        r"City[:\s]*([^\n\r]+)"
    ], section="personal"),
    
    FieldMapping("country", FieldType.TEXT, [
        r"Country\s+([^\n\r]+)"
    ], section="personal"),
    
    FieldMapping("residence_duration", FieldType.TEXT, [
        r"Residence\s+([^\n\r]+)",
        r"3 years or longer[^\n]*([Yes|No])"
    ], section="personal"),
    
    FieldMapping("ssn", FieldType.SSN, [
        r"SSN/SIN\s+(\d{3}-\d{2}-\d{4})",
        r"SSN[:\s]*(\d{3}-\d{2}-\d{4})"
    ], section="personal"),
    
    FieldMapping("date_of_birth", FieldType.DATE, [
        r"Date of Birth\s+(\d{1,2}-\d{1,2}-\d{4})",
        r"DOB[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ], section="personal"),
    
    FieldMapping("primary_phone", FieldType.PHONE, [
        r"Primary Phone\s+(\d{3}-\d{3}-\d{4})",
        r"Phone[:\s]*(\d{3}[-\s]\d{3}[-\s]\d{4})"
    ], section="personal"),
    
    FieldMapping("cell_phone", FieldType.PHONE, [
        r"Cell Phone\s+(\d{3}-\d{3}-\d{4})",
        r"Cell[:\s]*(\d{3}[-\s]\d{3}[-\s]\d{4})"
    ], section="personal"),
    
    FieldMapping("email", FieldType.EMAIL, [
        r"Email\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        r"E-mail[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    ], section="personal"),
    
    FieldMapping("emergency_contact_name", FieldType.TEXT, [
        r"Emergency contact name[:\s]*([^\n\r]+)",
        r"Emergency Contact[:\s]*([^\n\r]+)"
    ], section="personal"),
    
    FieldMapping("emergency_contact_phone", FieldType.PHONE, [
        r"Emergency contact phone number[:\s]*(\d{3}[\s-]\d{3}[\s-]\d{4})",
        r"Emergency.*phone[:\s]*(\d{3}[\s-]\d{3}[\s-]\d{4})"
    ], section="personal"),
]

# Company Questions Section
COMPANY_QUESTIONS_FIELDS = [
    FieldMapping("position_applying_for", FieldType.TEXT, [
        r"What position are you applying for\?\s*([^\n\r]+)",
        r"Position[:\s]*([^\n\r]+)"
    ], section="company"),
    
    FieldMapping("location_applying_for", FieldType.TEXT, [
        r"What location are you applying for\?\s*([^\n\r]+)",
        r"Location[:\s]*([^\n\r]+)"
    ], section="company"),
    
    FieldMapping("legally_eligible_employment", FieldType.BOOLEAN, [
        r"Are you legally eligible for employment in the United States\?\s*(Yes|No)",
        r"legally eligible.*?\s*(Yes|No)"
    ], section="company"),
    
    FieldMapping("currently_employed", FieldType.BOOLEAN, [
        r"Are you currently employed\?\s*(Yes|No)",
        r"currently employed.*?\s*(Yes|No)"
    ], section="company"),
    
    FieldMapping("last_employment_end_date", FieldType.DATE, [
        r"What date did your last employment end\?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})",
        r"last employment end.*?(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ], section="company"),
    
    FieldMapping("read_write_speak_english", FieldType.BOOLEAN, [
        r"Do you read, write, and speak English\?\s*(Yes|No)",
        r"speak English.*?\s*(Yes|No)"
    ], section="company"),
    
    FieldMapping("worked_for_company_before", FieldType.BOOLEAN, [
        r"Have you ever worked for this company before\?\s*(Yes|No)",
        r"worked for this company.*?\s*(Yes|No)"
    ], section="company"),
    
    FieldMapping("has_twic_card", FieldType.BOOLEAN, [
        r"Do you have a current TWIC card\?\s*(Yes|No)",
        r"TWIC card.*?\s*(Yes|No)"
    ], section="company"),
    
    FieldMapping("twic_expiration_date", FieldType.DATE, [
        r"TWIC.*?Expiration date[:\s]*(\d{1,2}-\d{1,2}-\d{4})",
        r"TWIC.*?expires[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ], section="company"),
    
    FieldMapping("known_by_other_name", FieldType.BOOLEAN, [
        r"Have you ever been known by any other name\?\s*(Yes|No)",
        r"other name.*?\s*(Yes|No)"
    ], section="company"),
    
    FieldMapping("other_name", FieldType.TEXT, [
        r"Enter name[:\s]*([^\n\r]+)",
        r"other name[:\s]*([^\n\r]+)"
    ], section="company"),
    
    FieldMapping("how_heard_about_us", FieldType.TEXT, [
        r"How did you hear about us\?\s*([^\n\r]+)",
        r"hear about us.*?\s*([^\n\r]+)"
    ], section="company"),
    
    FieldMapping("referral_driver_name", FieldType.TEXT, [
        r"Driver Referral.*?enter the driver's name\s*([^\n\r]+)",
        r"driver's name[:\s]*([^\n\r]+)"
    ], section="company"),
]

# Driving Experience Section
DRIVING_EXPERIENCE_FIELDS = [
    FieldMapping("straight_truck_experience", FieldType.TEXT, [
        r"Straight Truck\s+([^\n\r]+)",
        r"Straight.*?(\d+[-+\s]*years?|None)"
    ], section="experience"),
    
    FieldMapping("tractor_semi_trailer_experience", FieldType.TEXT, [
        r"Tractor and Semi-Trailer\s+([^\n\r]+)",
        r"Semi-Trailer.*?(\d+[-+\s]*years?|None)"
    ], section="experience"),
    
    FieldMapping("tractor_two_trailers_experience", FieldType.TEXT, [
        r"Tractor - Two Trailers\s+([^\n\r]+)",
        r"Two Trailers.*?(\d+[-+\s]*years?|None)"
    ], section="experience"),
    
    FieldMapping("other_experience", FieldType.TEXT, [
        r"Other\s+([^\n\r]+)",
        r"Other.*?experience[:\s]*([^\n\r]+)"
    ], section="experience"),
]

# License Information Section
LICENSE_FIELDS = [
    FieldMapping("license_number", FieldType.TEXT, [
        r"License Number\s+([A-Za-z0-9]+)",
        r"License #[:\s]*([A-Za-z0-9]+)"
    ], section="license"),
    
    FieldMapping("licensing_authority", FieldType.TEXT, [
        r"Licensing Authority\s+([A-Z]{2})",
        r"State[:\s]*([A-Z]{2})"
    ], section="license"),
    
    FieldMapping("license_country", FieldType.TEXT, [
        r"Country\s+(US|United States|CA|Canada)",
        r"License.*?Country[:\s]*([^\n\r]+)"
    ], section="license"),
    
    FieldMapping("license_class", FieldType.TEXT, [
        r"License Class\s+([^\n\r]+)",
        r"Class[:\s]*([^\n\r]+)"
    ], section="license"),
    
    FieldMapping("license_expiration_date", FieldType.DATE, [
        r"License Expiration Date\s+(\d{1,2}-\d{1,2}-\d{4})",
        r"Expires[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ], section="license"),
    
    FieldMapping("dot_medical_card_expiration", FieldType.DATE, [
        r"DOT Medical Card Expiration Date\s+(\d{1,2}-\d{1,2}-\d{4})",
        r"Medical.*?expir.*?(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ], section="license"),
    
    FieldMapping("current_license", FieldType.BOOLEAN, [
        r"Current License\s+(Yes|No)",
        r"current.*?license.*?(Yes|No)"
    ], section="license"),
    
    FieldMapping("has_cdl", FieldType.BOOLEAN, [
        r"Commercial Driver License\s+(Yes|No)",
        r"CDL.*?(Yes|No)"
    ], section="license"),
]

# Endorsements Section
ENDORSEMENT_FIELDS = [
    FieldMapping("tanker_endorsement", FieldType.BOOLEAN, [
        r"Tanker Endorsement\s+(Yes|No)",
        r"Tanker.*?(Yes|No)"
    ], section="endorsements"),
    
    FieldMapping("hazmat_endorsement", FieldType.BOOLEAN, [
        r"HAZMAT Endorsement\s+(Yes|No)",
        r"HAZMAT.*?(Yes|No)"
    ], section="endorsements"),
    
    FieldMapping("x_endorsement", FieldType.BOOLEAN, [
        r"X Endorsement\s+(Yes|No)",
        r"X.*?Endorsement.*?(Yes|No)"
    ], section="endorsements"),
    
    FieldMapping("doubles_triples_endorsement", FieldType.BOOLEAN, [
        r"Doubles Triples Endorsement\s+(Yes|No)",
        r"Doubles.*?Triples.*?(Yes|No)"
    ], section="endorsements"),
    
    FieldMapping("other_endorsement", FieldType.BOOLEAN, [
        r"Other Endorsement\s+(Yes|No)",
        r"Other.*?Endorsement.*?(Yes|No)"
    ], section="endorsements"),
]

# Trucking School Section
TRUCKING_SCHOOL_FIELDS = [
    FieldMapping("trucking_school_name", FieldType.TEXT, [
        r"School\s+([^\n\r]+)",
        r"trucking.*?school[:\s]*([^\n\r]+)"
    ], section="education"),
    
    FieldMapping("school_address", FieldType.ADDRESS, [
        r"School.*?Address[:\s]*([^\n\r]+)",
        r"school.*?location[:\s]*([^\n\r]+)"
    ], section="education"),
    
    FieldMapping("school_city_state", FieldType.TEXT, [
        r"School.*?City, State/Province[:\s]*([^\n\r]+)",
        r"school.*?city[:\s]*([^\n\r]+)"
    ], section="education"),
    
    FieldMapping("school_phone", FieldType.PHONE, [
        r"School.*?Phone[:\s]*(\d{3}[-\s]\d{3}[-\s]\d{4})",
        r"school.*?phone[:\s]*(\d{3}[-\s]\d{3}[-\s]\d{4})"
    ], section="education"),
    
    FieldMapping("school_graduated", FieldType.BOOLEAN, [
        r"Did you graduate\?\s*(Yes|No)",
        r"graduate.*?(Yes|No)"
    ], section="education"),
    
    FieldMapping("school_gpa", FieldType.NUMBER, [
        r"GPA\s+(\d+\.?\d*)",
        r"grade.*?(\d+\.?\d*)"
    ], section="education"),
    
    FieldMapping("school_hours", FieldType.NUMBER, [
        r"Hours of Instruction\s+(\d+)",
        r"instruction.*?hours[:\s]*(\d+)"
    ], section="education"),
]

# FMCSR Compliance Section
FMCSR_FIELDS = [
    FieldMapping("currently_disqualified", FieldType.BOOLEAN, [
        r"are you currently disqualified.*?\s*(Yes|No)",
        r"disqualified.*?(Yes|No)"
    ], section="compliance"),
    
    FieldMapping("license_suspended_revoked", FieldType.BOOLEAN, [
        r"license.*?suspended or revoked.*?\s*(Yes|No)",
        r"suspended.*?revoked.*?(Yes|No)"
    ], section="compliance"),
    
    FieldMapping("suspension_details", FieldType.TEXT, [
        r"suspension.*?detail.*?([^\n\r]+)",
        r"revocation.*?detail.*?([^\n\r]+)"
    ], section="compliance"),
    
    FieldMapping("denied_license", FieldType.BOOLEAN, [
        r"denied a license.*?\s*(Yes|No)",
        r"denied.*?license.*?(Yes|No)"
    ], section="compliance"),
    
    FieldMapping("denial_details", FieldType.TEXT, [
        r"denial.*?detail.*?([^\n\r]+)",
        r"denied.*?detail.*?([^\n\r]+)"
    ], section="compliance"),
    
    FieldMapping("failed_drug_test", FieldType.BOOLEAN, [
        r"tested positive.*?refused to test.*?\s*(Yes|No)",
        r"drug.*?test.*?(Yes|No)"
    ], section="compliance"),
    
    FieldMapping("drug_test_details", FieldType.TEXT, [
        r"drug.*?test.*?detail.*?([^\n\r]+)",
        r"positive.*?detail.*?([^\n\r]+)"
    ], section="compliance"),
    
    FieldMapping("last_positive_date", FieldType.DATE, [
        r"Date of last positive.*?(\d{1,2}-\d{1,2}-\d{4})",
        r"last positive.*?(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ], section="compliance"),
    
    FieldMapping("convicted_serious_offenses", FieldType.BOOLEAN, [
        r"convicted of any of the following offenses.*?\s*(Yes|No)",
        r"serious.*?offenses.*?(Yes|No)"
    ], section="compliance"),
]

# Vehicle Accident Record Section
ACCIDENT_FIELDS = [
    FieldMapping("accidents_last_5_years", FieldType.BOOLEAN, [
        r"involved in any accidents.*?last 5 years.*?\s*(Yes|No)",
        r"accidents.*?5 years.*?(Yes|No)"
    ], section="accidents"),
    
    FieldMapping("accident_type", FieldType.TEXT, [
        r"Type of Accident.*?([^\n\r]+)",
        r"accident.*?type[:\s]*([^\n\r]+)"
    ], section="accidents"),
    
    FieldMapping("accident_date", FieldType.DATE, [
        r"Date of Accident.*?(\d{1,2}-\d{4})",
        r"accident.*?date[:\s]*(\d{1,2}[-/]\d{4})"
    ], section="accidents"),
    
    FieldMapping("hazmat_accident", FieldType.BOOLEAN, [
        r"Hazmat Accident.*?\s*(Yes|No)",
        r"hazmat.*?accident.*?(Yes|No)"
    ], section="accidents"),
    
    FieldMapping("vehicle_towed", FieldType.BOOLEAN, [
        r"any vehicle towed away\?\s*(Yes|No)",
        r"towed.*?(Yes|No)"
    ], section="accidents"),
    
    FieldMapping("accident_city", FieldType.TEXT, [
        r"City\s+([^\n\r]+)",
        r"accident.*?city[:\s]*([^\n\r]+)"
    ], section="accidents"),
    
    FieldMapping("accident_state", FieldType.TEXT, [
        r"State/Province\s+([A-Z]{2})",
        r"accident.*?state[:\s]*([A-Z]{2})"
    ], section="accidents"),
    
    FieldMapping("commercial_vehicle_accident", FieldType.BOOLEAN, [
        r"Were you in a commercial vehicle\?\s*(Yes|No)",
        r"commercial vehicle.*?(Yes|No)"
    ], section="accidents"),
    
    FieldMapping("dot_recordable_accident", FieldType.BOOLEAN, [
        r"Department of Transportation recordable accident\?\s*(Yes|No)",
        r"DOT.*?recordable.*?(Yes|No)"
    ], section="accidents"),
    
    FieldMapping("at_fault", FieldType.BOOLEAN, [
        r"Were you at fault\?\s*(Yes|No)",
        r"at fault.*?(Yes|No)"
    ], section="accidents"),
    
    FieldMapping("ticketed", FieldType.BOOLEAN, [
        r"Were you ticketed\?\s*(Yes|No)",
        r"ticketed.*?(Yes|No)"
    ], section="accidents"),
    
    FieldMapping("accident_description", FieldType.TEXT, [
        r"Description\s+([^\n\r]+(?:\n[^\n\r]+)*)",
        r"accident.*?description[:\s]*([^\n\r]+)"
    ], section="accidents"),
]

# Traffic Violations Section
TRAFFIC_FIELDS = [
    FieldMapping("moving_violations_3_years", FieldType.BOOLEAN, [
        r"moving violations.*?past 3 years.*?\s*(Yes|No)",
        r"traffic.*?violations.*?(Yes|No)"
    ], section="traffic"),
    
    FieldMapping("violation_details", FieldType.TEXT, [
        r"violations.*?detail.*?([^\n\r]+)",
        r"traffic.*?detail.*?([^\n\r]+)"
    ], section="traffic"),
]

# Criminal Record Section
CRIMINAL_FIELDS = [
    FieldMapping("convicted_of_crime", FieldType.BOOLEAN, [
        r"Have you ever been convicted of a crime\?\s*(Yes|No)",
        r"convicted.*?crime.*?(Yes|No)"
    ], section="criminal"),
    
    FieldMapping("crime_details", FieldType.TEXT, [
        r"convicted.*?Comment\s+([^\n\r]+)",
        r"crime.*?comment[:\s]*([^\n\r]+)"
    ], section="criminal"),
    
    FieldMapping("deferred_prosecutions", FieldType.BOOLEAN, [
        r"Do you have any deferred prosecutions\?\s*(Yes|No)",
        r"deferred.*?prosecutions.*?(Yes|No)"
    ], section="criminal"),
    
    FieldMapping("charges_pending", FieldType.BOOLEAN, [
        r"Do you have criminal charges pending\?\s*(Yes|No)",
        r"charges.*?pending.*?(Yes|No)"
    ], section="criminal"),
    
    FieldMapping("felony_conviction", FieldType.BOOLEAN, [
        r"pled.*?guilty.*?convicted.*?felony\?\s*(Yes|No)",
        r"felony.*?(Yes|No)"
    ], section="criminal"),
    
    FieldMapping("felony_details", FieldType.TEXT, [
        r"felony.*?Comment\s+([^\n\r]+)",
        r"felony.*?comment[:\s]*([^\n\r]+)"
    ], section="criminal"),
    
    FieldMapping("minister_permit", FieldType.BOOLEAN, [
        r"minister's permit.*?Canada\?\s*(Yes|No)",
        r"minister.*?permit.*?(Yes|No)"
    ], section="criminal"),
    
    FieldMapping("misdemeanor_5_years", FieldType.BOOLEAN, [
        r"within the last five years.*?misdemeanor\?\s*(Yes|No)",
        r"misdemeanor.*?5 years.*?(Yes|No)"
    ], section="criminal"),
]

# Signature Section
SIGNATURE_FIELDS = [
    FieldMapping("signature_full_name", FieldType.TEXT, [
        r"Full Name\s+([^\n\r]+)",
        r"signature.*?name[:\s]*([^\n\r]+)"
    ], section="signature"),
    
    FieldMapping("ip_address", FieldType.TEXT, [
        r"IP Address\s+([0-9.]+)",
        r"IP[:\s]*([0-9.]+)"
    ], section="signature"),
    
    FieldMapping("signature_date_time", FieldType.TEXT, [
        r"Signature Date/Time\s+([^\n\r]+)",
        r"signature.*?date[:\s]*([^\n\r]+)"
    ], section="signature"),
]

# FCRA Acknowledgments Section
FCRA_FIELDS = [
    FieldMapping("fcra_summary_acknowledgment", FieldType.BOOLEAN, [
        r"FCRA Summary of Rights Acknowledgment.*?\s*(Yes|No)",
        r"FCRA.*?acknowledgment.*?(Yes|No)"
    ], section="fcra"),
    
    FieldMapping("psp_disclosure_authorization", FieldType.BOOLEAN, [
        r"PSP Disclosure and Authorization.*?\s*(Yes|No)",
        r"PSP.*?authorization.*?(Yes|No)"
    ], section="fcra"),
    
    FieldMapping("fcra_disclosure", FieldType.BOOLEAN, [
        r"FCRA Disclosure.*?\s*(Yes|No)",
        r"FCRA.*?disclosure.*?(Yes|No)"
    ], section="fcra"),
    
    FieldMapping("fcra_authorization", FieldType.BOOLEAN, [
        r"FCRA Authorization.*?\s*(Yes|No)",
        r"FCRA.*?authorization.*?(Yes|No)"
    ], section="fcra"),
    
    FieldMapping("employment_verification_acknowledgment", FieldType.BOOLEAN, [
        r"Employment Verification Acknowledgment.*?\s*(Yes|No)",
        r"employment.*?verification.*?(Yes|No)"
    ], section="fcra"),
    
    FieldMapping("clearinghouse_release", FieldType.BOOLEAN, [
        r"Clearinghouse Release.*?\s*(Yes|No)",
        r"clearinghouse.*?(Yes|No)"
    ], section="fcra"),
    
    FieldMapping("investigative_consumer_report", FieldType.BOOLEAN, [
        r"INVESTIGATIVE CONSUMER REPORT.*?\s*(Yes|No)",
        r"investigative.*?report.*?(Yes|No)"
    ], section="fcra"),
]

# Combine all field mappings
ALL_ENHANCED_FIELD_MAPPINGS = (
    PERSONAL_INFO_FIELDS +
    COMPANY_QUESTIONS_FIELDS +
    DRIVING_EXPERIENCE_FIELDS +
    LICENSE_FIELDS +
    ENDORSEMENT_FIELDS +
    TRUCKING_SCHOOL_FIELDS +
    FMCSR_FIELDS +
    ACCIDENT_FIELDS +
    TRAFFIC_FIELDS +
    CRIMINAL_FIELDS +
    SIGNATURE_FIELDS +
    FCRA_FIELDS
)

# Enhanced Supabase Schema for comprehensive data
ENHANCED_SUPABASE_SCHEMA = {
    "table_name": "driver_applications_comprehensive",
    "columns": {
        # Primary key and timestamps
        "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
        "created_at": "timestamp DEFAULT now()",
        "updated_at": "timestamp DEFAULT now()",
        
        # Personal Information
        "referral_code": "text",
        "full_name": "text NOT NULL",
        "current_address": "text",
        "city_state_zip": "text",
        "country": "text",
        "residence_duration": "text",
        "ssn": "text",
        "date_of_birth": "date",
        "primary_phone": "text",
        "cell_phone": "text",
        "email": "text",
        "emergency_contact_name": "text",
        "emergency_contact_phone": "text",
        
        # Company Questions
        "position_applying_for": "text",
        "location_applying_for": "text",
        "legally_eligible_employment": "boolean",
        "currently_employed": "boolean",
        "last_employment_end_date": "date",
        "read_write_speak_english": "boolean",
        "worked_for_company_before": "boolean",
        "has_twic_card": "boolean",
        "twic_expiration_date": "date",
        "known_by_other_name": "boolean",
        "other_name": "text",
        "how_heard_about_us": "text",
        "referral_driver_name": "text",
        
        # Driving Experience
        "straight_truck_experience": "text",
        "tractor_semi_trailer_experience": "text",
        "tractor_two_trailers_experience": "text",
        "other_experience": "text",
        
        # License Information
        "license_number": "text",
        "licensing_authority": "text",
        "license_country": "text",
        "license_class": "text",
        "license_expiration_date": "date",
        "dot_medical_card_expiration": "date",
        "current_license": "boolean",
        "has_cdl": "boolean",
        
        # Endorsements
        "tanker_endorsement": "boolean",
        "hazmat_endorsement": "boolean",
        "x_endorsement": "boolean",
        "doubles_triples_endorsement": "boolean",
        "other_endorsement": "boolean",
        
        # Trucking School
        "trucking_school_name": "text",
        "school_address": "text",
        "school_city_state": "text",
        "school_phone": "text",
        "school_graduated": "boolean",
        "school_gpa": "decimal",
        "school_hours": "integer",
        
        # FMCSR Compliance
        "currently_disqualified": "boolean",
        "license_suspended_revoked": "boolean",
        "suspension_details": "text",
        "denied_license": "boolean",
        "denial_details": "text",
        "failed_drug_test": "boolean",
        "drug_test_details": "text",
        "last_positive_date": "date",
        "convicted_serious_offenses": "boolean",
        
        # Vehicle Accidents
        "accidents_last_5_years": "boolean",
        "accident_type": "text",
        "accident_date": "date",
        "hazmat_accident": "boolean",
        "vehicle_towed": "boolean",
        "accident_city": "text",
        "accident_state": "text",
        "commercial_vehicle_accident": "boolean",
        "dot_recordable_accident": "boolean",
        "at_fault": "boolean",
        "ticketed": "boolean",
        "accident_description": "text",
        
        # Traffic Violations
        "moving_violations_3_years": "boolean",
        "violation_details": "text",
        
        # Criminal Record
        "convicted_of_crime": "boolean",
        "crime_details": "text",
        "deferred_prosecutions": "boolean",
        "charges_pending": "boolean",
        "felony_conviction": "boolean",
        "felony_details": "text",
        "minister_permit": "boolean",
        "misdemeanor_5_years": "boolean",
        
        # Signature
        "signature_full_name": "text",
        "ip_address": "text",
        "signature_date_time": "text",
        
        # FCRA Acknowledgments
        "fcra_summary_acknowledgment": "boolean",
        "psp_disclosure_authorization": "boolean",
        "fcra_disclosure": "boolean",
        "fcra_authorization": "boolean",
        "employment_verification_acknowledgment": "boolean",
        "clearinghouse_release": "boolean",
        "investigative_consumer_report": "boolean",
        
        # Employment History (JSON)
        "employment_history": "jsonb",
        
        # Metadata
        "pdf_filename": "text",
        "parsing_confidence": "decimal",
        "raw_text": "text"
    }
}

def get_field_by_name(field_name: str) -> Optional[FieldMapping]:
    """Get a field mapping by name."""
    for field in ALL_ENHANCED_FIELD_MAPPINGS:
        if field.field_name == field_name:
            return field
    return None

def get_fields_by_section(section: str) -> List[FieldMapping]:
    """Get all field mappings for a specific section."""
    return [field for field in ALL_ENHANCED_FIELD_MAPPINGS if field.section == section]

def get_all_sections() -> List[str]:
    """Get all unique section names."""
    return list(set(field.section for field in ALL_ENHANCED_FIELD_MAPPINGS))

