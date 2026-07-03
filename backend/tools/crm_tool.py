from agents import function_tool
import requests

API_URL = "http://127.0.0.1:8000"


@function_tool
def get_customer_kyc(customer_id: str):
    """
    Fetch customer KYC details from the CRM service.
    """

    try:
        response = requests.get(
            f"{API_URL}/kyc/{customer_id}",
            timeout=5
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e)
        }