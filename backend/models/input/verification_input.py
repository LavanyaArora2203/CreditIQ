from typing import List, Literal
from pydantic import BaseModel, Field


class TriggerEvent(BaseModel):
    event_type: Literal["loan_approved"]
    source_agent: Literal["underwriting_agent"]
    source_task_id: str


class LoanContext(BaseModel):
    loan_type: Literal[
        "personal_loan",
        "home_loan",
        "auto_loan",
        "business_loan"
    ]

    approved_amount: float = Field(gt=0)
    approved_tenure_months: int = Field(gt=0)


class DocumentCategory(BaseModel):
    document_ids: List[str] = Field(default_factory=list)
    document_types: List[str] = Field(default_factory=list)


class DocumentsToVerify(BaseModel):
    kyc: DocumentCategory
    income_proof: DocumentCategory
    address_proof: DocumentCategory


class CustomerSubmittedData(BaseModel):
    name: str
    dob: str
    pan_number: str
    aadhaar_number: str
    address: str


class VerificationRequirements(BaseModel):
    aml_check_required: bool
    sanctions_screening_required: bool

    min_confidence_threshold: float = Field(
        ge=0,
        le=1
    )


class SessionContext(BaseModel):
    conversation_id: str


class VerificationInput(BaseModel):
    task_id: str

    agent: Literal["verification_agent"]

    customer_id: str

    trigger_event: TriggerEvent

    loan_context: LoanContext

    documents_to_verify: DocumentsToVerify

    customer_submitted_data: CustomerSubmittedData

    verification_requirements: VerificationRequirements

    session_context: SessionContext

    auth_token: str