import json
from crewai.tools import BaseTool

class KYCRetrievalTool(BaseTool):

    name : str = "KYC Retrieval Tool"

    description : str = (
        "Retrieve customer KYC details using customer ID."
    )

    def _run(self, customer_id: str):

        with open("data/kyc_data.json") as f:
            customers = json.load(f)

        for customer in customers:
            if customer["customer_id"] == customer_id:
                return customer

        return {
            "status": "NOT_FOUND"
        }