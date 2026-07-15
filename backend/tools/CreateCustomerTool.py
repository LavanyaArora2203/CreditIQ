import json
from crewai.tools import BaseTool

class CreateCustomerTool(BaseTool):
    name : str = "Create Customer"
    description : str = "Create a new customer account."

    def _run(self,
             customer_id: str,
             name: str,
             phone: str,
             email: str):

        with open("data/customer_data.json", "r") as f:
            customers = json.load(f)

        new_customer = {
            "customer_id": customer_id,
            "name": name,
            "phone": phone,
            "email": email
        }

        customers.append(new_customer)

        with open("data/customer_data.json", "w") as f:
            json.dump(customers, f, indent=4)

        return "Customer created successfully."