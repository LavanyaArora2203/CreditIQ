from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class VerificationCheck(BaseModel):
    verified: bool
    method: str
    confidence: float = Field(ge=0, le=1)
    mismatches: List[str] = Field(default_factory=list)


class AMLScreening(BaseModel):
    passed: bool
    sanctions_list_hit: bool


class VerificationChecks(BaseModel):
    kyc: VerificationCheck
    income_proof: VerificationCheck
    address_proof: VerificationCheck
    aml_screening: AMLScreening


class VerificationResult(BaseModel):
    overall_verified: bool
    verified_at: str
    checks: VerificationChecks


class ManualReviewFlag(BaseModel):
    required: bool
    reason: Optional[str] = None


class VerificationOutput(BaseModel):
    task_id: str

    agent: Literal["verification_agent"]

    status: Literal[
        "verification_complete",
        "verification_failed",
        "partial",
        "manual_review_required",
        "failed"
    ]

    verification_result: Optional[VerificationResult] = None

    risk_flags: List[str] = Field(default_factory=list)

    manual_review_flag: ManualReviewFlag

    reasoning: str

    confidence: float = Field(
        ge=0,
        le=1,
        description="Overall confidence score"
    )

    errors: List[str] = Field(default_factory=list)