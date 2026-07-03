from typing import Dict


def generate_response(result: Dict) -> str:
    """
    Converts underwriting decisions into user-friendly chatbot responses.
    """

    decision = result.get("decision", "")
    reason = result.get("reason", "")
    customer = result.get("customer", {})

    name = customer.get("customer_id", "Customer")

    # --------------------------------------------------
    # Approved
    # --------------------------------------------------

    if decision == "APPROVED":

        return (
            f"🎉 Congratulations!\n\n"
            f"Your personal loan has been approved.\n\n"
            f"Reason: {reason}\n\n"
            f"Our team will now generate your sanction letter."
        )

    # --------------------------------------------------
    # Credit Score
    # --------------------------------------------------

    if "Credit score" in reason:

        return (
            "Unfortunately, the application could not be approved because "
            "the credit score is below the bank's eligibility criteria.\n\n"
            "Improving the credit score and applying again after a few months "
            "may increase the chances of approval."
        )

    # --------------------------------------------------
    # Salary
    # --------------------------------------------------

    if "Salary" in reason or "EMI" in reason:

        return (
            "The requested loan amount results in an EMI that exceeds the "
            "permitted affordability limit.\n\n"
            "A smaller loan amount may be eligible for approval."
        )

    # --------------------------------------------------
    # Limit
    # --------------------------------------------------

    if "underwriting limit" in reason.lower():

        limit = customer.get("preapproved_limit", 0)

        return (
            f"The requested amount exceeds the maximum eligible loan amount.\n\n"
            f"Based on the current profile, the pre-approved limit is ₹{limit:,}."
        )

    return f"Application Status : {decision}\nReason : {reason}"