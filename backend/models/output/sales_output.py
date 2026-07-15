from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AlternativeRecommendation(BaseModel):
    amount: float = Field(gt=0)
    tenure_months: int = Field(gt=0)
    interest_rate: float = Field(gt=0)
    emi: float = Field(gt=0)


class Recommendation(BaseModel):
    customer_id: str

    loan_type: Literal[
        "personal_loan",
        "home_loan",
        "auto_loan",
        "business_loan"
    ]

    recommended_amount: float = Field(gt=0)
    recommended_tenure_months: int = Field(gt=0)
    interest_rate: float = Field(gt=0)
    emi: float = Field(gt=0)

    eligibility_score: float = Field(
        ge=0,
        le=1,
        description="Eligibility score between 0 and 1"
    )

    alternatives: List[AlternativeRecommendation] = Field(default_factory=list)


class SalesOutput(BaseModel):
    task_id: str

    agent: Literal["sales_agent"]

    status: Literal[
        "success",
        "partial",
        "failed",
        "needs_clarification"
    ]

    recommendation: Optional[Recommendation] = None

    reasoning: str

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score between 0 and 1"
    )

    requires_followup: bool = False

    followup_question: Optional[str] = None

    errors: List[str] = Field(default_factory=list)