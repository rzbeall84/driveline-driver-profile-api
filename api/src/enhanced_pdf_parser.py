"""
Enhanced PDF Parser for Comprehensive Tenstreet Driver Application Data Extraction
Extracts data from all sections including employment history, criminal history, etc.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import PyPDF2
import pdfplumber
from enhanced_field_mapping import (
    ALL_ENHANCED_FIELD_MAPPINGS, 
    FieldType, 
    FieldMapping,
    get_fields_by_section,
    get_all_sections
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedTenstreetPDFParser:
    """Enhanced parser for comprehensive Tenstreet driver application data extraction."""
    
    def __init__(self):
        self.field_mappings = ALL_ENHANCED_FIELD_MAPPINGS
        self.sections = get_all_sections()
        
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse a Tenstreet PDF and extract comprehensive data.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing all extracted data
        """
        try:
            # Extract text from PDF
            raw_text = self._extract_text_from_pdf(pdf_path)
            
            # Initialize result dictionary
            result = {
                'pdf_filename': pdf_path.split('/')[-1],
                'raw_text': raw_text,
                'parsing_timestamp': datetime.now().isoformat(),
                'extraction_metadata': {
                    'total_sections_processed': len(self.sections),
                    'fields_attempted': len(self.field_mappings),
                    'fields_extracted': 0,
                    'sections_found': []
                }
            }
            
            # Extract data from each section
            for section in self.sections:
                section_data = self._extract_section_data(raw_text, section)
                result.update(section_data)
                
                if section_data:
                    result['extraction_metadata']['sections_found'].append(section)
            
            # Extract employment history (special handling)
            employment_history = self._extract_employment_history(raw_text)
            result['employment_history'] = employment_history
            
            # Extract accident history (special handling)
            accident_history = self._extract_accident_history(raw_text)
            result['accident_history'] = accident_history
            
            # Calculate parsing confidence
            confidence = self._calculate_parsing_confidence(result)
            result['parsing_confidence'] = confidence
            
            # Count extracted fields
            result['extraction_metadata']['fields_extracted'] = sum(
                1 for key, value in result.items() 
                if value is not None and key not in ['raw_text', 'extraction_metadata', 'parsing_timestamp']
            )
            
            logger.info(f"Successfully parsed PDF with {confidence}% confidence")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"PDF parsing failed: {str(e)}")
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods for better coverage."""
        text = ""
        
        try:
            # Method 1: pdfplumber (better for forms and tables)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
        
        # Method 2: PyPDF2 (fallback)
        if not text.strip():
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed: {e}")
        
        if not text.strip():
            raise Exception("Could not extract text from PDF")
        
        return text
    
    def _extract_section_data(self, text: str, section: str) -> Dict[str, Any]:
        """Extract data for a specific section."""
        section_fields = get_fields_by_section(section)
        section_data = {}
        
        for field in section_fields:
            value = self._extract_field_value(text, field)
            if value is not None:
                section_data[field.field_name] = value
        
        return section_data
    
    def _extract_field_value(self, text: str, field: FieldMapping) -> Any:
        """Extract value for a specific field using its patterns."""
        for pattern in field.patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    raw_value = match.group(1).strip()
                    return self._convert_field_value(raw_value, field.field_type)
            except Exception as e:
                logger.debug(f"Pattern failed for {field.field_name}: {e}")
                continue
        
        return None
    
    def _convert_field_value(self, raw_value: str, field_type: FieldType) -> Any:
        """Convert raw string value to appropriate type."""
        if not raw_value or raw_value.lower() in ['', 'none', 'n/a', 'not found']:
            return None
        
        try:
            if field_type == FieldType.BOOLEAN:
                return raw_value.lower() in ['yes', 'true', '1', 'y']
            
            elif field_type == FieldType.NUMBER:
                if '.' in raw_value:
                    return float(raw_value)
                return int(raw_value)
            
            elif field_type == FieldType.DATE:
                # Handle various date formats
                date_patterns = [
                    r'(\d{1,2})-(\d{1,2})-(\d{4})',
                    r'(\d{1,2})/(\d{1,2})/(\d{4})',
                    r'(\d{4})-(\d{1,2})-(\d{1,2})'
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, raw_value)
                    if match:
                        if len(match.group(3)) == 4:  # Year is 4 digits
                            return f"{match.group(3)}-{match.group(1).zfill(2)}-{match.group(2).zfill(2)}"
                        else:  # Year is 2 digits, assume 20xx
                            year = f"20{match.group(3)}"
                            return f"{year}-{match.group(1).zfill(2)}-{match.group(2).zfill(2)}"
                
                return raw_value  # Return as-is if no pattern matches
            
            elif field_type == FieldType.PHONE:
                # Clean phone number
                phone = re.sub(r'[^\d]', '', raw_value)
                if len(phone) == 10:
                    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
                return raw_value
            
            elif field_type == FieldType.EMAIL:
                # Validate email format
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if re.match(email_pattern, raw_value):
                    return raw_value.lower()
                return None
            
            elif field_type == FieldType.SSN:
                # Format SSN
                ssn = re.sub(r'[^\d]', '', raw_value)
                if len(ssn) == 9:
                    return f"{ssn[:3]}-{ssn[3:5]}-{ssn[5:]}"
                return raw_value
            
            else:  # TEXT, ADDRESS, ARRAY, OBJECT
                return raw_value.strip()
        
        except Exception as e:
            logger.debug(f"Value conversion failed: {e}")
            return raw_value
    
    def _extract_employment_history(self, text: str) -> List[Dict[str, Any]]:
        """Extract comprehensive employment history."""
        employment_history = []
        
        # Pattern to find employment sections
        employment_pattern = r'Company\s+([^\n\r]+).*?(?=Company\s+[^\n\r]+|Unemployment|Trucking School|$)'
        
        matches = re.finditer(employment_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        for match in matches:
            employment_text = match.group(0)
            
            # Extract employment details
            employment = {
                'company_name': self._extract_employment_field(employment_text, r'Company\s+([^\n\r]+)'),
                'start_date': self._extract_employment_field(employment_text, r'Start Date\s+([^\n\r]+)'),
                'end_date': self._extract_employment_field(employment_text, r'End Date\s+([^\n\r]+)'),
                'address': self._extract_employment_field(employment_text, r'Address\s+([^\n\r]+)'),
                'city_state_zip': self._extract_employment_field(employment_text, r'City, State/Province Zip/Postal\s+([^\n\r]+)'),
                'country': self._extract_employment_field(employment_text, r'Country\s+([^\n\r]+)'),
                'phone': self._extract_employment_field(employment_text, r'Phone\s+([^\n\r]+)'),
                'fax': self._extract_employment_field(employment_text, r'Fax\s+([^\n\r]+)'),
                'position_held': self._extract_employment_field(employment_text, r'Position Held\s+([^\n\r]+)'),
                'reason_for_leaving': self._extract_employment_field(employment_text, r'Reason for leaving\?\s+([^\n\r]+)'),
                'terminated': self._extract_employment_boolean(employment_text, r'Were you terminated.*?\s+(Yes|No)'),
                'current_employer': self._extract_employment_boolean(employment_text, r'Is this your current employer\?\s+(Yes|No)'),
                'may_contact': self._extract_employment_boolean(employment_text, r'May we contact this employer.*?\s+(Yes|No)'),
                'operated_cmv': self._extract_employment_boolean(employment_text, r'Did you operate a commercial motor vehicle\?\s+(Yes|No)'),
                'subject_to_fmcsr': self._extract_employment_boolean(employment_text, r'Were you subject to the Federal Motor Carrier.*?\s+(Yes|No)'),
                'safety_sensitive_functions': self._extract_employment_boolean(employment_text, r'Did you perform any safety sensitive functions.*?\s+(Yes|No)'),
                'areas_driven': self._extract_employment_field(employment_text, r'Areas Driven\s+([^\n\r]+)'),
                'miles_driven_weekly': self._extract_employment_field(employment_text, r'Miles driven weekly\s+([^\n\r]+)'),
                'pay_range': self._extract_employment_field(employment_text, r'Pay Range.*?\s+([^\n\r]+)'),
                'most_common_truck': self._extract_employment_field(employment_text, r'Most common truck driven\s+([^\n\r]+)'),
                'most_common_trailer': self._extract_employment_field(employment_text, r'Most common trailer\s+([^\n\r]+)'),
                'trailer_length': self._extract_employment_field(employment_text, r'Trailer length\s+([^\n\r]+)')
            }
            
            # Only add if we have at least company name
            if employment['company_name']:
                employment_history.append(employment)
        
        # Also extract unemployment periods
        unemployment_pattern = r'Unemployment.*?Start Date\s+([^\n\r]+).*?End Date\s+([^\n\r]+).*?Comment\s+([^\n\r]+)'
        unemployment_matches = re.finditer(unemployment_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        for match in unemployment_matches:
            unemployment = {
                'company_name': 'UNEMPLOYMENT',
                'start_date': match.group(1).strip(),
                'end_date': match.group(2).strip(),
                'reason_for_leaving': match.group(3).strip(),
                'employment_type': 'unemployment'
            }
            employment_history.append(unemployment)
        
        # Sort by start date (most recent first)
        try:
            employment_history.sort(key=lambda x: x.get('start_date', ''), reverse=True)
        except TypeError:
            # If sorting fails due to None values, just return unsorted
            pass
        
        return employment_history
    
    def _extract_employment_field(self, text: str, pattern: str) -> Optional[str]:
        """Extract a field from employment text."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return value if value and value.lower() not in ['', 'none', 'n/a'] else None
        return None
    
    def _extract_employment_boolean(self, text: str, pattern: str) -> Optional[bool]:
        """Extract a boolean field from employment text."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip().lower()
            return value == 'yes'
        return None
    
    def _extract_accident_history(self, text: str) -> List[Dict[str, Any]]:
        """Extract vehicle accident history."""
        accidents = []
        
        # Look for accident sections
        accident_pattern = r'Type of Accident.*?(?=Type of Accident|Traffic Convictions|Criminal Record|$)'
        
        matches = re.finditer(accident_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        for match in matches:
            accident_text = match.group(0)
            
            accident = {
                'type': self._extract_employment_field(accident_text, r'Type of Accident.*?([^\n\r]+)'),
                'date': self._extract_employment_field(accident_text, r'Date of Accident.*?([^\n\r]+)'),
                'hazmat_involved': self._extract_employment_boolean(accident_text, r'Hazmat Accident.*?\s+(Yes|No)'),
                'vehicle_towed': self._extract_employment_boolean(accident_text, r'any vehicle towed away\?\s+(Yes|No)'),
                'city': self._extract_employment_field(accident_text, r'City\s+([^\n\r]+)'),
                'state': self._extract_employment_field(accident_text, r'State/Province\s+([^\n\r]+)'),
                'commercial_vehicle': self._extract_employment_boolean(accident_text, r'Were you in a commercial vehicle\?\s+(Yes|No)'),
                'dot_recordable': self._extract_employment_boolean(accident_text, r'Department of Transportation recordable accident\?\s+(Yes|No)'),
                'at_fault': self._extract_employment_boolean(accident_text, r'Were you at fault\?\s+(Yes|No)'),
                'ticketed': self._extract_employment_boolean(accident_text, r'Were you ticketed\?\s+(Yes|No)'),
                'description': self._extract_employment_field(accident_text, r'Description\s+([^\n\r]+(?:\n[^\n\r]+)*)')
            }
            
            # Only add if we have meaningful data
            if accident['type'] or accident['date']:
                accidents.append(accident)
        
        return accidents
    
    def _calculate_parsing_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate parsing confidence based on extracted data."""
        total_fields = len(self.field_mappings)
        extracted_fields = 0
        
        # Count non-null extracted fields
        for field in self.field_mappings:
            if field.field_name in result and result[field.field_name] is not None:
                extracted_fields += 1
        
        # Bonus for employment history
        if result.get('employment_history') and len(result['employment_history']) > 0:
            extracted_fields += 5  # Bonus for employment history
        
        # Bonus for required fields
        required_fields = ['full_name', 'email', 'license_number']
        for field in required_fields:
            if result.get(field):
                extracted_fields += 2  # Extra weight for required fields
        
        # Ensure we don't divide by zero and handle edge cases
        if total_fields == 0:
            confidence = 0.0
        else:
            confidence = min(100.0, (extracted_fields / total_fields) * 100)
        
        return round(confidence, 2)

# Example usage and testing
if __name__ == "__main__":
    parser = EnhancedTenstreetPDFParser()
    
    # Test with a sample PDF
    try:
        result = parser.parse_pdf("/home/ubuntu/pdf_parser_project/samples/Anthony_Thrower_269924480.pdf")
        print(f"Parsing completed with {result['parsing_confidence']}% confidence")
        print(f"Extracted {result['extraction_metadata']['fields_extracted']} fields")
        print(f"Found {len(result['employment_history'])} employment records")
        
        # Print some key extracted data
        print("\nKey extracted data:")
        print(f"Name: {result.get('full_name')}")
        print(f"Email: {result.get('email')}")
        print(f"License: {result.get('license_number')}")
        print(f"CDL: {result.get('has_cdl')}")
        print(f"Criminal Record: {result.get('convicted_of_crime')}")
        print(f"Drug Test Issues: {result.get('failed_drug_test')}")
        
    except Exception as e:
        print(f"Error: {e}")

