from crewai.tools import BaseTool
from pathlib import Path

class PolicyRetrieverTool(BaseTool):
    name: str = "Policy Retriever Tool"
    description: str = (
        "Retrieve company loan policies from company_policies.txt."
    )

    policy_file: str = "data/company_policies.txt"

    def _run(self) -> str:
        try:
            path = Path(self.policy_file)

            if not path.exists():
                return "Policy file not found."

            return path.read_text(encoding="utf-8")

        except Exception as e:
            return f"Error reading policy file: {e}"