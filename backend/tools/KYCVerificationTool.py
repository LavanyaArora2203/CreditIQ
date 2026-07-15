from crewai.tools import BaseTool
class KYCVerificationTool(BaseTool):

    name : str = "KYC Verification Tool"

    description : str= (
        "Verify customer KYC information."
    )

    def _run(self, customer: dict):

        errors = []

        required_fields = [
            "name",
            "aadhaar",
            "pan",
            "dob",
            "address",
            "mobile"
        ]

        for field in required_fields:

            if not customer.get(field):

                errors.append(f"{field} missing")

        if errors:

            return {
                "verified": False,
                "errors": errors
            }

        return {
            "verified": True,
            "errors": []
        }