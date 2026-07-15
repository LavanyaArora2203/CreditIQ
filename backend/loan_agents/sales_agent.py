"""
Sales Agent (CrewAI)
=====================
Receives a text query from a "master agent", searches info.txt for the
relevant facts, and returns a single final answer string back to the
master agent.

Usage (direct, same process):
    from sales_agent import run_sales_agent
    answer = run_sales_agent("What is the price of the Professional plan?")

Usage (master agent as a separate CrewAI hierarchical crew):
    See `as_crewai_subagent()` below to plug this Agent directly into a
    manager/master Crew using Process.hierarchical.

Usage (master agent in a different process / service):
    Run `api.py` and POST {"query": "..."} to /ask
"""

import os
from crewai import Agent, Task, Crew, Process
# query=input("Enter user query")

from crewai_tools import TXTSearchTool
from crewai import llm
from llm.llm import llm
# query=input("Enter")
# ---------------------------------------------------------------------------
# 1. Tool
# ---------------------------------------------------------------------------
info_search_tool = TXTSearchTool(
    txt="info.txt"
)

# ---------------------------------------------------------------------------
# 2. Agent
# ---------------------------------------------------------------------------
sales_agent = Agent(
    role="Sales Support Agent",
    goal=(
        "Answer incoming questions accurately and concisely by grounding "
        "every answer in facts retrieved from info.txt. Never invent facts "
        "that are not present in the retrieved content."
    ),
    backstory=(
        "You are a product and pricing expert for the company. Your only "
        "source of truth is info.txt, which you access through the Info "
        "File Search Tool. You always search before answering, and if the "
        "requested information isn't in info.txt, you say so plainly "
        "instead of guessing."
    ),
    tools=[info_search_tool],
    verbose=True,
    allow_delegation=False,
    llm=llm
)


# ---------------------------------------------------------------------------
# 3. Task factory — one task per incoming query
# ---------------------------------------------------------------------------
task=Task(
        description=(
            f'The master agent sent the query"\n\n'
            "Steps:\n"
            "1. Use the Info File Search Tool to search info.txt for content "
            "relevant to this query.\n"
            "2. Read the returned passages carefully.\n"
            "3. Compose a direct, concise answer using only those facts.\n"
            "4. If the search returns no relevant information, clearly state "
            "that the answer is not available in info.txt rather than "
            "guessing."
        ),
        expected_output=(
            "A short, accurate, well-formed answer (1-5 sentences) suitable "
            "to hand back to the master agent as the final result. No "
            "meta-commentary about the search process."
        ),
        agent=sales_agent,
    )


##Crew() object is orchestrator of crew ai


# crew=Crew(

# )

crew = Crew(
    agents=[sales_agent],
    tasks=[task],
    process=Process.sequential,
    cache=True,
    memory=True,
    verbose=True

)

def run(query: str):
    return crew.kickoff(
        inputs={
            "query": query
        }
    )
if __name__ == "__main__":
    query = input("Enter query: ")
    print(run(query))


# if __name__ == "__main__":
#     # Simulated call from a master agent
#     incoming_query = os.environ.get(
#         "QUERY", "What is the price of the Professional plan and does it include support?"
#     )
#     print(f"\n[Master Agent -> Sales Agent] Query: {incoming_query}\n")
#     final_answer = run_sales_agent(incoming_query)
#     print(f"\n[Sales Agent -> Master Agent] Final Answer:\n{final_answer}\n")