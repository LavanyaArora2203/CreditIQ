from agents import Agent

from prompts.verification_prompt import VERIFICATION_AGENT_PROMPT
from utils.constants import VERIFICATION_AGENT_NAME


verification_agent = Agent(
    name=VERIFICATION_AGENT_NAME,
    instructions=VERIFICATION_AGENT_PROMPT,
    handoff_description=(
        "Verifies customer identity, PAN, Aadhaar, and KYC."
    ),
)
