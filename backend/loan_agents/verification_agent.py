from agents import Agent
from backend.models.verification_output import VerificationOutput


from backend.prompts.verification_prompt import VERIFICATION_AGENT_PROMPT
from backend.Utils.constants import VERIFICATION_AGENT_NAME
from backend.tools.crm_tool import get_customer_kyc


verification_agent = Agent(
    name=VERIFICATION_AGENT_NAME,
    instructions=VERIFICATION_AGENT_PROMPT,
    handoff_description=(
        "Verifies customer identity, PAN, Aadhaar, and KYC."
    ),
    output_type=VerificationOutput,
    tools=[
        get_customer_kyc
    ]
)
