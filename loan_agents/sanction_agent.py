from agents import Agent

from prompts.sanction_prompt import SANCTION_AGENT_PROMPT
from utils.constants import SANCTION_AGENT_NAME


sanction_agent = Agent(
    name=SANCTION_AGENT_NAME,
    instructions=SANCTION_AGENT_PROMPT,
    handoff_description=(
        "Generates the final loan sanction response and sanction letter."
    ),
)