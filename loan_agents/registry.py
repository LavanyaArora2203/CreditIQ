from loan_agents.sales_agent import sales_agent
from loan_agents.verification_agent import verification_agent
from loan_agents.underwriting_agent import underwriting_agent
from loan_agents.sanction_letter_agent import sanction_agent

ALL_HANDOFFS = [
    sales_agent,
    verification_agent,
    underwriting_agent,
    sanction_agent,
]