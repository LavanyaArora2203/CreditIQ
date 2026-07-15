"""
Maps outputs from one pipeline stage into the input the next stage needs.

FIX: the original mapper.py assumed every agent consumed/produced the full,
deeply-nested pydantic models in models/input and models/output (e.g. it
tried to build a complete UnderwritingInput from a WorkflowState object
with fields like state.credit_profile, state.financial_profile,
state.documents, state.company etc. that nothing in the codebase ever
populates — there's no code anywhere that fetches a customer's income,
employment type, bank balance, or company session token). It also had
broken imports: `from models.underwriting_input import (...)` and
`from models.verification_input import (...)` pointed at
`models/underwriting_input.py`, but that file actually lives at
`models/input/underwriting_input.py`.

As actually implemented, the loan_agents (see loan_agents/*.py) take
simple scalar inputs (customer_id, loan_amount, tenure, interest_rate) via
CrewAI's kickoff(inputs=...) templating, NOT the full nested pydantic
objects — only the sanction letter step genuinely needs an assembled
structured object. So this file now does the one real mapping step the
pipeline needs: turning an approved UnderwritingDecision + a
KYCVerificationResult + the customer's on-file data into the
`approved_data` dict the sanction_letter_agent expects.

The full pydantic input models in models/input/ are untouched and still
usable if/when you wire this up to richer data sources (e.g. a real credit
bureau, a real CRM) later.
"""

from orchestartor.utils import find_customer, repayment_start_date

# Static company info sourced from data/bank_info.txt (ABC Finance Ltd is
# the fictional NBFC used throughout the project's sample data).
DEFAULT_COMPANY = {
    "name": "ABC Finance Ltd.",
    "address": "Connaught Place, New Delhi - 110001",
    "email": "support@abcfinance.com",
    "phone": "1800-000-000",
}


def build_sanction_input(
    customer_id: str,
    underwriting_decision: dict,
    verification_result: dict,
) -> dict:
    """
    underwriting_decision: dict matching loan_agents.underwriting_agent.UnderwritingDecision
    verification_result:   dict matching loan_agents.verification_agent.KYCVerificationResult
    """
    customer = find_customer(customer_id) or {}

    return {
        "company": DEFAULT_COMPANY,
        "customer": {
            "customer_id": customer_id,
            "name": customer.get("name", "Unknown"),
            "address": customer.get("city", "Not Available"),
            "phone": customer.get("phone", "Not Available"),
            "email": customer.get("email", "Not Available"),
        },
        "loan": {
            "loan_type": "Personal Loan",
            "approved_amount": underwriting_decision.get("approved_amount"),
            "interest_rate": underwriting_decision.get("interest_rate"),
            "tenure_months": underwriting_decision.get("tenure"),
            "emi": underwriting_decision.get("monthly_emi"),
            "processing_fee": round(underwriting_decision.get("approved_amount", 0) * 0.01, 2),
            "disbursement_amount": underwriting_decision.get("approved_amount"),
            "repayment_start_date": repayment_start_date(),
        },
        "credit_summary": {
            "credit_score": underwriting_decision.get("credit_score"),
            "risk_category": "Low" if underwriting_decision.get("credit_score", 0) >= 750 else "Medium",
        },
        "approval_summary": {
            "status": "Approved",
            "reason": underwriting_decision.get("reason", ""),
        },
        "verification_summary": {
            "kyc_status": verification_result.get("kyc_status"),
            "reason": verification_result.get("reason"),
        },
    }