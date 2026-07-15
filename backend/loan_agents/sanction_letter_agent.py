
from tools.SanctionLetterTool import SanctionLetterTool
from crewai import Agent, Task, Crew, Process
from crewai import llm
from llm.llm import llm

loan_sanction_agent = Agent(
    role="Loan Sanction Letter Generator",

    goal="""
    Generate a professional Personal Loan Sanction Letter for customers whose
    loan has already been approved by the Underwriting Agent.

    Do NOT perform underwriting or verification.

    Only generate the sanction letter from the approved loan information
    received from the Master Agent.
    """,

    backstory="""
    You are the documentation specialist of an NBFC.

    Your responsibility begins only after the customer's loan has been approved.

    You create RBI-style professional sanction letters using the approved
    customer information, loan details, repayment schedule,
    applicable conditions, and company details.

    Your output should be accurate, properly formatted,
    and suitable for conversion into PDF.

    Never modify approved values.

    Never reject or approve loans.

    Never perform any calculations unless explicitly asked.

    Always return a structured sanction letter.
    """,

    verbose=True,
    allow_delegation=False,
    tools=[
        SanctionLetterTool()
    ],
    llm=llm
)
from crewai import Task

task = Task(
    description="""
The loan has already been approved.

Using ONLY the approved information received from the Master Agent,
generate a complete Personal Loan Sanction Letter.

Input will contain:

Customer Information
--------------------
Customer Name
Customer ID
Address
Phone
Email

Loan Information
----------------
Loan Type
Approved Amount
Interest Rate
Loan Tenure
EMI
Processing Fee
Disbursement Amount
Repayment Start Date

Credit Summary
--------------
Credit Score
Risk Category

Approval Summary
----------------
Approval Status
Approval Reason

Company Information
-------------------
Company Name
Company Address
Support Email
Support Phone

Generate a professional sanction letter.

Do NOT change any approved values.

If any optional field is unavailable,
mention "Not Applicable".

Return ONLY the sanction letter.

Do not explain anything.
""",

    expected_output="""
A complete Personal Loan Sanction Letter containing:

- Company Header
- Sanction Letter Number
- Date
- Customer Details
- Loan Details
- Credit Assessment Summary
- Repayment Details
- Terms and Conditions
- Approval Summary
- Authorized Signatory
- Footer

The output should be professionally formatted and ready for PDF generation.
""",

    agent=loan_sanction_agent
)
crew = Crew(
    agents=[loan_sanction_agent],
    tasks=[task],
    process=Process.sequential,
    cache=True,
    memory=True,
    verbose=True

)


def run(approved_data: dict):
    """
    approved_data must look like:
    {
        "company": {"name": ..., "address": ..., "email": ..., "phone": ...},
        "customer": {"customer_id": ..., "name": ..., "address": ..., "phone": ..., "email": ...},
        "loan": {"loan_type": ..., "approved_amount": ..., "interest_rate": ...,
                 "tenure_months": ..., "emi": ..., "processing_fee": ...,
                 "disbursement_amount": ..., "repayment_start_date": ...},
        "credit_summary": {"credit_score": ..., "risk_category": ...},
        "approval_summary": {"status": ..., "reason": ...}
    }
    """
    return crew.kickoff(inputs={"approved_data": approved_data})


# Expected Input from Master Agent
# approved_loan = {
#     "company": {
#         "name": "ABC Finance Ltd",
#         "address": "New Delhi",
#         "email": "support@abcfinance.com",
#         "phone": "1800-000-000"
#     },

#     "customer": {
#         "customer_id": "CUST1024",
#         "name": "Rahul Sharma",
#         "address": "Delhi",
#         "phone": "9876543210",
#         "email": "rahul@gmail.com"
#     },

#     "loan": {
#         "loan_type": "Personal Loan",
#         "approved_amount": 500000,
#         "interest_rate": 10.5,
#         "tenure_months": 60,
#         "emi": 10747,
#         "processing_fee": 5000,
#         "disbursement_amount": 495000,
#         "repayment_start_date": "05-Aug-2026"
#     },

#     "credit_summary": {
#         "credit_score": 785,
#         "risk_category": "Low"
#     },

#     "approval_summary": {
#         "status": "Approved",
#         "reason": "Excellent repayment history and policy compliant."
#     }
# }


