import requests
from crewai.tools import BaseTool

class CreditBureauTool(BaseTool):
    name: str = "Credit Bureau Tool"
    description: str = (
        "Retrieve a customer's credit report using their customer ID."
    )

    api_url: str = "http://localhost:8000/api/credit-bureau"

    def _run(self, customer_id: str) -> dict:
        try:
            response = requests.get(
                f"{self.api_url}/{customer_id}",
                timeout=10
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }