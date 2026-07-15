from typing import List, Literal
from pydantic import BaseModel, Field


class RequestContext(BaseModel):
    intent: Literal["loan_underwriting"]

    loan_type: Literal[
        "personal_loan",
        "home_loan",
        "auto_loan",
        "business_loan"
    ]

    requested_amount: float = Field(gt=0)
    requested_tenure_months: int = Field(gt=0)
    proposed_interest_rate: float = Field(gt=0)
    proposed_emi: float = Field(gt=0)

    source_agent: Literal["sales_agent"]
    source_task_id: str


class ExistingLoan(BaseModel):
    loan_type: Literal[
        "personal_loan",
        "home_loan",
        "auto_loan",
        "business_loan"
    ]

    outstanding_amount: float = Field(gt=0)
    emi: float = Field(gt=0)


class CustomerFinancials(BaseModel):
    credit_score: int = Field(ge=300, le=900)

    monthly_income: float = Field(gt=0)

    existing_emis: float = Field(ge=0)

    employment_type: Literal[
        "salaried",
        "self_employed"
    ]

    employment_tenure_months: int = Field(ge=0)

    existing_loans: List[ExistingLoan] = Field(default_factory=list)

    bank_statement_avg_balance: float = Field(ge=0)


class Documents(BaseModel):
    kyc_verified: bool
    income_proof_verified: bool
    document_ids: List[str] = Field(default_factory=list)


class SessionContext(BaseModel):
    conversation_id: str


class UnderwritingInput(BaseModel):
    task_id: str
    agent: Literal["underwriting_agent"]

    customer_id: str

    request_context: RequestContext

    customer_financials: CustomerFinancials

    documents: Documents

    session_context: SessionContext

    auth_token: str