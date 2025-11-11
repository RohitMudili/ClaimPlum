"""
OCR utility for extracting text from images using Tesseract
Fallback option when Gemini Vision is unavailable or for cost optimization
"""
import pytesseract
from PIL import Image
import io
import logging
from typing import Optional
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OCRHelper:
    """Helper class for OCR operations using Tesseract"""

    def __init__(self):
        """Initialize OCR helper"""
        # Set Tesseract path if configured
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

    def extract_text_from_image(self, image_data: bytes) -> str:
        """
        Extract text from image using Tesseract OCR

        Args:
            image_data: Raw image bytes

        Returns:
            Extracted text
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Perform OCR
            text = pytesseract.image_to_string(image)

            logger.info(f"OCR extracted {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise

    def get_image_quality_score(self, image_data: bytes) -> float:
        """
        Assess image quality for OCR suitability

        Args:
            image_data: Raw image bytes

        Returns:
            Quality score between 0 and 1
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Basic quality checks
            width, height = image.size
            aspect_ratio = width / height if height > 0 else 0

            # Score based on resolution and aspect ratio
            score = 0.0

            # Resolution check (prefer higher resolution)
            if width >= 1200 or height >= 1200:
                score += 0.4
            elif width >= 800 or height >= 800:
                score += 0.3
            elif width >= 600 or height >= 600:
                score += 0.2
            else:
                score += 0.1

            # Aspect ratio check (prefer document-like ratios)
            if 0.5 <= aspect_ratio <= 2.0:
                score += 0.3
            else:
                score += 0.1

            # File format check
            if image.format in ['PNG', 'JPEG', 'JPG']:
                score += 0.3

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            return 0.5  # Default moderate quality

    def preprocess_image(self, image_data: bytes) -> bytes:
        """
        Preprocess image for better OCR results

        Args:
            image_data: Raw image bytes

        Returns:
            Preprocessed image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')

            # Increase contrast (simple method)
            # In production, consider more advanced preprocessing

            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()

        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image_data  # Return original if preprocessing fails
