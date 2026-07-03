import asyncio

from agents import Runner

from loan_agents.master_agent import master_agent


async def main():

    user_query = "My Aadhaar verification is pending."
    print(f"\nUSER : {user_query}\n")

    result = await Runner.run(
        starting_agent=master_agent,
        input=user_query,
    )

    print("\nFINAL OUTPUT\n")
    print(result.final_output)

    print("\nLAST AGENT\n")
    print(result.last_agent.name)


if __name__ == "__main__":
    asyncio.run(main())