from agents import Agent

from prompts.sales_prompt import SALES_AGENT_PROMPT


sales_agent = Agent(
    name="SalesAgent",
    instructions=SALES_AGENT_PROMPT,
    handoff_description=(
        "Handles customer onboarding, loan enquiries, "
        "and collects missing application details."
    ),
)