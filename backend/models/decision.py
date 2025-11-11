"""
Decision models for claim adjudication
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class DecisionType(str, Enum):
    """Types of adjudication decisions"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PARTIAL = "PARTIAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    NOT_A_MEMBER = "NOT_A_MEMBER"  


class StepResult(str, Enum):
    """Result of each adjudication step"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class RejectionReason(BaseModel):
    """Structured rejection reason"""
    category: str = Field(..., description="Category: eligibility, documentation, coverage, limits, medical, process")
    code: str = Field(..., description="Reason code (e.g., POLICY_INACTIVE)")
    message: str = Field(..., description="Human-readable message")
    details: Optional[str] = Field(None, description="Additional details")


class Deductions(BaseModel):
    """Breakdown of deductions"""
    copay: float = Field(0.0, description="Co-payment amount")
    non_covered_items: float = Field(0.0, description="Items not covered by policy")
    exceeded_limits: float = Field(0.0, description="Amount exceeding limits")
    network_discount: float = Field(0.0, description="Network provider discount")


class AdjudicationSteps(BaseModel):
    """Results of each adjudication step"""
    eligibility: StepResult = StepResult.SKIPPED
    documents: StepResult = StepResult.SKIPPED
    coverage: StepResult = StepResult.SKIPPED
    limits: StepResult = StepResult.SKIPPED
    medical_necessity: StepResult = StepResult.SKIPPED


class ClaimDecision(BaseModel):
    """Final claim adjudication decision"""

    # Decision
    decision: DecisionType = Field(..., description="Final decision")
    approved_amount: float = Field(0.0, description="Amount approved for payment")
    claimed_amount: float = Field(..., description="Total amount claimed")

    # Deductions
    deductions: Deductions = Field(default_factory=Deductions)

    # Reasons and explanations
    rejection_reasons: List[RejectionReason] = Field(default_factory=list)
    notes: str = Field("", description="Additional notes for the decision")
    next_steps: str = Field("", description="What the claimant should do")

    # Scoring and flags
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in decision")
    fraud_flags: List[str] = Field(default_factory=list)

    # Process details
    adjudication_steps: AdjudicationSteps = Field(default_factory=AdjudicationSteps)
    processing_notes: Dict[str, str] = Field(default_factory=dict)

    # Cashless/Network info
    cashless_approved: bool = Field(False, description="Whether cashless is approved")
    is_network_hospital: bool = Field(False, description="Whether hospital is in network")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "APPROVED",
                "approved_amount": 1350.0,
                "claimed_amount": 1500.0,
                "deductions": {
                    "copay": 150.0,
                    "non_covered_items": 0.0,
                    "exceeded_limits": 0.0
                },
                "rejection_reasons": [],
                "notes": "Claim approved with 10% copay",
                "confidence_score": 0.95,
                "adjudication_steps": {
                    "eligibility": "PASS",
                    "documents": "PASS",
                    "coverage": "PASS",
                    "limits": "PASS",
                    "medical_necessity": "PASS"
                }
            }
        }


class MemberInfo(BaseModel):
    """Member information for adjudication"""
    member_id: str = Field(..., description="Member ID")
    member_name: str = Field(..., description="Member name")
    policy_start_date: str = Field(..., description="Policy start date (YYYY-MM-DD)")
    policy_status: str = Field("active", description="Policy status")
    ytd_claims: float = Field(0.0, description="Year-to-date claims amount")
    previous_claims: List[Dict] = Field(default_factory=list, description="Previous claim history")
