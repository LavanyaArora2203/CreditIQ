from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Decision(BaseModel):
    approved: bool

    approved_amount: float = Field(gt=0)
    approved_tenure_months: int = Field(gt=0)

    final_interest_rate: float = Field(gt=0)
    final_emi: float = Field(gt=0)

    risk_grade: str

    debt_to_income_ratio: float = Field(
        ge=0,
        le=1,
        description="Debt-to-Income ratio (0-1)"
    )


class AdjustmentsFromRequest(BaseModel):
    amount_changed: bool
    original_amount: float = Field(gt=0)
    reason: str


class ManualReviewFlag(BaseModel):
    required: bool
    reason: Optional[str] = None


class UnderwritingOutput(BaseModel):
    task_id: str

    agent: Literal["underwriting_agent"]

    status: Literal[
        "success",
        "rejected",
        "pending_documents",
        "manual_review_required",
        "failed"
    ]

    decision: Optional[Decision] = None

    adjustments_from_request: Optional[AdjustmentsFromRequest] = None

    conditions: List[str] = Field(default_factory=list)

    rejection_reason: Optional[str] = None

    manual_review_flag: ManualReviewFlag

    reasoning: str

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score between 0 and 1"
    )

    errors: List[str] = Field(default_factory=list)