"""
Custom exceptions for the loan workflow.

This file was empty in the original project (0 bytes) even though the
orchestrator needs a way to signal "this stage failed" distinctly from a
plain Python exception. Kept intentionally small — just enough for the
orchestrator to raise/catch meaningful errors per stage.
"""


class WorkflowStageError(Exception):
    """Raised when a specific pipeline stage fails."""

    def __init__(self, stage: str, message: str):
        self.stage = stage
        self.message = message
        super().__init__(f"[{stage}] {message}")


class CustomerNotFoundError(WorkflowStageError):
    def __init__(self, customer_id: str):
        super().__init__("checker", f"Customer '{customer_id}' not found and could not be created.")


class LoanRejectedError(WorkflowStageError):
    def __init__(self, reason: str):
        super().__init__("underwriting", f"Loan rejected: {reason}")


class VerificationFailedError(WorkflowStageError):
    def __init__(self, reason: str):
        super().__init__("verification", f"KYC verification failed: {reason}")