"""
Claims API endpoints using Supabase
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from typing import Optional
from datetime import datetime
import shutil
from pathlib import Path

from db.supabase_client import get_supabase, get_supabase_admin
from services.document_processor import DocumentProcessor
from services.adjudication_engine import AdjudicationEngine
from models.decision import MemberInfo as AdjMemberInfo
from config import get_settings

router = APIRouter(prefix="/api/claims", tags=["claims"])
settings = get_settings()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


async def _process_non_member_preview(
    prescription: Optional[UploadFile],
    bill: Optional[UploadFile],
    member_name: Optional[str],
    contact_email: Optional[str],
    contact_phone: Optional[str]
):
    """
    Process documents for non-member as sales preview
    Shows what they WOULD get with Plum coverage
    Even works without documents - shows generic sales pitch
    """
    try:
        # If no documents provided, show generic sales pitch
        if not prescription and not bill:
            return {
                "decision": "NOT_A_MEMBER",
                "message": "🎉 Great news! We'd love to help cover your medical expenses.",
                "sales_pitch": {
                    "headline": "Join thousands of companies using Plum!",
                    "value_proposition": "Get comprehensive OPD coverage for your team starting at just ₹500/employee/month",
                    "cta": "Get your team covered in just 2 minutes",
                    "cta_url": "https://plumhq.com/get-quote",
                    "urgency": "Join 5,000+ companies trusting Plum for healthcare"
                },
                "policy_benefits": {
                    "annual_coverage": "₹50,000 per employee",
                    "opd_coverage": "Consultations, diagnostics, pharmacy",
                    "network_hospitals": "5,000+ partner hospitals",
                    "cashless_claims": "Instant approval up to ₹5,000",
                    "fast_processing": "Claims processed in <2 minutes"
                },
                "next_steps": [
                    "Visit plumhq.com to get a free quote",
                    "Share your company details for a custom plan",
                    "Get your team covered and start saving today!"
                ],
                "contact_info": {
                    "email": "sales@plumhq.com",
                    "phone": "+91-80-1234-5678",
                    "website": "https://plumhq.com"
                },
                "lead_captured": bool(contact_email or contact_phone)
            }

        # Process documents to extract data
        processor = DocumentProcessor()
        merged_data = None

        # Read and process prescription if provided
        if prescription:
            prescription_data = await prescription.read()
            prescription_result = processor.process_document(prescription_data, prescription.filename)
            if prescription_result.success:
                merged_data = prescription_result.data

        # Read and process bill if provided
        if bill:
            bill_data = await bill.read()
            bill_result = processor.process_document(bill_data, bill.filename)

            # Merge bill data if we have prescription data already
            if bill_result.success and merged_data:
                if bill_result.data.costs:
                    merged_data.costs = bill_result.data.costs
                if bill_result.data.hospital_name:
                    merged_data.hospital_name = bill_result.data.hospital_name
            # If no prescription but bill succeeded, use bill data
            elif bill_result.success:
                merged_data = bill_result.data

        # If still no merged_data (both documents failed or missing), return generic sales pitch
        if not merged_data:
            return {
                "decision": "NOT_A_MEMBER",
                "message": "🎉 Great news! We'd love to help cover your medical expenses.",
                "sales_pitch": {
                    "headline": "Join thousands of companies using Plum!",
                    "value_proposition": "Get comprehensive OPD coverage for your team starting at just ₹500/employee/month",
                    "benefits": [
                        "✓ No waiting period - instant coverage",
                        "✓ Cover consultation, diagnostics, pharmacy bills",
                        "✓ Digital-first experience with quick claim approvals",
                        "✓ Flexible plans from ₹50,000 to ₹1,00,000 per employee"
                    ],
                    "cta": "Get your team covered in just 2 minutes",
                    "cta_url": "https://plumhq.com/get-quote",
                    "urgency": "Join 5,000+ companies trusting Plum for healthcare"
                }
            }

        # Create hypothetical member for calculation
        hypothetical_member = AdjMemberInfo(
            member_id="PREVIEW",
            member_name=member_name or "Potential Customer",
            policy_start_date=datetime.utcnow().strftime('%Y-%m-%d'),
            policy_status="active",
            ytd_claims=0.0,
            previous_claims=[]
        )

        # Run adjudication to show potential savings
        engine = AdjudicationEngine()
        preview_decision = engine.adjudicate_claim(merged_data, hypothetical_member)

        claimed_amount = merged_data.costs.total if merged_data.costs else 0.0
        potential_savings = claimed_amount - preview_decision.approved_amount if preview_decision.approved_amount > 0 else 0
        coverage_percentage = (preview_decision.approved_amount / claimed_amount * 100) if claimed_amount > 0 else 0

        # Build sales conversion response
        return {
            "decision": "NOT_A_MEMBER",
            "message": "🎉 Great news! We'd love to help cover these medical expenses.",
            "sales_pitch": {
                "headline": "You're not covered yet, but you could be!",
                "value_proposition": f"With Plum, you would have saved ₹{potential_savings:.2f} on this claim ({coverage_percentage:.0f}% coverage).",
                "cta": "Get your team covered in just 2 minutes",
                "cta_url": "https://plumhq.com/get-quote",
                "urgency": "Join 5,000+ companies trusting Plum for healthcare"
            },
            "claim_preview": {
                "your_claim_amount": claimed_amount,
                "plum_would_cover": preview_decision.approved_amount,
                "your_savings": potential_savings,
                "coverage_percentage": round(coverage_percentage, 1),
                "copay_details": {
                    "consultation": f"Only 10% copay (you pay ₹{preview_decision.deductions.copay:.0f})",
                    "network_discount": f"20% discount at network hospitals (₹{preview_decision.deductions.network_discount:.0f} saved)"
                },
                "what_we_found": {
                    "diagnosis": merged_data.diagnosis or "Treatment reviewed",
                    "hospital": merged_data.hospital_name or "Hospital visit",
                    "doctor": merged_data.doctor_info.name if merged_data.doctor_info else "Medical professional"
                }
            },
            "policy_benefits": {
                "annual_coverage": "₹50,000 per employee",
                "opd_coverage": "Consultations, diagnostics, pharmacy",
                "network_hospitals": "5,000+ partner hospitals",
                "cashless_claims": "Instant approval up to ₹5,000",
                "fast_processing": "Claims processed in <2 minutes"
            },
            "next_steps": [
                "Visit plumhq.com to get a free quote",
                "Share your company details for a custom plan",
                "Get your team covered and start saving today!"
            ],
            "contact_info": {
                "email": "sales@plumhq.com",
                "phone": "+91-80-1234-5678",
                "website": "https://plumhq.com"
            },
            "lead_captured": bool(contact_email or contact_phone),
            "confidence_score": preview_decision.confidence_score
        }

    except Exception as e:
        # Even if processing fails, return sales response
        return {
            "decision": "NOT_A_MEMBER",
            "message": "We'd love to help! This ID isn't in our system, but you can get coverage for your team.",
            "sales_pitch": {
                "headline": "Join thousands of companies using Plum",
                "value_proposition": "Comprehensive OPD coverage starting at just ₹500/employee/month",
                "cta": "Get a free quote in 2 minutes",
                "cta_url": "https://plumhq.com/get-quote"
            },
            "error_note": "We couldn't fully process your documents, but we'd still love to help you get covered!",
            "next_steps": [
                "Visit plumhq.com for a free consultation",
                "Speak to our sales team for custom pricing"
            ]
        }


@router.post("/upload")
async def upload_documents(
    member_id: Optional[str] = Form(None),
    prescription: Optional[UploadFile] = File(None),
    bill: Optional[UploadFile] = File(None),
    member_name: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    supabase=Depends(get_supabase_admin)
):
    """
    Upload claim documents - ALL FIELDS OPTIONAL

    For NON-MEMBERS: Returns sales conversion response with claim preview
    For MEMBERS: Normal claim upload flow
    """
    # If no member_id provided, treat as non-member
    if not member_id:
        return await _process_non_member_preview(
            prescription=prescription,
            bill=bill,
            member_name=member_name,
            contact_email=contact_email,
            contact_phone=contact_phone
        )

    # Check if member exists
    member_result = supabase.table("members").select("*").eq("id", member_id).execute()

    # SALES CONVERSION OPPORTUNITY: Non-member trying to submit claim
    if not member_result.data:
        # Log as sales lead if contact info provided
        if contact_email or contact_phone:
            try:
                lead_data = {
                    "member_id": member_id,
                    "name": member_name,
                    "email": contact_email,
                    "phone": contact_phone,
                    "source": "claim_upload_attempt",
                    "created_at": datetime.utcnow().isoformat()
                }
                # Store in a leads table (you can create this later)
                # supabase.table("sales_leads").insert(lead_data).execute()
            except:
                pass  # Don't fail if lead capture fails

        # Return sales conversion response with claim preview
        return await _process_non_member_preview(
            prescription=prescription,
            bill=bill,
            member_name=member_name,
            contact_email=contact_email,
            contact_phone=contact_phone
        )

    # Check which documents are missing and reject claim if any are missing
    missing_docs = []
    if not prescription:
        missing_docs.append("prescription")
    if not bill:
        missing_docs.append("bill")

    if missing_docs:
        raise HTTPException(
            status_code=400,
            detail=f"Claim rejected: Missing required document(s): {', '.join(missing_docs)}"
        )

    # Generate claim ID
    claims_count = supabase.table("claims").select("id", count="exact").execute()
    claim_id = f"CLM_{claims_count.count + 1:06d}"

    # Create claim record
    claim_data = {
        "claim_id": claim_id,
        "member_id": member_id,
        "status": "PENDING",
        "submission_date": datetime.utcnow().isoformat()
    }
    claim_result = supabase.table("claims").insert(claim_data).execute()
    claim = claim_result.data[0]

    # Save files
    files_saved = []
    try:
        # Save prescription
        prescription_filename = f"{claim_id}_prescription_{prescription.filename}"
        prescription_path = UPLOAD_DIR / prescription_filename
        with prescription_path.open("wb") as buffer:
            shutil.copyfileobj(prescription.file, buffer)
        files_saved.append(prescription_path)

        # Save bill
        bill_filename = f"{claim_id}_bill_{bill.filename}"
        bill_path = UPLOAD_DIR / bill_filename
        with bill_path.open("wb") as buffer:
            shutil.copyfileobj(bill.file, buffer)
        files_saved.append(bill_path)

        # Create document records
        documents = [
            {
                "claim_id": claim["id"],
                "document_type": "PRESCRIPTION",
                "file_name": prescription.filename,
                "file_path": str(prescription_path),
                "processing_status": "pending"
            },
            {
                "claim_id": claim["id"],
                "document_type": "BILL",
                "file_name": bill.filename,
                "file_path": str(bill_path),
                "processing_status": "pending"
            }
        ]

        supabase.table("documents").insert(documents).execute()

        return {
            "claim_id": claim_id,
            "status": "uploaded",
            "message": "Documents uploaded successfully. Use /process endpoint to process claim.",
            "documents": {
                "prescription": prescription_filename,
                "bill": bill_filename
            }
        }

    except Exception as e:
        # Clean up uploaded files on error
        for file_path in files_saved:
            if file_path.exists():
                file_path.unlink()
        # Delete claim record
        supabase.table("claims").delete().eq("id", claim["id"]).execute()
        raise HTTPException(status_code=500, detail=f"Failed to upload documents: {str(e)}")


@router.post("/process/{claim_id}")
async def process_claim(
    claim_id: str,
    supabase=Depends(get_supabase_admin)
):
    """Process a claim"""
    # Get claim
    claim_result = supabase.table("claims").select("*, members(*)").eq("claim_id", claim_id).execute()
    if not claim_result.data:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim = claim_result.data[0]

    if claim["status"] == "COMPLETED":
        raise HTTPException(status_code=400, detail="Claim already processed")

    # Update status
    supabase.table("claims").update({"status": "PROCESSING"}).eq("id", claim["id"]).execute()

    try:
        # Get documents
        docs_result = supabase.table("documents").select("*").eq("claim_id", claim["id"]).execute()
        documents = docs_result.data

        prescription_doc = next((d for d in documents if d["document_type"] == "PRESCRIPTION"), None)
        bill_doc = next((d for d in documents if d["document_type"] == "BILL"), None)

        if not prescription_doc or not bill_doc:
            raise HTTPException(status_code=400, detail="Missing documents")

        # Process documents
        processor = DocumentProcessor()

        # Process prescription
        with open(prescription_doc["file_path"], 'rb') as f:
            prescription_data = f.read()
        prescription_result = processor.process_document(prescription_data, prescription_doc["file_name"])

        if not prescription_result.success:
            raise Exception(f"Prescription processing failed: {prescription_result.error}")

        # Process bill
        with open(bill_doc["file_path"], 'rb') as f:
            bill_data = f.read()
        bill_result = processor.process_document(bill_data, bill_doc["file_name"])

        if not bill_result.success:
            raise Exception(f"Bill processing failed: {bill_result.error}")

        # Merge extracted data
        merged_data = prescription_result.data
        if bill_result.data.costs:
            merged_data.costs = bill_result.data.costs
        if bill_result.data.hospital_name:
            merged_data.hospital_name = bill_result.data.hospital_name

        # Get member info
        member = claim["members"]
        adj_member_info = AdjMemberInfo(
            member_id=member["id"],
            member_name=member["name"],
            policy_start_date=member["policy_start_date"][:10],  # YYYY-MM-DD
            policy_status=member["policy_status"],
            ytd_claims=float(member["ytd_claims"]),
            previous_claims=[]
        )

        # Adjudicate claim
        engine = AdjudicationEngine()
        decision = engine.adjudicate_claim(merged_data, adj_member_info)

        # Update claim
        claim_update = {
            "claim_amount": merged_data.costs.total if merged_data.costs else 0.0,
            "approved_amount": decision.approved_amount,
            "decision": decision.decision.value,
            "confidence_score": float(decision.confidence_score),
            "status": "COMPLETED",
            "processed_at": datetime.utcnow().isoformat()
        }
        supabase.table("claims").update(claim_update).eq("id", claim["id"]).execute()

        # Save decision
        decision_record = {
            "claim_id": claim["id"],
            "decision_type": decision.decision.value,
            "approved_amount": decision.approved_amount,
            "claimed_amount": decision.claimed_amount,
            "copay_amount": decision.deductions.copay,
            "non_covered_amount": decision.deductions.non_covered_items,
            "exceeded_limits_amount": decision.deductions.exceeded_limits,
            "network_discount": decision.deductions.network_discount,
            "confidence_score": float(decision.confidence_score),
            "fraud_flags": decision.fraud_flags,
            "rejection_reasons": [r.model_dump() for r in decision.rejection_reasons],
            "adjudication_steps": decision.adjudication_steps.model_dump(),
            "notes": decision.notes,
            "next_steps": decision.next_steps,
            "is_network_hospital": decision.is_network_hospital,
            "cashless_approved": decision.cashless_approved
        }
        supabase.table("decisions").insert(decision_record).execute()

        # Update member YTD if approved
        if decision.decision.value in ["APPROVED", "PARTIAL"]:
            new_ytd = float(member["ytd_claims"]) + decision.approved_amount
            supabase.table("members").update({"ytd_claims": new_ytd}).eq("id", member["id"]).execute()

        return {
            "claim_id": claim_id,
            "decision": decision.decision.value,
            "approved_amount": decision.approved_amount,
            "claimed_amount": decision.claimed_amount,
            "confidence_score": decision.confidence_score,
            "deductions": {
                "copay": decision.deductions.copay,
                "non_covered": decision.deductions.non_covered_items,
                "exceeded_limits": decision.deductions.exceeded_limits,
                "network_discount": decision.deductions.network_discount
            },
            "rejection_reasons": [r.model_dump() for r in decision.rejection_reasons],
            "fraud_flags": decision.fraud_flags,
            "notes": decision.notes,
            "next_steps": decision.next_steps
        }

    except Exception as e:
        supabase.table("claims").update({"status": "FAILED"}).eq("id", claim["id"]).execute()
        raise HTTPException(status_code=500, detail=f"Claim processing failed: {str(e)}")


@router.get("/{claim_id}")
async def get_claim(claim_id: str, supabase=Depends(get_supabase)):
    """Get claim details"""
    result = supabase.table("claims").select("*, members(name)").eq("claim_id", claim_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim = result.data[0]
    return {
        "claim_id": claim["claim_id"],
        "member_id": claim["member_id"],
        "member_name": claim["members"]["name"],
        "status": claim["status"],
        "submission_date": claim["submission_date"],
        "claim_amount": claim["claim_amount"],
        "approved_amount": claim["approved_amount"],
        "decision": claim["decision"],
        "confidence_score": claim["confidence_score"],
        "processed_at": claim["processed_at"]
    }


@router.get("")
async def list_claims(
    member_id: Optional[str] = None,
    status: Optional[str] = None,
    supabase=Depends(get_supabase)
):
    """List claims"""
    query = supabase.table("claims").select("*, members(name)")

    if member_id:
        query = query.eq("member_id", member_id)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).limit(50).execute()

    return {
        "claims": [
            {
                "claim_id": c["claim_id"],
                "member_id": c["member_id"],
                "member_name": c["members"]["name"],
                "status": c["status"],
                "claim_amount": c["claim_amount"],
                "approved_amount": c["approved_amount"],
                "decision": c["decision"],
                "submission_date": c["submission_date"]
            }
            for c in result.data
        ]
    }
