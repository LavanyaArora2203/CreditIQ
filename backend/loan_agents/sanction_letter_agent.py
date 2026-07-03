import logging
import json

from agents import Agent, function_tool

from backend.Utils.emi_calculator import calculate_emi
from backend.Services.sanction_letter_service import generate_sanction_letter
from backend.prompts.sanction_prompt import SANCTION_AGENT_PROMPT

from pydantic import BaseModel

class Customer(BaseModel):
    name: str
    customer_id: str
logger = logging.getLogger(__name__)


@function_tool
def generate_sanction_letter_tool(
    customer: Customer,
    loan_amount: float,
    decision: str,
    interest_rate: float,
    tenure_months: int,
):
    customer = json.loads(customer)
    """
    Generate a loan sanction letter for an approved customer.

    Args:
        customer (dict):
            Customer information.

        loan_amount (float):
            Approved loan amount.

        decision (str):
            Loan decision from underwriting engine.

        interest_rate (float):
            Annual interest rate.

        tenure_months (int):
            Loan tenure in months.

    Returns:
        dict:
            Status and sanction letter details or failure reason.
    """

    try:
        # ----------------------------
        # Validate decision
        # ----------------------------
        if decision.upper() != "APPROVED":
            return {
                "status": "skipped",
                "reason": "Loan not approved"
            }

        # ----------------------------
        # Validate customer
        # ----------------------------
        if not customer:
            return {
                "status": "failed",
                "reason": "Customer details not found"
            }

        # ----------------------------
        # Validate required fields
        # ----------------------------
        customer_name = customer.name
        customer_id = customer.customer_id

        if not customer_name or not customer_id:
            return {
                "status": "failed",
                "reason": "Missing customer information"
            }

        # ----------------------------
        # Validate loan amount
        # ----------------------------
        if loan_amount <= 0:
            return {
                "status": "failed",
                "reason": "Invalid loan amount"
            }

        # ----------------------------
        # Validate loan parameters
        # ----------------------------
        if interest_rate <= 0:
            return {
                "status": "failed",
                "reason": "Invalid interest rate"
            }

        if tenure_months <= 0:
            return {
                "status": "failed",
                "reason": "Invalid loan tenure"
            }

        logger.info(
            f"Generating sanction letter for customer {customer_id}"
        )

        # ----------------------------
        # Calculate EMI
        # ----------------------------
        emi = calculate_emi(
            principal=loan_amount,
            annual_interest_rate=interest_rate,
            tenure_months=tenure_months,
        )

        # ----------------------------
        # Generate sanction letter
        # ----------------------------
        sanction_letter = generate_sanction_letter(
            customer_name=customer_name,
            customer_id=customer_id,
            loan_amount=loan_amount,
            tenure_months=tenure_months,
            interest_rate=interest_rate,
            emi=round(emi, 2),
        )

        logger.info(
            f"Sanction letter successfully generated for {customer_id}"
        )

        return {
            "status": "success",
            "sanction_letter": sanction_letter,
        }

    except Exception as e:
        logger.exception("Failed to generate sanction letter")

        return {
            "status": "failed",
            "reason": str(e),
        }


sanction_agent = Agent(
    name="Sanction Agent",

    handoff_description=(
        "Creates the official loan sanction letter "
        "for approved loan applications using the "
        "finalized loan terms."
    ),

    instructions=SANCTION_AGENT_PROMPT,

    tools=[
        generate_sanction_letter_tool,
    ],
)