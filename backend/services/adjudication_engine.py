"""
Adjudication Engine - Main decision-making logic for claim approval/rejection

Implements 5-step adjudication workflow:
1. Eligibility Check
2. Document Validation
3. Coverage Verification
4. Limits Check
5. Medical Necessity Review
"""
import logging
from datetime import datetime, timedelta
from typing import Tuple
from models.claim_data import ExtractedData
from models.decision import (
    ClaimDecision, DecisionType, RejectionReason, Deductions,
    AdjudicationSteps, StepResult, MemberInfo
)
from services.policy_service import PolicyService
from services.fraud_detector import FraudDetector

logger = logging.getLogger(__name__)


class AdjudicationEngine:
    """Main engine for claim adjudication"""

    def __init__(self):
        """Initialize adjudication engine"""
        self.policy_service = PolicyService()
        self.fraud_detector = FraudDetector()
        logger.info("Adjudication engine initialized")

    def adjudicate_claim(
        self,
        extracted_data: ExtractedData,
        member_info: MemberInfo
    ) -> ClaimDecision:
        """
        Adjudicate a claim through 5-step workflow

        Args:
            extracted_data: Extracted data from documents
            member_info: Member information

        Returns:
            ClaimDecision with final decision and reasoning
        """
        logger.info(f"Starting adjudication for member: {member_info.member_id}")

        # Initialize decision object
        decision = ClaimDecision(
            claimed_amount=extracted_data.costs.total if extracted_data.costs else 0.0,
            decision=DecisionType.APPROVED  # Start optimistic
        )

        # Run fraud detection first
        fraud_flags = self.fraud_detector.detect_fraud(extracted_data, member_info)
        decision.fraud_flags = fraud_flags

        # If high fraud risk, send for manual review
        fraud_risk = self.fraud_detector.calculate_fraud_risk_score(fraud_flags)
        if fraud_risk >= 0.5:
            decision.decision = DecisionType.MANUAL_REVIEW
            decision.notes = f"Flagged for manual review due to fraud indicators (risk score: {fraud_risk:.2f})"
            return decision

        # Step 1: Eligibility Check
        step1_pass, rejection_reasons = self._check_eligibility(extracted_data, member_info)
        decision.adjudication_steps.eligibility = StepResult.PASS if step1_pass else StepResult.FAIL
        if not step1_pass:
            decision.decision = DecisionType.REJECTED
            decision.rejection_reasons.extend(rejection_reasons)
            return decision

        # Step 2: Document Validation
        step2_pass, rejection_reasons = self._validate_documents(extracted_data)
        decision.adjudication_steps.documents = StepResult.PASS if step2_pass else StepResult.FAIL
        if not step2_pass:
            decision.decision = DecisionType.REJECTED
            decision.rejection_reasons.extend(rejection_reasons)
            return decision

        # Step 3: Coverage Verification
        step3_pass, rejection_reasons, partial_coverage = self._verify_coverage(extracted_data)
        decision.adjudication_steps.coverage = StepResult.PASS if step3_pass else StepResult.FAIL
        if not step3_pass and not partial_coverage:
            decision.decision = DecisionType.REJECTED
            decision.rejection_reasons.extend(rejection_reasons)
            return decision
        elif partial_coverage:
            decision.decision = DecisionType.PARTIAL
            decision.rejection_reasons.extend(rejection_reasons)

        # Step 4: Limits Check
        step4_pass, approved_amount, deductions, rejection_reasons = self._check_limits(
            extracted_data, member_info
        )
        decision.adjudication_steps.limits = StepResult.PASS if step4_pass else StepResult.WARNING
        decision.approved_amount = approved_amount
        decision.deductions = deductions

        if not step4_pass:
            if approved_amount > 0:
                decision.decision = DecisionType.PARTIAL
            else:
                decision.decision = DecisionType.REJECTED
            decision.rejection_reasons.extend(rejection_reasons)

        # Step 5: Medical Necessity Review
        step5_pass, rejection_reasons = self._review_medical_necessity(extracted_data)
        decision.adjudication_steps.medical_necessity = StepResult.PASS if step5_pass else StepResult.FAIL
        if not step5_pass:
            decision.decision = DecisionType.REJECTED
            decision.rejection_reasons.extend(rejection_reasons)
            return decision

        # Check for network hospital benefits
        hospital_name = extracted_data.hospital_name or (
            extracted_data.doctor_info.clinic_name if extracted_data.doctor_info else None
        )
        if hospital_name and self.policy_service.is_network_hospital(hospital_name):
            decision.is_network_hospital = True
            # Apply network discount
            network_discount_pct = self.policy_service.get_network_discount() / 100
            discount = decision.approved_amount * network_discount_pct
            decision.deductions.network_discount = discount
            decision.approved_amount -= discount

            # Check cashless eligibility
            if decision.claimed_amount <= self.policy_service.get_instant_approval_limit():
                decision.cashless_approved = True

        # Calculate confidence score
        decision.confidence_score = self._calculate_decision_confidence(decision, extracted_data)

        # Generate notes and next steps
        decision.notes = self._generate_notes(decision)
        decision.next_steps = self._generate_next_steps(decision)

        logger.info(
            f"Adjudication complete: {decision.decision.value}, "
            f"Approved: ₹{decision.approved_amount:.2f}, "
            f"Confidence: {decision.confidence_score:.2f}"
        )

        return decision

    def _check_eligibility(
        self,
        extracted_data: ExtractedData,
        member_info: MemberInfo
    ) -> Tuple[bool, list]:
        """Step 1: Check member eligibility"""
        rejection_reasons = []

        # Check policy status
        if member_info.policy_status.lower() != 'active':
            rejection_reasons.append(RejectionReason(
                category="eligibility",
                code="POLICY_INACTIVE",
                message="Policy is not active",
                details=f"Policy status: {member_info.policy_status}"
            ))
            return False, rejection_reasons

        # Check waiting period
        if extracted_data.dates and extracted_data.dates.consultation_date:
            try:
                policy_start = datetime.strptime(member_info.policy_start_date, '%Y-%m-%d')
                consultation_date = datetime.strptime(extracted_data.dates.consultation_date, '%Y-%m-%d')
                days_diff = (consultation_date - policy_start).days

                # Check initial waiting period
                initial_waiting = self.policy_service.get_waiting_period('initial')
                if days_diff < initial_waiting:
                    rejection_reasons.append(RejectionReason(
                        category="eligibility",
                        code="WAITING_PERIOD",
                        message=f"Treatment within {initial_waiting}-day initial waiting period",
                        details=f"Policy active for only {days_diff} days"
                    ))
                    return False, rejection_reasons

                # Check specific condition waiting periods
                if extracted_data.diagnosis:
                    diagnosis_lower = extracted_data.diagnosis.lower()
                    if 'diabetes' in diagnosis_lower:
                        diabetes_waiting = self.policy_service.get_waiting_period('diabetes')
                        if days_diff < diabetes_waiting:
                            rejection_reasons.append(RejectionReason(
                                category="eligibility",
                                code="WAITING_PERIOD",
                                message=f"Diabetes has {diabetes_waiting}-day waiting period",
                                details=f"Eligible from {(policy_start + timedelta(days=diabetes_waiting)).strftime('%Y-%m-%d')}"
                            ))
                            return False, rejection_reasons

                    if 'hypertension' in diagnosis_lower or 'blood pressure' in diagnosis_lower:
                        hypertension_waiting = self.policy_service.get_waiting_period('hypertension')
                        if days_diff < hypertension_waiting:
                            rejection_reasons.append(RejectionReason(
                                category="eligibility",
                                code="WAITING_PERIOD",
                                message=f"Hypertension has {hypertension_waiting}-day waiting period",
                                details=f"Eligible from {(policy_start + timedelta(days=hypertension_waiting)).strftime('%Y-%m-%d')}"
                            ))
                            return False, rejection_reasons

            except Exception as e:
                logger.error(f"Date parsing error in eligibility check: {str(e)}")

        return True, []

    def _validate_documents(self, extracted_data: ExtractedData) -> Tuple[bool, list]:
        """Step 2: Validate document completeness and authenticity"""
        rejection_reasons = []

        # Check for prescription
        if not extracted_data.doctor_info or not extracted_data.doctor_info.name:
            rejection_reasons.append(RejectionReason(
                category="documentation",
                code="MISSING_DOCUMENTS",
                message="Prescription from registered doctor is required",
                details="Doctor information not found in documents"
            ))
            return False, rejection_reasons

        # Validate doctor registration
        if extracted_data.doctor_info and extracted_data.doctor_info.registration_number:
            reg_num = extracted_data.doctor_info.registration_number
            # Basic format validation (should have / or -)
            if '/' not in reg_num and '-' not in reg_num:
                rejection_reasons.append(RejectionReason(
                    category="documentation",
                    code="DOCTOR_REG_INVALID",
                    message="Invalid doctor registration number format",
                    details=f"Registration: {reg_num}"
                ))
                return False, rejection_reasons
        else:
            rejection_reasons.append(RejectionReason(
                category="documentation",
                code="DOCTOR_REG_INVALID",
                message="Doctor registration number missing",
                details="Valid registration required for claim processing"
            ))
            return False, rejection_reasons

        # Check for dates
        if not extracted_data.dates or not extracted_data.dates.consultation_date:
            rejection_reasons.append(RejectionReason(
                category="documentation",
                code="DATE_MISMATCH",
                message="Consultation date missing from documents",
                details="Date required for claim processing"
            ))
            return False, rejection_reasons

        return True, []

    def _verify_coverage(self, extracted_data: ExtractedData) -> Tuple[bool, list, bool]:
        """
        Step 3: Verify if services are covered

        Returns:
            (all_covered, rejection_reasons, partial_coverage)
        """
        rejection_reasons = []
        partial_coverage = False

        # Check if diagnosis is excluded
        if extracted_data.diagnosis:
            if self.policy_service.is_excluded(extracted_data.diagnosis):
                rejection_reasons.append(RejectionReason(
                    category="coverage",
                    code="EXCLUDED_CONDITION",
                    message="Condition is excluded from coverage",
                    details=f"Diagnosis: {extracted_data.diagnosis}"
                ))
                return False, rejection_reasons, False

        # Check procedures
        for procedure in extracted_data.procedures:
            proc_name = procedure.name.lower()

            # Check for cosmetic procedures
            if 'cosmetic' in proc_name or 'whitening' in proc_name or 'aesthetic' in proc_name:
                rejection_reasons.append(RejectionReason(
                    category="coverage",
                    code="SERVICE_NOT_COVERED",
                    message=f"Cosmetic procedure not covered: {procedure.name}",
                    details="Cosmetic procedures are excluded"
                ))
                partial_coverage = True

            # Check for weight loss
            if 'weight loss' in proc_name or 'bariatric' in proc_name or 'diet plan' in proc_name:
                rejection_reasons.append(RejectionReason(
                    category="coverage",
                    code="SERVICE_NOT_COVERED",
                    message=f"Weight loss treatment not covered: {procedure.name}",
                    details="Weight loss treatments are excluded"
                ))
                if len(extracted_data.procedures) == 1:
                    return False, rejection_reasons, False
                partial_coverage = True

        # Check for pre-authorization requirements
        for test in extracted_data.diagnostic_tests:
            if self.policy_service.requires_pre_authorization(test):
                rejection_reasons.append(RejectionReason(
                    category="coverage",
                    code="PRE_AUTH_MISSING",
                    message=f"{test} requires pre-authorization",
                    details="Pre-authorization must be obtained before treatment"
                ))
                return False, rejection_reasons, False

        # If we have rejection reasons but not all services were rejected
        if rejection_reasons and partial_coverage:
            return False, rejection_reasons, True

        return True, [], False

    def _check_limits(
        self,
        extracted_data: ExtractedData,
        member_info: MemberInfo
    ) -> Tuple[bool, float, Deductions, list]:
        """
        Step 4: Check against coverage limits

        Returns:
            (within_limits, approved_amount, deductions, rejection_reasons)
        """
        rejection_reasons = []
        deductions = Deductions()

        if not extracted_data.costs:
            return False, 0.0, deductions, [RejectionReason(
                category="limits",
                code="BELOW_MIN_AMOUNT",
                message="No costs found in claim",
                details=""
            )]

        claimed_amount = extracted_data.costs.total

        # Check minimum claim amount
        min_amount = self.policy_service.get_minimum_claim_amount()
        if claimed_amount < min_amount:
            rejection_reasons.append(RejectionReason(
                category="process",
                code="BELOW_MIN_AMOUNT",
                message=f"Claim below minimum amount of ₹{min_amount}",
                details=f"Claimed: ₹{claimed_amount}"
            ))
            return False, 0.0, deductions, rejection_reasons

        # Check per-claim limit
        per_claim_limit = self.policy_service.get_per_claim_limit()
        if claimed_amount > per_claim_limit:
            rejection_reasons.append(RejectionReason(
                category="limits",
                code="PER_CLAIM_EXCEEDED",
                message=f"Claim exceeds per-claim limit of ₹{per_claim_limit}",
                details=f"Claimed: ₹{claimed_amount}"
            ))
            return False, 0.0, deductions, rejection_reasons

        # Check annual limit
        annual_limit = self.policy_service.get_annual_limit()
        ytd_with_current = member_info.ytd_claims + claimed_amount

        if ytd_with_current > annual_limit:
            remaining = annual_limit - member_info.ytd_claims
            if remaining <= 0:
                rejection_reasons.append(RejectionReason(
                    category="limits",
                    code="ANNUAL_LIMIT_EXCEEDED",
                    message=f"Annual limit of ₹{annual_limit} exhausted",
                    details=f"YTD claims: ₹{member_info.ytd_claims}"
                ))
                return False, 0.0, deductions, rejection_reasons
            else:
                # Partial approval up to remaining limit
                deductions.exceeded_limits = claimed_amount - remaining
                claimed_amount = remaining
                rejection_reasons.append(RejectionReason(
                    category="limits",
                    code="ANNUAL_LIMIT_EXCEEDED",
                    message=f"Partial approval: ₹{remaining} remaining in annual limit",
                    details=f"₹{deductions.exceeded_limits} exceeds limit"
                ))

        # Calculate copay
        consultation_copay_pct = self.policy_service.get_consultation_copay() / 100
        if extracted_data.costs.consultation > 0:
            copay = extracted_data.costs.consultation * consultation_copay_pct
            deductions.copay += copay

        pharmacy_copay_pct = self.policy_service.get_pharmacy_copay() / 100
        if extracted_data.costs.medicines > 0:
            # Assume branded drugs for now (in production, would check actual prescriptions)
            copay = extracted_data.costs.medicines * pharmacy_copay_pct
            deductions.copay += copay

        # Calculate approved amount
        approved_amount = claimed_amount - deductions.copay - deductions.non_covered_items - deductions.exceeded_limits

        return True, approved_amount, deductions, rejection_reasons

    def _review_medical_necessity(self, extracted_data: ExtractedData) -> Tuple[bool, list]:
        """Step 5: Review medical necessity"""
        rejection_reasons = []

        # Basic check: diagnosis should justify treatment
        if not extracted_data.diagnosis:
            rejection_reasons.append(RejectionReason(
                category="medical",
                code="NOT_MEDICALLY_NECESSARY",
                message="Diagnosis missing - cannot assess medical necessity",
                details="Clear diagnosis required for claim approval"
            ))
            return False, rejection_reasons

        # Check if medications align with diagnosis (basic heuristics)
        # In production, this would use medical knowledge bases

        return True, []

    def _calculate_decision_confidence(
        self,
        decision: ClaimDecision,
        extracted_data: ExtractedData
    ) -> float:
        """Calculate confidence score for the decision"""
        score = extracted_data.confidence_score  # Start with extraction confidence

        # Adjust based on decision factors
        if decision.decision == DecisionType.REJECTED:
            score = min(score + 0.1, 1.0)  # Higher confidence in rejections
        elif decision.decision == DecisionType.MANUAL_REVIEW:
            score = 0.5  # Medium confidence when sending for review
        elif len(decision.fraud_flags) > 0:
            score *= 0.8  # Lower confidence with fraud flags

        return score

    def _generate_notes(self, decision: ClaimDecision) -> str:
        """Generate human-readable notes for the decision"""
        if decision.decision == DecisionType.APPROVED:
            notes = f"Claim approved for ₹{decision.approved_amount:.2f}"
            if decision.deductions.copay > 0:
                notes += f" (after ₹{decision.deductions.copay:.2f} copay)"
            if decision.is_network_hospital:
                notes += f". Network discount of ₹{decision.deductions.network_discount:.2f} applied"
            return notes

        elif decision.decision == DecisionType.REJECTED:
            return f"Claim rejected. {len(decision.rejection_reasons)} issues found."

        elif decision.decision == DecisionType.PARTIAL:
            return f"Partial approval: ₹{decision.approved_amount:.2f} of ₹{decision.claimed_amount:.2f}"

        elif decision.decision == DecisionType.MANUAL_REVIEW:
            return "Claim flagged for manual review due to unusual patterns"

        return ""

    def _generate_next_steps(self, decision: ClaimDecision) -> str:
        """Generate next steps for the claimant"""
        if decision.decision == DecisionType.APPROVED:
            if decision.cashless_approved:
                return "Cashless approval granted. No payment required from you."
            return "Approved amount will be reimbursed to your account within 5-7 business days."

        elif decision.decision == DecisionType.REJECTED:
            return "Please review rejection reasons. You may appeal this decision with additional documentation."

        elif decision.decision == DecisionType.PARTIAL:
            return "Partial amount approved. You may appeal for the rejected portion with additional justification."

        elif decision.decision == DecisionType.MANUAL_REVIEW:
            return "Our claims team will review your claim within 2-3 business days. You may be contacted for additional information."

        return ""
