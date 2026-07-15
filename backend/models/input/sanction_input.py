from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class TriggerEvent(BaseModel):
    event_type: Literal["verification_complete"]
    source_agent: Literal["verification_agent"]
    source_task_id: str


class Company(BaseModel):
    name: str
    address: str
    email: EmailStr
    phone: str


class Customer(BaseModel):
    customer_id: str
    name: str
    address: str
    phone: str
    email: EmailStr


class Loan(BaseModel):
    loan_type: str

    approved_amount: float = Field(gt=0)
    interest_rate: float = Field(gt=0)
    tenure_months: int = Field(gt=0)
    emi: float = Field(gt=0)

    processing_fee: float = Field(ge=0)
    disbursement_amount: float = Field(gt=0)

    repayment_start_date: str


class CreditSummary(BaseModel):
    credit_score: int = Field(ge=300, le=900)
    risk_category: str


class ApprovalSummary(BaseModel):
    status: Literal[
        "Approved",
        "Rejected",
        "Conditionally Approved"
    ]
    reason: str


class VerificationSummary(BaseModel):
    kyc_verified: bool

    verification_confidence: float = Field(
        ge=0,
        le=1
    )


class SessionContext(BaseModel):
    conversation_id: str


class SanctionLetterInput(BaseModel):
    task_id: str

    agent: Literal["sanction_letter_agent"]

    trigger_event: TriggerEvent

    company: Company

    customer: Customer

    loan: Loan

    credit_summary: CreditSummary

    approval_summary: ApprovalSummary

    verification_summary: VerificationSummary

    session_context: SessionContext