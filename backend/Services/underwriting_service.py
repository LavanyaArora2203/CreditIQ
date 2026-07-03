import requests

from Services.salary_service import evaluate_salary
from Utils.agent_logger import log_agent

CREDIT_API = "http://127.0.0.1:8000/credit"


def evaluate_loan(
    customer_id: str,
    loan_amount: float,
    annual_interest_rate: float = 10,
    tenure_months: int = 60,
):

    response = requests.get(f"{CREDIT_API}/{customer_id}")

    if response.status_code != 200:
        log_agent(
            "UnderwritingAgent",
            "Loan Evaluation",
            "FAILED",
            f"{customer_id} not found"
        )
        return {
            "status": "error",
            "message": "Customer not found"
        }

    customer = response.json()

    credit_score = customer["credit_score"]
    salary = customer["monthly_salary"]
    limit = customer["preapproved_limit"]

    # --------------------------------------------------
    # Rule 0 : Minimum Credit Score
    # --------------------------------------------------

    if credit_score < 700:
        log_agent(
            "UnderwritingAgent",
            "Credit Check",
            "REJECTED",
            f"Credit Score: {credit_score}"
        )
        return {
            "decision": "REJECTED",
            "reason": "Credit score below minimum threshold",
            "customer": customer
        }

    # --------------------------------------------------
    # Rule 1 : Within Pre-approved Limit
    # --------------------------------------------------

    if loan_amount <= limit:
        log_agent(
            "UnderwritingAgent",
            "Loan Approval",
            "APPROVED",
            f"Loan Amount: {loan_amount}"
        )
        return {
            "decision": "APPROVED",
            "reason": "Within pre-approved limit",
            "customer": customer
        }

    # --------------------------------------------------
    # Rule 2 : Between 1x and 2x Limit
    # Salary Verification Required
    # --------------------------------------------------

    if loan_amount <= (2 * limit):

        log_agent(
            "UnderwritingAgent",
            "Salary Verification",
            "STARTED",
            f"Loan Amount: {loan_amount}"
        )

        salary_result = evaluate_salary(
            monthly_salary=salary,
            loan_amount=loan_amount,
            annual_interest_rate=annual_interest_rate,
            tenure_months=tenure_months
        )

        if salary_result["status"] == "APPROVED":
            log_agent(
                "SalaryAgent",
                "EMI Check",
                "APPROVED",
                f"EMI: {salary_result['emi']}"
            )
            return {
                "decision": "APPROVED",
                "reason": "Approved after salary verification",
                "salary_verification": salary_result,
                "customer": customer
            }

        log_agent(
            "SalaryAgent",
            "EMI Check",
            "REJECTED",
            f"EMI: {salary_result['emi']}"
        )
        return {
            "decision": "REJECTED",
            "reason": "Salary verification failed",
            "salary_verification": salary_result,
            "customer": customer
        }

    # --------------------------------------------------
    # Rule 3 : Loan exceeds underwriting limit
    # --------------------------------------------------

    return {
        "decision": "REJECTED",
        "reason": "Requested amount exceeds underwriting limit",
        "customer": customer
    }