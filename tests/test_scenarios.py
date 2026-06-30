from Services.underwriting_service import evaluate_loan
from Services.verification_service import verify_customer


def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_result(result):
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print(result)


def run_tests():

    print_header("AI CREDIT ANALYST - DAY 6 TEST SUITE")

    # ---------------------------------------------------
    # Scenario 1
    # Low Credit Score
    # ---------------------------------------------------

    print("\nScenario 1 : Low Credit Score")

    result = evaluate_loan(
        customer_id="CUST010",
        loan_amount=100000
    )

    print_result(result)

    print("\n" + "-" * 70)

    # ---------------------------------------------------
    # Scenario 2
    # Loan exceeds 2x pre-approved limit
    # ---------------------------------------------------

    print("\nScenario 2 : Loan Exceeds Maximum Eligible Amount")

    result = evaluate_loan(
        customer_id="CUST002",
        loan_amount=700000
    )

    print_result(result)

    print("\n" + "-" * 70)

    # ---------------------------------------------------
    # Scenario 3
    # Salary Slip Required
    # EMI too high
    # ---------------------------------------------------

    print("\nScenario 3 : Salary Slip Required + High EMI")

    result = evaluate_loan(
        customer_id="CUST003",
        loan_amount=1000000
    )

    print_result(result)

    print("\n" + "-" * 70)

    # ---------------------------------------------------
    # Scenario 4
    # Salary Slip Required
    # EMI acceptable
    # ---------------------------------------------------

    print("\nScenario 4 : Salary Slip Required + EMI Acceptable")

    result = evaluate_loan(
        customer_id="CUST003",
        loan_amount=900000
    )

    print_result(result)

    print("\n" + "-" * 70)

    # ---------------------------------------------------
    # Scenario 5
    # KYC Verification Failure
    # ---------------------------------------------------

    print("\nScenario 5 : KYC Verification Failure")

    try:

        result = verify_customer(
            customer_id="CUST001",
            full_name="Arjun Mehta",
            pan_number="ARJPM1234A",
            address_line1="Wrong Address"
        )

    except TypeError:
        # In case your verification agent accepts a single dictionary

        result = verify_customer(
            customer_id="CUST001",
            customer_data={
                "full_name": "Arjun Mehta",
                "pan_number": "ARJPM1234A",
                "address_line1": "Wrong Address"
            }
        )

    print_result(result)

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()