from agents import Agent
from tools.offermart_tool import get_customer_offer
from prompts.sales_prompt import SALES_AGENT_PROMPT
from models.sales_output import SalesOutput

sales_agent = Agent(
    name="Sales Agent",
    handoff_description=(
        "Handles customer loan enquiries, explains loan offers, "
        "collects loan preferences, and guides customers through "
        "the sales conversation."
    ),
    instructions=SALES_AGENT_PROMPT,

    tools=[
        get_customer_offer
    ],
    output_type=SalesOutput

)
    
