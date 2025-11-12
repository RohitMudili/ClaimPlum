"""
Document Processing Service - Main orchestrator for document extraction pipeline

Architecture:
1. Pre-processing: File validation, format detection, quality check
2. OCR Layer: Gemini Vision (primary) → Tesseract (fallback)
3. LLM Extraction: Structured data extraction with validation
4. Post-processing: Data validation, normalization, confidence scoring
"""
import logging
import time
from typing import BinaryIO, Tuple
from pathlib import Path
import pypdf
import io

from models.claim_data import ExtractedData, ProcessingResult
from services.llm_service import GeminiService
from utils.ocr_helper import OCRHelper
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentProcessor:
    """Main document processing orchestrator"""

    def __init__(self):
        """Initialize document processor with services"""
        self.gemini_service = GeminiService()
        self.ocr_helper = OCRHelper()
        logger.info("Document processor initialized")

    def process_document(self, file_data: bytes, filename: str) -> ProcessingResult:
        """
        Process uploaded medical document and extract structured data

        Args:
            file_data: Raw file bytes
            filename: Original filename

        Returns:
            ProcessingResult with extracted data or error
        """
        start_time = time.time()

        try:
            # Step 1: Pre-processing
            logger.info(f"Processing document: {filename}")
            file_type, mime_type = self._detect_file_type(filename, file_data)

            if not self._validate_file(file_data, file_type):
                return ProcessingResult(
                    success=False,
                    error="Invalid or corrupted file",
                    processing_time=time.time() - start_time,
                    method_used="validation_failed"
                )

            # Step 2: Extract content (try multiple methods)
            extraction_result = self._extract_with_fallback(file_data, file_type, mime_type)

            if not extraction_result['success']:
                return ProcessingResult(
                    success=False,
                    error=extraction_result['error'],
                    processing_time=time.time() - start_time,
                    method_used=extraction_result['method']
                )

            # Step 3: Validate and normalize extracted data
            extracted_data = self._validate_and_normalize(extraction_result['data'])

            # Step 4: Calculate final confidence score
            if extracted_data.confidence_score == 0.0:
                extracted_data.confidence_score = self.gemini_service.calculate_confidence(
                    extraction_result['data']
                )

            processing_time = time.time() - start_time
            logger.info(
                f"Document processed successfully in {processing_time:.2f}s "
                f"(method: {extraction_result['method']}, confidence: {extracted_data.confidence_score:.2f})"
            )

            return ProcessingResult(
                success=True,
                data=extracted_data,
                processing_time=processing_time,
                method_used=extraction_result['method']
            )

        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}", exc_info=True)
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time,
                method_used="error"
            )

    def _detect_file_type(self, filename: str, file_data: bytes) -> Tuple[str, str]:
        """
        Detect file type from filename and magic bytes

        Returns:
            (file_type, mime_type)
        """
        ext = Path(filename).suffix.lower()

        # Check magic bytes for verification
        if file_data.startswith(b'%PDF'):
            return 'pdf', 'application/pdf'
        elif file_data.startswith(b'\xff\xd8\xff'):
            return 'jpg', 'image/jpeg'
        elif file_data.startswith(b'\x89PNG'):
            return 'png', 'image/png'

        # Fallback to extension
        mime_map = {
            '.pdf': ('pdf', 'application/pdf'),
            '.png': ('png', 'image/png'),
            '.jpg': ('jpg', 'image/jpeg'),
            '.jpeg': ('jpg', 'image/jpeg'),
        }

        return mime_map.get(ext, ('unknown', 'application/octet-stream'))

    def _validate_file(self, file_data: bytes, file_type: str) -> bool:
        """Validate file integrity and size"""

        # Check size
        if len(file_data) > settings.MAX_UPLOAD_SIZE:
            logger.error(f"File too large: {len(file_data)} bytes")
            return False

        if len(file_data) < 100:  # Too small to be valid
            logger.error("File too small")
            return False

        # Type-specific validation
        try:
            if file_type == 'pdf':
                # Try to open with pypdf
                pdf = pypdf.PdfReader(io.BytesIO(file_data))
                if len(pdf.pages) == 0:
                    return False

            elif file_type in ['jpg', 'png']:
                # Try to open with PIL
                from PIL import Image
                Image.open(io.BytesIO(file_data))

            return True

        except Exception as e:
            logger.error(f"File validation failed: {str(e)}")
            return False

    def _extract_with_fallback(self, file_data: bytes, file_type: str, mime_type: str) -> dict:
        """
        Extract data using multiple methods with intelligent fallback

        Priority:
        1. Gemini Vision (fast, accurate, works with PDF and images)
        2. Tesseract OCR + Gemini Text (fallback for cost or API issues)

        Returns:
            Dict with success, data/error, and method used
        """

        # Method 1: Try Gemini Vision first (best quality)
        # Gemini 2.5 Flash can read PDFs directly!
        try:
            logger.info("Attempting extraction with Gemini Vision...")

            # Send file directly to Gemini (works for both PDF and images)
            extracted_data = self.gemini_service.extract_from_image(
                file_data, mime_type
            )

            return {
                'success': True,
                'data': extracted_data,
                'method': 'gemini_vision'
            }

        except Exception as e:
            logger.warning(f"Gemini Vision failed: {str(e)}. Trying fallback...")

        # Method 2: Fallback to pypdf text extraction + Gemini
        try:
            logger.info("Attempting extraction with text extraction + Gemini...")

            # For PDF, extract text with pypdf
            if file_type == 'pdf':
                pdf = pypdf.PdfReader(io.BytesIO(file_data))
                text_parts = []
                for page in pdf.pages:
                    text_parts.append(page.extract_text())
                ocr_text = "\n".join(text_parts)

                if not ocr_text.strip():
                    raise ValueError("PDF text extraction returned empty text")

            # For images, use Tesseract OCR
            else:
                ocr_text = self.ocr_helper.extract_text_from_image(file_data)

                if not ocr_text.strip():
                    raise ValueError("OCR returned empty text")

            # Use Gemini to structure the text
            extracted_data = self.gemini_service.extract_from_text(ocr_text)

            return {
                'success': True,
                'data': extracted_data,
                'method': 'text_extraction_gemini'
            }

        except Exception as e:
            logger.error(f"All extraction methods failed: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to extract data: {str(e)}",
                'method': 'all_failed'
            }

    def _pdf_to_image(self, pdf_data: bytes) -> bytes:
        """
        Convert first page of PDF to image

        Args:
            pdf_data: PDF file bytes

        Returns:
            PNG image bytes
        """
        try:
            from pdf2image import convert_from_bytes

            images = convert_from_bytes(pdf_data, first_page=1, last_page=1)

            if not images:
                raise ValueError("No pages in PDF")

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()

        except ImportError:
            logger.warning("pdf2image not available, using pypdf text extraction")
            # Fallback: extract text from PDF
            pdf = pypdf.PdfReader(io.BytesIO(pdf_data))
            text = pdf.pages[0].extract_text()

            # For this fallback, we'll need to process as text
            # This is not ideal but works as last resort
            raise NotImplementedError("PDF to image conversion requires pdf2image library")

    def _validate_and_normalize(self, raw_data: dict) -> ExtractedData:
        """
        Validate extracted data and normalize to ExtractedData model

        Args:
            raw_data: Raw dictionary from LLM

        Returns:
            Validated ExtractedData instance
        """
        try:
            # Pydantic will validate and normalize
            return ExtractedData(**raw_data)

        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            # Return minimal valid structure
            return ExtractedData(
                document_type="unknown",
                confidence_score=0.0,
                extraction_errors=[f"Validation error: {str(e)}"]
            )
