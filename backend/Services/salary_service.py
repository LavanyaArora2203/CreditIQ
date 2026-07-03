from typing import Dict
import math


# ---------------------------------------------------
# EMI Calculator
# ---------------------------------------------------

def calculate_emi(
    loan_amount: float,
    annual_interest_rate: float = 10.0,
    tenure_months: int = 60
) -> float:
    """
    Calculate EMI using the standard EMI formula.

    Parameters
    ----------
    loan_amount : float
    annual_interest_rate : float
    tenure_months : int

    Returns
    -------
    float
        Monthly EMI
    """

    monthly_rate = annual_interest_rate / (12 * 100)

    if monthly_rate == 0:
        return round(loan_amount / tenure_months, 2)

    emi = (
        loan_amount
        * monthly_rate
        * math.pow(1 + monthly_rate, tenure_months)
    ) / (
        math.pow(1 + monthly_rate, tenure_months) - 1
    )

    return round(emi, 2)


# ---------------------------------------------------
# EMI Eligibility
# ---------------------------------------------------

def evaluate_salary(
    monthly_salary: float,
    loan_amount: float,
    annual_interest_rate: float = 10.0,
    tenure_months: int = 60
) -> Dict:
    """
    Determines whether the EMI exceeds 50%
    of the customer's monthly salary.
    """

    emi = calculate_emi(
        loan_amount,
        annual_interest_rate,
        tenure_months
    )

    allowed_emi = monthly_salary * 0.50

    if emi <= allowed_emi:

        return {
            "status": "APPROVED",
            "emi": emi,
            "allowed_emi": round(allowed_emi, 2),
            "reason": "EMI within affordability limit."
        }

    return {
        "status": "REJECTED",
        "emi": emi,
        "allowed_emi": round(allowed_emi, 2),
        "reason": "EMI exceeds 50% of monthly salary."
    }