"""
Test script for adjudication engine
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.document_processor import DocumentProcessor
from services.adjudication_engine import AdjudicationEngine
from models.decision import MemberInfo
import json


def test_full_workflow(prescription_path: str, bill_path: str, member_info: MemberInfo):
    """Test complete workflow: document processing + adjudication"""
    print(f"\n{'='*70}")
    print(f"Testing Complete Workflow")
    print('='*70)

    # Step 1: Process documents (both prescription and bill)
    print("\n[1/3] Processing Prescription...")
    processor = DocumentProcessor()

    with open(prescription_path, 'rb') as f:
        prescription_data = f.read()

    prescription_result = processor.process_document(prescription_data, Path(prescription_path).name)

    if not prescription_result.success:
        print(f"✗ Prescription processing failed: {prescription_result.error}")
        return

    print(f"✓ Prescription processed (confidence: {prescription_result.data.confidence_score:.2f})")
    print(f"  Doctor: {prescription_result.data.doctor_info.name if prescription_result.data.doctor_info else 'N/A'}")
    print(f"  Diagnosis: {prescription_result.data.diagnosis}")

    # Step 2: Process bill
    print("\n[2/3] Processing Bill...")
    with open(bill_path, 'rb') as f:
        bill_data = f.read()

    bill_result = processor.process_document(bill_data, Path(bill_path).name)

    if not bill_result.success:
        print(f"✗ Bill processing failed: {bill_result.error}")
        return

    print(f"✓ Bill processed (confidence: {bill_result.data.confidence_score:.2f})")
    print(f"  Amount: ₹{bill_result.data.costs.total if bill_result.data.costs else 0:.2f}")

    # Merge data from both documents
    merged_data = prescription_result.data
    if bill_result.data.costs:
        merged_data.costs = bill_result.data.costs
    if bill_result.data.hospital_name:
        merged_data.hospital_name = bill_result.data.hospital_name

    print(f"\n✓ Combined extraction:")
    print(f"  Patient: {merged_data.patient_name}")
    print(f"  Diagnosis: {merged_data.diagnosis}")
    print(f"  Amount: ₹{merged_data.costs.total if merged_data.costs else 0:.2f}")

    # Step 3: Adjudicate claim
    print("\n[3/3] Adjudicating Claim...")
    engine = AdjudicationEngine()
    decision = engine.adjudicate_claim(merged_data, member_info)

    print(f"\n{'='*70}")
    print(f"DECISION: {decision.decision.value}")
    print('='*70)
    print(f"Claimed Amount:  ₹{decision.claimed_amount:.2f}")
    print(f"Approved Amount: ₹{decision.approved_amount:.2f}")
    print(f"Confidence:      {decision.confidence_score:.2f}")

    if decision.deductions.copay > 0:
        print(f"\nDeductions:")
        print(f"  Copay: ₹{decision.deductions.copay:.2f}")

    if decision.rejection_reasons:
        print(f"\nRejection Reasons:")
        for reason in decision.rejection_reasons:
            print(f"  [{reason.code}] {reason.message}")

    if decision.fraud_flags:
        print(f"\nFraud Flags:")
        for flag in decision.fraud_flags:
            print(f"  ⚠ {flag}")

    print(f"\nAdjudication Steps:")
    print(f"  Eligibility:        {decision.adjudication_steps.eligibility.value}")
    print(f"  Documents:          {decision.adjudication_steps.documents.value}")
    print(f"  Coverage:           {decision.adjudication_steps.coverage.value}")
    print(f"  Limits:             {decision.adjudication_steps.limits.value}")
    print(f"  Medical Necessity:  {decision.adjudication_steps.medical_necessity.value}")

    print(f"\nNotes: {decision.notes}")
    print(f"Next Steps: {decision.next_steps}")

    print(f"\n{'='*70}\n")


def main():
    """Run tests"""
    print("Adjudication Engine Test")
    print("=" * 70)

    # Test Case 1: Simple consultation (should be APPROVED)
    member_tc001 = MemberInfo(
        member_id="EMP001",
        member_name="Rajesh Kumar",
        policy_start_date="2024-01-01",
        policy_status="active",
        ytd_claims=0.0,
        previous_claims=[]
    )

    test_full_workflow(
        "../test-docs/TC001/prescription.html.pdf",
        "../test-docs/TC001/bill.html.pdf",
        member_tc001
    )

    # Test Case 2: Limit exceeded (should be REJECTED)
    member_tc003 = MemberInfo(
        member_id="EMP003",
        member_name="Amit Verma",
        policy_start_date="2024-01-01",
        policy_status="active",
        ytd_claims=0.0,
        previous_claims=[]
    )

    test_full_workflow(
        "../test-docs/TC003/prescription.html.pdf",
        "../test-docs/TC003/bill.html.pdf",
        member_tc003
    )

    # Test Case 3: Waiting period (should be REJECTED)
    member_tc005 = MemberInfo(
        member_id="EMP005",
        member_name="Vikram Joshi",
        policy_start_date="2024-09-01",  # Policy just started
        policy_status="active",
        ytd_claims=0.0,
        previous_claims=[]
    )

    test_full_workflow(
        "../test-docs/TC005/prescription.html.pdf",
        "../test-docs/TC005/bill.html.pdf",
        member_tc005
    )


if __name__ == "__main__":
    print("Make sure you have:")
    print("1. Set GEMINI_API_KEY in .env file")
    print("2. Run document processing tests first")
    print()

    main()
