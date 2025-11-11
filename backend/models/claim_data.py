"""
Pydantic models for claim data extraction and validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class DoctorInfo(BaseModel):
    """Doctor information extracted from prescription"""
    name: Optional[str] = Field(None, description="Doctor's full name")
    registration_number: Optional[str] = Field(None, description="Medical registration number (e.g., KA/12345/2015)")
    specialty: Optional[str] = Field(None, description="Medical specialty")
    clinic_name: Optional[str] = Field(None, description="Clinic or hospital name")

    @field_validator('registration_number')
    @classmethod
    def validate_registration(cls, v):
        """Validate doctor registration format"""
        if v and not any(char in v for char in ['/', '-']):
            return None  # Invalid format, return None instead of raising
        return v


class Medication(BaseModel):
    """Individual medication details"""
    name: str = Field(..., description="Medicine name")
    dosage: Optional[str] = Field(None, description="Dosage information")
    duration: Optional[str] = Field(None, description="Duration/frequency")


class Procedure(BaseModel):
    """Medical procedure details"""
    name: str = Field(..., description="Procedure name")
    cost: Optional[float] = Field(None, description="Procedure cost")


class CostBreakdown(BaseModel):
    """Cost breakdown from bill"""
    consultation: float = Field(0.0, description="Consultation fees")
    medicines: float = Field(0.0, description="Medicine costs")
    diagnostic_tests: float = Field(0.0, description="Diagnostic test costs")
    procedures: float = Field(0.0, description="Procedure costs")
    other: float = Field(0.0, description="Other charges")
    total: float = Field(..., description="Total claim amount")

    @field_validator('total')
    @classmethod
    def validate_total(cls, v, info):
        """Ensure total matches sum of components"""
        values = info.data
        calculated = (
            values.get('consultation', 0) +
            values.get('medicines', 0) +
            values.get('diagnostic_tests', 0) +
            values.get('procedures', 0) +
            values.get('other', 0)
        )
        # If total is significantly different, trust the explicitly stated total
        if v == 0 and calculated > 0:
            return calculated
        return v


class DateInfo(BaseModel):
    """Date information from documents"""
    consultation_date: Optional[str] = Field(None, description="Date of consultation (YYYY-MM-DD)")
    prescription_date: Optional[str] = Field(None, description="Date of prescription (YYYY-MM-DD)")
    bill_date: Optional[str] = Field(None, description="Date of bill (YYYY-MM-DD)")

    @field_validator('consultation_date', 'prescription_date', 'bill_date')
    @classmethod
    def normalize_date(cls, v):
        """Normalize date to YYYY-MM-DD format"""
        if not v:
            return None

        # Try to parse various date formats
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']:
            try:
                dt = datetime.strptime(v, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # If can't parse, return as-is
        return v


class ExtractedData(BaseModel):
    """Complete extracted data from medical documents"""

    # Document metadata
    document_type: str = Field(..., description="Type: prescription, bill, or both")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Extraction confidence (0-1)")

    # Medical information
    doctor_info: Optional[DoctorInfo] = None
    patient_name: Optional[str] = Field(None, description="Patient name")
    diagnosis: Optional[str] = Field(None, description="Medical diagnosis")
    medications: List[Medication] = Field(default_factory=list, description="Prescribed medications")
    procedures: List[Procedure] = Field(default_factory=list, description="Medical procedures")
    diagnostic_tests: List[str] = Field(default_factory=list, description="Diagnostic tests performed")

    # Financial information
    costs: Optional[CostBreakdown] = None

    # Date information
    dates: Optional[DateInfo] = None

    # Additional context
    hospital_name: Optional[str] = Field(None, description="Hospital/clinic name from bill")
    notes: Optional[str] = Field(None, description="Additional notes or observations")
    extraction_errors: List[str] = Field(default_factory=list, description="Any extraction errors")

    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "both",
                "confidence_score": 0.95,
                "doctor_info": {
                    "name": "Dr. Sharma",
                    "registration_number": "KA/45678/2015",
                    "specialty": "General Physician"
                },
                "patient_name": "Rajesh Kumar",
                "diagnosis": "Viral fever",
                "medications": [
                    {"name": "Paracetamol 650mg", "dosage": "1-0-1", "duration": "3 days"}
                ],
                "costs": {
                    "consultation": 1000.0,
                    "diagnostic_tests": 500.0,
                    "total": 1500.0
                },
                "dates": {
                    "consultation_date": "2024-11-01"
                }
            }
        }


class ProcessingResult(BaseModel):
    """Result of document processing"""
    success: bool = Field(..., description="Whether processing succeeded")
    data: Optional[ExtractedData] = Field(None, description="Extracted data if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: float = Field(..., description="Processing time in seconds")
    method_used: str = Field(..., description="Method used: gemini_vision, gemini_ocr, tesseract")
