"""
Test script for document processor
Run this to test the document extraction pipeline
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.document_processor import DocumentProcessor
import json


def test_document(file_path: str):
    """Test document processing on a single file"""
    print(f"\n{'='*60}")
    print(f"Testing: {file_path}")
    print('='*60)

    # Read file
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Process
    processor = DocumentProcessor()
    result = processor.process_document(file_data, Path(file_path).name)

    # Display results
    print(f"\n✓ Success: {result.success}")
    print(f"✓ Method: {result.method_used}")
    print(f"✓ Time: {result.processing_time:.2f}s")

    if result.success and result.data:
        print(f"✓ Confidence: {result.data.confidence_score:.2f}")
        print(f"\nExtracted Data:")
        print(json.dumps(result.data.model_dump(), indent=2, default=str))
    else:
        print(f"\n✗ Error: {result.error}")


def main():
    """Test on sample documents"""
    # Test paths
    test_files = [
        "../test-docs/TC001/prescription.html.pdf",
        "../test-docs/TC001/bill.html.pdf",
        # Add more test files as needed
    ]

    for file_path in test_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            try:
                test_document(str(full_path))
            except Exception as e:
                print(f"✗ Test failed: {str(e)}")
        else:
            print(f"✗ File not found: {full_path}")


if __name__ == "__main__":
    print("Document Processor Test")
    print("Make sure you have:")
    print("1. Installed dependencies: pip install -r requirements.txt")
    print("2. Set GEMINI_API_KEY in .env file")
    print("3. (Optional) Installed Tesseract OCR for fallback\n")

    main()
