# if custID in data then go ahead else create a new account

import os
from crewai import llm
from llm.llm import llm
from crewai import Agent, Task, Crew, Process
from tools.SearchCustomerTool import SearchCustomerTool
from tools.CreateCustomerTool import CreateCustomerTool

checker_agent = Agent(
    role="Customer Verification Officer",

    goal="""
    Verify whether a customer already exists.
    If not, create a new customer account.
    """,

    backstory="""
    You work in the customer onboarding department.
    Your responsibility is to ensure every customer exists in the database
    before any loan processing begins.
    """,

    tools=[
        SearchCustomerTool(),
        CreateCustomerTool()
    ],

    verbose=True,
    llm=llm
)

task = Task(
    description="""
    Customer ID: {customer_id}

    Check whether this customer exists.

    If the customer exists,
    simply return YES.

    If the customer does not exist,

    ask for the customer's

    - Name
    - Phone Number
    - Email Address

    Create a new account using the provided information.

    Finally return YES.
    """,

    expected_output="""
    Return YES if customer already exists else return new customer account created

    
    """,

    agent=checker_agent
)
crew = Crew(
    agents=[checker_agent],
    tasks=[task],
    process=Process.sequential,
    cache=True,
    memory=True,
    verbose=True

)
def run(customer_id: str):
    return crew.kickoff(
        inputs={
            "customer_id": customer_id
        }
    )

if __name__ == "__main__":
    customer_id = input("Enter your CustomerID: ")
    print(run(customer_id))


