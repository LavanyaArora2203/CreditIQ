import json
from crewai.tools import BaseTool

class SearchCustomerTool(BaseTool):
    name : str = "Search Customer"
    description : str = "Search a customer by customer ID."

    def _run(self, customer_id: str):
        with open("data/customer_data.json", "r") as f:
            customers = json.load(f)

        for customer in customers:
            if customer["customer_id"] == customer_id:
                return {
                    "exists": True,
                    "customer": customer
                }

        return {
            "exists": False
        }