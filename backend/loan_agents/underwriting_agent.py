from agents import Agent

from backend.prompts.underwriting_prompt import UNDERWRITING_AGENT_PROMPT
from backend.Utils.constants import UNDERWRITING_AGENT_NAME


underwriting_agent = Agent(
    name=UNDERWRITING_AGENT_NAME,
    instructions=UNDERWRITING_AGENT_PROMPT,
    handoff_description=(
        "Evaluates financial risk and recommends loan approval or rejection."
    ),
)