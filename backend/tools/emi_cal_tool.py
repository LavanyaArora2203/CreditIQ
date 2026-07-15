from crewai.tools import BaseTool
import math

class EMICalculatorTool(BaseTool):
    name: str = "EMI Calculator Tool"
    description: str = (
        "Calculate monthly EMI for a loan."
    )

    def _run(
        self,
        loan_amount: float,
        annual_interest_rate: float,
        tenure_months: int
    ) -> dict:

        monthly_rate = annual_interest_rate / (12 * 100)

        emi = (
            loan_amount
            * monthly_rate
            * math.pow(1 + monthly_rate, tenure_months)
        ) / (
            math.pow(1 + monthly_rate, tenure_months) - 1
        )

        return {
            "loan_amount": loan_amount,
            "interest_rate": annual_interest_rate,
            "tenure": tenure_months,
            "monthly_emi": round(emi, 2)
        }