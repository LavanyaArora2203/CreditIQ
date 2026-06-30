import asyncio
from agents import Runner
from loan_agents.verification_agent import verification_agent


async def main():

    result = await Runner.run(
        verification_agent,
        """
Customer ID is CUST003.

Phone is 9988776655.

Address is 56 Indiranagar.
"""
    )

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())