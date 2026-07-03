from agents import Agent

from backend.prompts.master_prompt import MASTER_AGENT_PROMPT
from backend.Utils.constants import MASTER_AGENT_NAME

from backend.loan_agents.sales_agent import sales_agent
from backend.loan_agents.verification_agent import verification_agent
from backend.loan_agents.underwriting_agent import underwriting_agent
from backend.loan_agents.sanction_letter_agent import sanction_agent

from backend.Utils.constants import MASTER_AGENT_NAME
from backend.loan_agents.registry import ALL_HANDOFFS

master_agent = Agent(
    name=MASTER_AGENT_NAME,
    instructions=MASTER_AGENT_PROMPT,
    handoffs=ALL_HANDOFFS
)

