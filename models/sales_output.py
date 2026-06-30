from pydantic import BaseModel


class SalesOutput(BaseModel):
    customer_id: str
    requested_loan_amount: int
    preferred_tenure_months: int
    offered_amount: int
    interest_rate: float | None = None
    sales_completed: bool
    remarks: str = ""