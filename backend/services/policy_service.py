"""
Policy Service - Loads and provides access to policy terms and rules
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PolicyService:
    """Service for loading and querying policy terms"""

    def __init__(self):
        """Initialize policy service and load policy terms"""
        self.policy_terms = self._load_policy_terms()
        logger.info("Policy service initialized")

    def _load_policy_terms(self) -> Dict[str, Any]:
        """Load policy terms from JSON file"""
        try:
            policy_path = Path(__file__).parent.parent / settings.POLICY_FILE_PATH
            with open(policy_path, 'r') as f:
                policy = json.load(f)
            logger.info(f"Loaded policy: {policy.get('policy_name')}")
            return policy
        except Exception as e:
            logger.error(f"Failed to load policy terms: {str(e)}")
            raise

    def get_annual_limit(self) -> float:
        """Get annual coverage limit"""
        return self.policy_terms.get('coverage_details', {}).get('annual_limit', 0)

    def get_per_claim_limit(self) -> float:
        """Get per-claim limit"""
        return self.policy_terms.get('coverage_details', {}).get('per_claim_limit', 0)

    def get_consultation_limit(self) -> float:
        """Get consultation fee sub-limit"""
        return self.policy_terms.get('coverage_details', {}).get('consultation_fees', {}).get('sub_limit', 0)

    def get_consultation_copay(self) -> float:
        """Get consultation copay percentage"""
        return self.policy_terms.get('coverage_details', {}).get('consultation_fees', {}).get('copay_percentage', 0)

    def get_diagnostic_limit(self) -> float:
        """Get diagnostic tests sub-limit"""
        return self.policy_terms.get('coverage_details', {}).get('diagnostic_tests', {}).get('sub_limit', 0)

    def get_pharmacy_limit(self) -> float:
        """Get pharmacy sub-limit"""
        return self.policy_terms.get('coverage_details', {}).get('pharmacy', {}).get('sub_limit', 0)

    def get_pharmacy_copay(self) -> float:
        """Get pharmacy copay for branded drugs"""
        return self.policy_terms.get('coverage_details', {}).get('pharmacy', {}).get('branded_drugs_copay', 0)

    def get_dental_limit(self) -> float:
        """Get dental treatment sub-limit"""
        return self.policy_terms.get('coverage_details', {}).get('dental', {}).get('sub_limit', 0)

    def get_vision_limit(self) -> float:
        """Get vision care sub-limit"""
        return self.policy_terms.get('coverage_details', {}).get('vision', {}).get('sub_limit', 0)

    def get_alternative_medicine_limit(self) -> float:
        """Get alternative medicine sub-limit"""
        return self.policy_terms.get('coverage_details', {}).get('alternative_medicine', {}).get('sub_limit', 0)

    def get_network_discount(self) -> float:
        """Get network provider discount percentage"""
        return self.policy_terms.get('coverage_details', {}).get('consultation_fees', {}).get('network_discount', 0)

    def get_waiting_period(self, condition_type: str = 'initial') -> int:
        """
        Get waiting period in days

        Args:
            condition_type: Type of condition (initial, pre_existing_diseases, specific ailment name)

        Returns:
            Waiting period in days
        """
        waiting_periods = self.policy_terms.get('waiting_periods', {})

        if condition_type == 'initial':
            return waiting_periods.get('initial_waiting', 30)
        elif condition_type == 'pre_existing':
            return waiting_periods.get('pre_existing_diseases', 365)
        else:
            # Check specific ailments
            specific = waiting_periods.get('specific_ailments', {})
            return specific.get(condition_type.lower(), 0)

    def is_excluded(self, service_or_condition: str) -> bool:
        """
        Check if a service or condition is excluded

        Args:
            service_or_condition: Service or condition name

        Returns:
            True if excluded, False otherwise
        """
        exclusions = self.policy_terms.get('exclusions', [])
        service_lower = service_or_condition.lower()

        for exclusion in exclusions:
            if exclusion.lower() in service_lower or service_lower in exclusion.lower():
                return True

        return False

    def is_network_hospital(self, hospital_name: str) -> bool:
        """
        Check if hospital is in network

        Args:
            hospital_name: Hospital name

        Returns:
            True if in network, False otherwise
        """
        network_hospitals = self.policy_terms.get('network_hospitals', [])
        hospital_lower = hospital_name.lower() if hospital_name else ""

        for network_hosp in network_hospitals:
            if network_hosp.lower() in hospital_lower or hospital_lower in network_hosp.lower():
                return True

        return False

    def get_minimum_claim_amount(self) -> float:
        """Get minimum claim amount"""
        return self.policy_terms.get('claim_requirements', {}).get('minimum_claim_amount', 500)

    def get_submission_timeline_days(self) -> int:
        """Get submission timeline in days"""
        return self.policy_terms.get('claim_requirements', {}).get('submission_timeline_days', 30)

    def requires_pre_authorization(self, service: str) -> bool:
        """
        Check if service requires pre-authorization

        Args:
            service: Service name

        Returns:
            True if pre-auth required, False otherwise
        """
        # Check diagnostic tests
        diag_tests = self.policy_terms.get('coverage_details', {}).get('diagnostic_tests', {})
        covered_tests = diag_tests.get('covered_tests', [])

        for test in covered_tests:
            if 'pre-auth' in test.lower() and service.lower() in test.lower():
                return True

        return False

    def get_covered_procedures(self, category: str) -> list:
        """
        Get list of covered procedures for a category

        Args:
            category: Category name (dental, vision, etc.)

        Returns:
            List of covered procedures
        """
        category_data = self.policy_terms.get('coverage_details', {}).get(category, {})
        return category_data.get('procedures_covered', [])

    def is_procedure_covered(self, procedure: str, category: str = None) -> bool:
        """
        Check if a procedure is covered

        Args:
            procedure: Procedure name
            category: Optional category to narrow search

        Returns:
            True if covered, False otherwise
        """
        if category:
            covered = self.get_covered_procedures(category)
            procedure_lower = procedure.lower()
            for cov in covered:
                if cov.lower() in procedure_lower or procedure_lower in cov.lower():
                    return True
            return False

        # Check all categories
        coverage = self.policy_terms.get('coverage_details', {})
        for cat_name, cat_data in coverage.items():
            if isinstance(cat_data, dict) and 'procedures_covered' in cat_data:
                for proc in cat_data['procedures_covered']:
                    if proc.lower() in procedure.lower() or procedure.lower() in proc.lower():
                        return True

        return False

    def get_instant_approval_limit(self) -> float:
        """Get instant approval limit for cashless claims"""
        return self.policy_terms.get('cashless_facilities', {}).get('instant_approval_limit', 5000)
