"""
LLM Service for document understanding and data extraction using Gemini
"""
import google.generativeai as genai
from config import get_settings
import json
import logging
from typing import Optional, Dict, Any
import base64

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiService:
    """Service for interacting with Google Gemini API"""

    def __init__(self):
        """Initialize Gemini client"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured in environment")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)

        logger.info(f"Initialized Gemini service with model: {settings.LLM_MODEL}")

    def extract_from_image(self, image_data: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Extract structured data from medical document image using Gemini Vision

        Args:
            image_data: Raw image/PDF bytes
            mime_type: MIME type (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Extracted data as dictionary
        """
        try:
            prompt = self._get_extraction_prompt()

            # Create content with image
            image_part = {
                "mime_type": mime_type,
                "data": image_data
            }

            response = self.model.generate_content(
                [prompt, image_part],
                generation_config=genai.GenerationConfig(
                    temperature=settings.LLM_TEMPERATURE,
                    max_output_tokens=settings.LLM_MAX_TOKENS,
                )
            )

            # Parse JSON response
            result = self._parse_response(response.text)
            return result

        except Exception as e:
            logger.error(f"Gemini vision extraction failed: {str(e)}")
            raise

    def extract_from_text(self, text_content: str) -> Dict[str, Any]:
        """
        Extract structured data from OCR'd text using Gemini

        Args:
            text_content: Text extracted from document via OCR

        Returns:
            Extracted data as dictionary
        """
        try:
            prompt = self._get_extraction_prompt() + f"\n\nDocument Text:\n{text_content}"

            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=settings.LLM_TEMPERATURE,
                    max_output_tokens=settings.LLM_MAX_TOKENS,
                )
            )

            result = self._parse_response(response.text)
            return result

        except Exception as e:
            logger.error(f"Gemini text extraction failed: {str(e)}")
            raise

    def _get_extraction_prompt(self) -> str:
        """Get the extraction prompt for medical documents"""
        return """You are an expert medical document analyzer. Extract structured information from the provided medical document (prescription, bill, or both).

**IMPORTANT INSTRUCTIONS:**
1. Extract ALL information you can find, even if some fields are missing
2. For dates, convert to YYYY-MM-DD format
3. For doctor registration, extract the full registration number (e.g., KA/12345/2015)
4. For costs, extract individual line items and total
5. Return ONLY valid JSON, no markdown formatting, no extra text
6. If a field is not present, use null or empty array as appropriate
7. Always include a confidence_score (0.0 to 1.0) based on document quality and completeness

**Output JSON Schema:**
{
    "document_type": "prescription | bill | both",
    "confidence_score": 0.0-1.0,
    "doctor_info": {
        "name": "string",
        "registration_number": "string or null",
        "specialty": "string or null",
        "clinic_name": "string or null"
    },
    "patient_name": "string or null",
    "diagnosis": "string or null",
    "medications": [
        {
            "name": "string",
            "dosage": "string or null",
            "duration": "string or null"
        }
    ],
    "procedures": [
        {
            "name": "string",
            "cost": number or null
        }
    ],
    "diagnostic_tests": ["test1", "test2"],
    "costs": {
        "consultation": 0.0,
        "medicines": 0.0,
        "diagnostic_tests": 0.0,
        "procedures": 0.0,
        "other": 0.0,
        "total": 0.0
    },
    "dates": {
        "consultation_date": "YYYY-MM-DD or null",
        "prescription_date": "YYYY-MM-DD or null",
        "bill_date": "YYYY-MM-DD or null"
    },
    "hospital_name": "string or null",
    "notes": "string or null",
    "extraction_errors": []
}

**Now analyze the document and return ONLY the JSON:**"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract JSON"""
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            data = json.loads(text)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text[:200]}")
            # Return minimal valid structure
            return {
                "document_type": "unknown",
                "confidence_score": 0.0,
                "extraction_errors": [f"JSON parse error: {str(e)}"]
            }

    def calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on extracted data completeness

        Args:
            extracted_data: Extracted data dictionary

        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        total_fields = 10

        # Check key fields
        if extracted_data.get('doctor_info', {}).get('name'):
            score += 1
        if extracted_data.get('doctor_info', {}).get('registration_number'):
            score += 1
        if extracted_data.get('patient_name'):
            score += 1
        if extracted_data.get('diagnosis'):
            score += 1
        if extracted_data.get('medications'):
            score += 1
        if extracted_data.get('costs', {}).get('total', 0) > 0:
            score += 2  # Financial data is critical
        if extracted_data.get('dates', {}).get('consultation_date'):
            score += 1
        if extracted_data.get('hospital_name') or extracted_data.get('doctor_info', {}).get('clinic_name'):
            score += 1
        if len(extracted_data.get('extraction_errors', [])) == 0:
            score += 1

        return min(score / total_fields, 1.0)
