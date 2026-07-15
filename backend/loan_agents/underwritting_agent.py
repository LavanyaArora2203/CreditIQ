loan_amount=input("Enter:")
tenure=input("Enter:")
interest_rate=input("Enter:")
from crewai import llm
from llm.llm import llm
# customer_id==input("Enter:")
from crewai import Agent, Task, Crew, Process
from tools.credit_bureau_tool import CreditBureauTool
from tools.emi_cal_tool import EMICalculatorTool
from tools.PolicyRetrivalTool import PolicyRetrieverTool
from models.output.underwriting_output import UnderwritingDecision
from models.input.underwriting_input import UnderwritingInput
underwriting_agent = Agent(
    role="Senior Personal Loan Underwriter",

    goal="""
    Evaluate every personal loan application fairly and accurately
    by analyzing the applicant's credit profile, financial health,
    loan request, and company lending policies before making
    an approval or rejection decision.
    """,

    backstory="""
    You are a Senior Underwriting Officer with over 15 years of
    experience in retail banking and personal loan underwriting.

    Your expertise includes:
    - Credit Risk Assessment
    - Income Analysis
    - Debt-to-Income (DTI) Evaluation
    - Loan Eligibility Assessment
    - EMI Affordability Analysis
    - Company Lending Policy Compliance

    You never approve or reject loans randomly.
    Every decision must be supported by objective financial data
    and the company's lending policies.

    You carefully verify the customer's repayment capacity,
    previous repayment behaviour, current liabilities,
    requested loan amount and tenure before making a decision.

    Your primary responsibility is to minimize loan defaults
    while approving eligible customers.
    """,

    tools=[
        CreditBureauTool(),
        PolicyRetrieverTool(),
        EMICalculatorTool()
    ],

    allow_delegation=False,

    memory=True,

    verbose=True,

    max_iter=10,
    llm=llm
)
from crewai import Task
task = Task(

    description="""
You have received a new personal loan application.

Customer ID:
{customer_id}

Requested Loan Amount:
₹{loan_amount}

Requested Tenure:
{tenure} months

-------------------------------
Instructions
-------------------------------

Step 1

Use the Credit Bureau Tool to retrieve the customer's
complete credit profile.

-------------------------------

Step 2

Use the Policy Retriever Tool to retrieve all company
lending policies.

-------------------------------

Step 3

Determine the applicable annual interest rate
according to the retrieved company policies.

-------------------------------

Step 4

Use the EMI Calculator Tool to calculate the
monthly EMI using

• Loan Amount

• Interest Rate

• Loan Tenure

-------------------------------

Step 5

Evaluate all of the following:

• Credit Score

• Monthly Income

• Existing EMI

• Active Loans

• Previous Defaults

• Requested Loan Amount

• Loan Tenure

• Monthly EMI

• Debt-to-Income Ratio

• Company Policies

-------------------------------

Step 6

Based on the above information,
decide whether the loan should be

APPROVED

or

REJECTED

-------------------------------

Your decision must be completely based on
company policies and customer financial data.

Never make assumptions.

Always explain the reasons for your decision.
""",

    expected_output="""
Return the result in JSON format.

{
    "customer_id": "",
    "decision": "APPROVED or REJECTED",
    "approved_amount": 0,
    "interest_rate": 0,
    "tenure": 0,
    "monthly_emi": 0,
    "credit_score": 0,
    "monthly_income": 0,
    "existing_emi": 0,
    "debt_to_income_ratio": 0,
    "reason": ""
}
""",


    agent=underwriting_agent,
    output_pydantic=UnderwritingDecision,
)


crew = Crew(
    agents=[underwriting_agent],
    tasks=[task],
    process=Process.sequential,
    cache=True,
    memory=True,
    verbose=True

)

def run(
    loan_amount,
    tenure,
    interest_rate,
):
    return crew.kickoff(
        inputs={
            "loan_amount": loan_amount,
            "tenure": tenure,
            "interest_rate": interest_rate,
        }
    )

if __name__ == "__main__":
    loan_amount = float(input("Loan Amount: "))
    tenure = int(input("Tenure: "))
    interest_rate = float(input("Interest Rate: "))

    print(
        run(
            loan_amount,
            tenure,
            interest_rate,
        )
    )




