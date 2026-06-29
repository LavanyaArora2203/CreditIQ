from agents import Agent

from prompts.master_prompt import MASTER_AGENT_PROMPT
from utils.constants import MASTER_AGENT_NAME

from loan_agents.sales_agent import sales_agent
from loan_agents.verification_agent import verification_agent
from loan_agents.underwriting_agent import underwriting_agent
from loan_agents.sanction_agent import sanction_agent

from utils.constants import MASTER_AGENT_NAME
from loan_agents.registry import ALL_HANDOFFS

master_agent = Agent(
    name=MASTER_AGENT_NAME,
    instructions=MASTER_AGENT_PROMPT,
    handoffs=ALL_HANDOFFS
)

