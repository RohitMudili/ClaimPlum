"""
Fraud Detection Service
Identifies suspicious patterns in claims
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from models.claim_data import ExtractedData
from models.decision import MemberInfo

logger = logging.getLogger(__name__)


class FraudDetector:
    """Service for detecting potential fraud in claims"""

    def __init__(self):
        """Initialize fraud detector"""
        logger.info("Fraud detector initialized")

    def detect_fraud(
        self,
        extracted_data: ExtractedData,
        member_info: MemberInfo
    ) -> List[str]:
        """
        Detect potential fraud indicators

        Args:
            extracted_data: Extracted claim data
            member_info: Member information

        Returns:
            List of fraud flags
        """
        fraud_flags = []

        # Check for multiple claims same day
        flags = self._check_multiple_claims_same_day(extracted_data, member_info)
        fraud_flags.extend(flags)

        # Check for unusual claim frequency
        flags = self._check_claim_frequency(member_info)
        fraud_flags.extend(flags)

        # Check for suspicious amounts
        flags = self._check_suspicious_amounts(extracted_data)
        fraud_flags.extend(flags)

        # Check for diagnosis-age mismatch
        flags = self._check_diagnosis_appropriateness(extracted_data)
        fraud_flags.extend(flags)

        # Check for document inconsistencies
        flags = self._check_document_consistency(extracted_data)
        fraud_flags.extend(flags)

        if fraud_flags:
            logger.warning(f"Fraud flags detected for {member_info.member_id}: {fraud_flags}")

        return fraud_flags

    def _check_multiple_claims_same_day(
        self,
        extracted_data: ExtractedData,
        member_info: MemberInfo
    ) -> List[str]:
        """Check for multiple claims on same day"""
        flags = []

        claim_date = extracted_data.dates.consultation_date if extracted_data.dates else None
        if not claim_date:
            return flags

        # Check previous claims
        same_day_claims = 0
        for prev_claim in member_info.previous_claims:
            if prev_claim.get('date') == claim_date:
                same_day_claims += 1

        if same_day_claims >= 2:
            flags.append(f"Multiple claims on same day ({same_day_claims + 1} total)")

        return flags

    def _check_claim_frequency(self, member_info: MemberInfo) -> List[str]:
        """Check for unusually high claim frequency"""
        flags = []

        # Count claims in last 30 days
        recent_claims = len(member_info.previous_claims)

        if recent_claims >= 10:
            flags.append(f"High claim frequency: {recent_claims} claims in recent period")
        elif recent_claims >= 5:
            flags.append(f"Elevated claim frequency: {recent_claims} claims in recent period")

        return flags

    def _check_suspicious_amounts(self, extracted_data: ExtractedData) -> List[str]:
        """Check for suspicious claim amounts"""
        flags = []

        if not extracted_data.costs:
            return flags

        total = extracted_data.costs.total

        # Check for round numbers (potential manipulation)
        if total > 1000 and total % 1000 == 0:
            flags.append(f"Suspiciously round claim amount: ₹{total}")

        # Check for amounts just under limits
        if 4800 <= total <= 5000:
            flags.append("Claim amount suspiciously close to per-claim limit")

        return flags

    def _check_diagnosis_appropriateness(self, extracted_data: ExtractedData) -> List[str]:
        """Check if diagnosis seems appropriate"""
        flags = []

        diagnosis = extracted_data.diagnosis
        if not diagnosis:
            return flags

        diagnosis_lower = diagnosis.lower()

        # Check for vague or suspicious diagnoses
        suspicious_terms = ['general', 'unspecified', 'unknown', 'other']
        for term in suspicious_terms:
            if term in diagnosis_lower:
                flags.append(f"Vague diagnosis: {diagnosis}")
                break

        return flags

    def _check_document_consistency(self, extracted_data: ExtractedData) -> List[str]:
        """Check for inconsistencies in documents"""
        flags = []

        # Check date consistency
        if extracted_data.dates:
            dates = []
            if extracted_data.dates.consultation_date:
                dates.append(extracted_data.dates.consultation_date)
            if extracted_data.dates.prescription_date:
                dates.append(extracted_data.dates.prescription_date)
            if extracted_data.dates.bill_date:
                dates.append(extracted_data.dates.bill_date)

            # Check if dates are too far apart
            if len(dates) >= 2:
                try:
                    date_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates if d]
                    if len(date_objs) >= 2:
                        date_diff = max(date_objs) - min(date_objs)
                        if date_diff.days > 7:
                            flags.append(f"Document dates span {date_diff.days} days (suspicious)")
                except:
                    pass

        # Check if costs don't add up
        if extracted_data.costs:
            costs = extracted_data.costs
            calculated_total = (
                costs.consultation +
                costs.medicines +
                costs.diagnostic_tests +
                costs.procedures +
                costs.other
            )

            if calculated_total > 0 and costs.total > 0:
                diff = abs(costs.total - calculated_total)
                if diff > costs.total * 0.2:  # More than 20% difference
                    flags.append(f"Cost breakdown doesn't match total (₹{diff:.2f} discrepancy)")

        # Check for missing critical information
        if not extracted_data.doctor_info or not extracted_data.doctor_info.registration_number:
            flags.append("Missing doctor registration number")

        return flags

    def calculate_fraud_risk_score(self, fraud_flags: List[str]) -> float:
        """
        Calculate overall fraud risk score

        Args:
            fraud_flags: List of fraud flags

        Returns:
            Risk score between 0 (no risk) and 1 (high risk)
        """
        if not fraud_flags:
            return 0.0

        # Weight different types of flags
        risk_score = 0.0

        for flag in fraud_flags:
            flag_lower = flag.lower()

            if 'multiple claims' in flag_lower:
                risk_score += 0.3
            elif 'high frequency' in flag_lower or 'elevated frequency' in flag_lower:
                risk_score += 0.25
            elif 'round amount' in flag_lower or 'close to limit' in flag_lower:
                risk_score += 0.15
            elif 'vague diagnosis' in flag_lower:
                risk_score += 0.1
            elif 'inconsistent' in flag_lower or 'discrepancy' in flag_lower:
                risk_score += 0.2
            elif 'missing' in flag_lower:
                risk_score += 0.15
            else:
                risk_score += 0.1

        return min(risk_score, 1.0)
