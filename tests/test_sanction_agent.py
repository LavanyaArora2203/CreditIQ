from loan_agents.sanction_letter_agent import create_sanction_letter

customer = {
    "customer_id": "CUST002",
    "name": "Priya Sharma",
}

# result = create_sanction_letter(
#     customer=customer,
#     loan_amount=300000,
#     decision="APPROVED",
# )
result = create_sanction_letter(
    customer=customer,
    loan_amount=300000,
    decision="REJECTED",
)



print(result)

