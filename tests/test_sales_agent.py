import asyncio

from agents import Runner
from loan_agents.sales_agent import sales_agent


async def main():
    result = await Runner.run(
        sales_agent,
        "My customer ID is CUST003."
    )

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())