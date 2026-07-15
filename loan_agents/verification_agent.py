from crewai import Agent, Task, Crew, Process
from crewai import llm
from llm.llm import llm
from tools.KYCRetrivalTool import KYCRetrievalTool
from tools.KYCVerificationTool import KYCVerificationTool
from models.output.underwriting_output import UnderwritingDecision
from models.input.underwriting_input import UnderwritingInput
verification_agent = Agent(

    role="KYC Verification Officer",

    goal="""
    Verify that the customer's KYC
    information is complete and valid.
    """,

    backstory="""
    You work in the onboarding department.

    Before any loan application is processed,
    you verify the customer's KYC documents.

    You carefully inspect all mandatory
    information before approving verification.
    """,

    tools=[
        KYCRetrievalTool(),
        KYCVerificationTool()
    ],

    verbose=True,

    allow_delegation=False,
    llm=llm
)

task = Task(

    description="""
Customer ID:

{customer_id}

Use the KYC Retrieval Tool to retrieve the
customer information.

Then use the KYC Verification Tool.

If all mandatory information exists,
mark the KYC as VERIFIED.

Otherwise mark it as FAILED.

Never assume missing information.
""",

    expected_output="""
{
    "customer_id":"",
    "kyc_status":"VERIFIED or FAILED",
    "reason":"",
    "missing_fields":[]
}
""",

    agent=verification_agent,
    output_pydantic=UnderwritingDecision,
)

crew = Crew(
    agents=[verification_agent],
    tasks=[task],
    process=Process.sequential,
    cache=True,
    memory=True,
    verbose=True

)

 
def run(customer_id: str):
    """Runs the verification crew and returns the raw CrewOutput.
    Use `.pydantic` on the result to get a validated KYCVerificationResult.
    """
    return crew.kickoff(inputs={"customer_id": customer_id})