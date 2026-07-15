from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AdditionalPreferences(BaseModel):
    max_emi: Optional[float] = Field(
        default=None,
        description="Maximum EMI customer is willing to pay"
    )

    interest_type: Literal[
        "fixed",
        "floating",
        "no_preference"
    ] = "no_preference"


class RequestContext(BaseModel):
    intent: Literal["loan_recommendation"]

    preferred_loan_type: Literal[
        "personal_loan",
        "home_loan",
        "auto_loan",
        "business_loan"
    ]

    preferred_amount: float = Field(gt=0)

    preferred_tenure_months: int = Field(
        gt=0,
        description="Loan tenure in months"
    )

    additional_preferences: AdditionalPreferences


class SessionContext(BaseModel):
    conversation_id: str
    previous_turns: List[dict] = Field(default_factory=list)


class SalesAgentRequest(BaseModel):
    task_id: str
    agent: Literal["sales_agent"]

    customer_id: str

    request_context: RequestContext

    session_context: SessionContext

    auth_token: str



# from models.sales_input import SalesInput

# def run(request: SalesInput):
#     customer_id = request.customer_id
#     loan_type = request.request_context.preferred_loan_type
#     amount = request.request_context.preferred_amount
#     tenure = request.request_context.preferred_tenure_months
#     max_emi = request.request_context.additional_preferences.max_emi

#     # Business logic here...
