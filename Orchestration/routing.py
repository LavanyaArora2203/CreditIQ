"""
routing.py

Contains workflow routing rules.
"""

from Orchestration.state_machine import WorkflowState


class WorkflowRouter:

    @staticmethod
    def after_sales():
        """
        Sales is always followed by Verification.
        """
        return WorkflowState.VERIFICATION

    @staticmethod
    def after_verification(verification_result):
        """
        Decide next step after verification.
        """

        if verification_result is None:
            return WorkflowState.FAILED

        status = verification_result.get("status", "").upper()

        if status == "VERIFIED":
            return WorkflowState.UNDERWRITING

        return WorkflowState.FAILED

    @staticmethod
    def after_underwriting(underwriting_result):
        """
        Decide next step after underwriting.
        """

        if underwriting_result is None:
            return WorkflowState.FAILED

        decision = underwriting_result.get(
            "decision",
            ""
        ).upper()

        if decision == "APPROVED":
            return WorkflowState.SANCTION

        return WorkflowState.COMPLETED

    @staticmethod
    def after_sanction():
        """
        Workflow ends after sanction letter generation.
        """
        return WorkflowState.COMPLETED