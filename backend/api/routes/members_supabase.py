"""
Members API endpoints using Supabase
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from db.supabase_client import get_supabase, get_supabase_admin

router = APIRouter(prefix="/api/members", tags=["members"])


class MemberCreate(BaseModel):
    """Schema for creating a new member"""
    id: str
    name: str
    policy_number: str
    policy_start_date: str  # YYYY-MM-DD
    annual_limit: float = 50000.0


@router.post("")
async def create_member(member_data: MemberCreate, supabase=Depends(get_supabase_admin)):
    """Create a new member"""
    # Check if member already exists
    existing = supabase.table("members").select("id").eq("id", member_data.id).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Member ID already exists")

    # Parse and validate date
    try:
        policy_start = datetime.strptime(member_data.policy_start_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Create member
    member = {
        "id": member_data.id,
        "name": member_data.name,
        "policy_number": member_data.policy_number,
        "policy_start_date": policy_start.isoformat(),
        "policy_status": "active",
        "annual_limit": member_data.annual_limit,
        "ytd_claims": 0.0
    }

    result = supabase.table("members").insert(member).execute()

    return {
        "member_id": result.data[0]["id"],
        "name": result.data[0]["name"],
        "policy_number": result.data[0]["policy_number"],
        "status": "created"
    }


@router.get("/{member_id}")
async def get_member(member_id: str, supabase=Depends(get_supabase)):
    """Get member details"""
    result = supabase.table("members").select("*").eq("id", member_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Member not found")

    member = result.data[0]
    return {
        "member_id": member["id"],
        "name": member["name"],
        "policy_number": member["policy_number"],
        "policy_start_date": member["policy_start_date"][:10],
        "policy_status": member["policy_status"],
        "annual_limit": member["annual_limit"],
        "ytd_claims": member["ytd_claims"],
        "remaining_limit": float(member["annual_limit"]) - float(member["ytd_claims"])
    }


@router.get("/{member_id}/claims")
async def get_member_claims(member_id: str, supabase=Depends(get_supabase)):
    """Get member's claim history"""
    # Get member
    member_result = supabase.table("members").select("*").eq("id", member_id).execute()
    if not member_result.data:
        raise HTTPException(status_code=404, detail="Member not found")

    member = member_result.data[0]

    # Get claims
    claims_result = supabase.table("claims").select("*").eq("member_id", member_id).order("created_at", desc=True).execute()

    return {
        "member_id": member_id,
        "member_name": member["name"],
        "total_claims": len(claims_result.data),
        "ytd_claims_amount": member["ytd_claims"],
        "claims": [
            {
                "claim_id": c["claim_id"],
                "status": c["status"],
                "claim_amount": c["claim_amount"],
                "approved_amount": c["approved_amount"],
                "decision": c["decision"],
                "submission_date": c["submission_date"],
                "processed_at": c["processed_at"]
            }
            for c in claims_result.data
        ]
    }
