from Services.underwriting_service import evaluate_loan

test_cases = [
    ("CUST001", 400000),   # Within limit
    ("CUST002", 500000),   # EMI evaluation
    ("CUST002", 700000),   # Above 2× limit
    ("CUST005", 200000),   # Low credit score
    ("CUST010", 100000),   # Low credit score
]

for customer_id, amount in test_cases:
    print("=" * 50)
    print(f"Customer: {customer_id}")
    print(f"Loan Amount: ₹{amount:,}")

    result = evaluate_loan(customer_id, amount)

    print(f"Decision: {result['decision']}")
    print(f"Reason: {result['reason']}")

    if "emi" in result:
        print(f"EMI: ₹{result['emi']}")