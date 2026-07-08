import requests
from agents import function_tool



API_URL = "http://127.0.0.1:8000"

@function_tool
def get_customer_offer(customer_id: str):
    """
    Fetch a customer's loan offer from the Offer Mart API.
    """

    try:
        response = requests.get(f"{API_URL}/offer/{customer_id}", timeout=5)

        if response.status_code == 200:
            return response.json()

        return {
            "error": f"Customer {customer_id} not found."
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e)
        }