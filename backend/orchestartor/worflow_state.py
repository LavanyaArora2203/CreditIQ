"""
Pydantic profile models describing a fully-hydrated loan workflow state.

FIX: the original file mixed these model definitions with a `StageExecutor`
class that referenced names that don't exist anywhere in the codebase
(`checker_agent`, `sales_crew`, `underwriting_crew`, `verification_crew`,
`sanction_crew`, `executor`, `WORKFLOW`, `sales_to_underwriting` — none of
these were imported or defined in that file) and used `state`/`stage`
variables before they were ever assigned. It could not have run — it's
dead/broken scratch code, so it has been removed rather than "fixed" by
guessing what it was supposed to do.

The actual working pipeline logic now lives in orchestrator.py, which
calls the loan_agents run() functions directly instead of routing through
this class. These pydantic models are kept because they're a clean,
reusable definition of "everything a fully wired-up system would need to
track" — useful once you build a real backend/frontend around this and
want typed state instead of loose dicts.
"""

from typing import Optional, List
from pydantic import BaseModel, Field

from models.input.sales_input import SalesAgentRequest
from models.output.sales_output import SalesOutput
from models.output.underwriting_output import UnderwritingOutput
from models.output.verification_output import VerificationOutput
from models.output.sanction_output import SanctionLetterOutput

from orchestartor.workflow_status import WorkflowStage


class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    address: str
    dob: str
    pan_number: str
    aadhaar_number: str


class FinancialProfile(BaseModel):
    monthly_income: float
    existing_emis: float
    employment_type: str
    employment_tenure_months: int
    avg_bank_balance: float


class CreditProfile(BaseModel):
    credit_score: int
    risk_category: str


class ExistingLoanState(BaseModel):
    loan_type: str
    outstanding_amount: float
    emi: float


class DocumentProfile(BaseModel):
    kyc_verified: bool
    income_verified: bool
    address_verified: bool
    kyc_document_ids: List[str] = Field(default_factory=list)
    income_document_ids: List[str] = Field(default_factory=list)
    address_document_ids: List[str] = Field(default_factory=list)


class CompanyProfile(BaseModel):
    name: str
    address: str
    email: str
    phone: str


class LoanProfile(BaseModel):
    loan_type: str
    requested_amount: float
    requested_tenure: int
    proposed_interest_rate: float
    proposed_emi: float
    processing_fee: float
    disbursement_amount: float
    repayment_start_date: str


class SessionProfile(BaseModel):
    conversation_id: str
    auth_token: str


class WorkflowState(BaseModel):
    ########################################
    # Initial Request
    ########################################
    sales_request: Optional[SalesAgentRequest] = None

    ########################################
    # Master Data
    ########################################
    customer: Optional[CustomerProfile] = None
    financial: Optional[FinancialProfile] = None
    credit: Optional[CreditProfile] = None
    documents: Optional[DocumentProfile] = None
    company: Optional[CompanyProfile] = None
    loan: Optional[LoanProfile] = None
    session: Optional[SessionProfile] = None
    existing_loans: List[ExistingLoanState] = Field(default_factory=list)

    ########################################
    # Agent Outputs
    ########################################
    current_stage: WorkflowStage = WorkflowStage.CHECKER
    workflow_finished: bool = False
    workflow_failed: bool = False

    sales_output: Optional[SalesOutput] = None
    underwriting_output: Optional[UnderwritingOutput] = None
    verification_output: Optional[VerificationOutput] = None
    sanction_output: Optional[SanctionLetterOutput] = None