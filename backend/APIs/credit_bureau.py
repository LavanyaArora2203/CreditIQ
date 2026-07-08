from fastapi import FastAPI, HTTPException
import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(
    prefix="/credit",
    tags=["Credit Bureau"]
)

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "Data"
    / "customers.json"
)


def load_customers():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/{customer_id}")
async def get_credit_details(customer_id: str):

    customers = load_customers()

    for customer in customers:

        if customer["Customer ID"] == customer_id:

            return {
                "customer_id": customer["Customer ID"],
                "credit_score": customer["Credit Score (/900)"],
                "monthly_salary": customer["Monthly Salary (₹)"],
                "preapproved_limit": customer["Pre-Approved Limit (₹)"],
                "existing_loan": customer["Existing Loan (₹)"],
                "name": customer["Name"],
            }

    raise HTTPException(
        status_code=404,
        detail="Customer not found",
    )