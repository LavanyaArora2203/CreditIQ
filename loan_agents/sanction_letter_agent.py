from Services.sanction_letter_service import generate_sanction_letter


def create_sanction_letter(
    customer: dict,
    loan_amount: float,
    decision: str,
):
    """
    Generates a sanction letter only for approved loans.
    """

    if decision != "APPROVED":
        return {
            "status": "skipped",
            "reason": "Loan not approved"
        }

    # Basic assumptions for now
    interest_rate = 10.5
    tenure_months = 36

    emi = (
        loan_amount *
        (1 + (interest_rate / 100))
    ) / tenure_months

    result = generate_sanction_letter(
        customer_name=customer["name"],
        customer_id=customer["customer_id"],
        loan_amount=loan_amount,
        tenure_months=tenure_months,
        interest_rate=interest_rate,
        emi=round(emi, 2),
    )

    return result