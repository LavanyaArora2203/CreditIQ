import json
from pathlib import Path

from Utils.agent_logger import log_agent

# -------------------------------
# Load KYC Database
# -------------------------------

DATA_PATH = Path(__file__).resolve().parent.parent / "Data" / "kyc.json"

with open(DATA_PATH, "r") as file:
    KYC_DATABASE = json.load(file)


# -------------------------------
# Verify Customer
# -------------------------------

def verify_customer(
    customer_id: str,
    full_name: str,
    pan_number: str,
    address_line1: str
):
    """
    Verifies customer's KYC details.
    """

    customer = KYC_DATABASE.get(customer_id)

    if customer is None:
        log_agent(
            "VerificationAgent",
            "KYC Verification",
            "FAILED",
            "Customer not found"
        )
        return {
            "status": "FAILED",
            "reason": "Customer not found"
        }

    if customer["full_name"].strip().lower() != full_name.strip().lower():
        log_agent(
            "VerificationAgent",
            "KYC Verification",
            "FAILED",
            "Name mismatch"
        )
        return {
            "status": "FAILED",
            "reason": "Name mismatch"
        }

    if customer["pan_number"].upper() != pan_number.upper():
        log_agent(
            "VerificationAgent",
            "KYC Verification",
            "FAILED",
            "PAN mismatch"
        )
        return {
            "status": "FAILED",
            "reason": "PAN mismatch"
        }

    if customer["address_line1"].strip().lower() != address_line1.strip().lower():
        log_agent(
            "VerificationAgent",
            "KYC Verification",
            "FAILED",
            "Address mismatch"
        )
        return {
            "status": "FAILED",
            "reason": "Address mismatch"
        }

    if customer["kyc_status"] != "verified":
        log_agent(
            "VerificationAgent",
            "KYC Verification",
            "FAILED",
            "KYC not verified"
        )
        return {
            "status": "FAILED",
            "reason": "KYC not verified"
        }

    # Logging success state
    log_agent(
        "VerificationAgent",
        "KYC Verification",
        "VERIFIED",
        customer_id
    )
    
    return {
        "status": "VERIFIED",
        "message": "Customer verification successful",
        "customer": customer
    }