def calculate_emi(principal, annual_interest_rate, tenure_months):
    """
    Calculates monthly EMI.

    principal : Loan Amount
    annual_interest_rate : e.g. 10 for 10%
    tenure_months : e.g. 60 months
    """

    monthly_rate = annual_interest_rate / (12 * 100)

    if monthly_rate == 0:
        return principal / tenure_months

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** tenure_months
    ) / (
        (1 + monthly_rate) ** tenure_months - 1
    )

    return round(emi, 2)