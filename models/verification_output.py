from pydantic import BaseModel


class VerificationOutput(BaseModel):
    customer_id: str
    phone_verified: bool
    address_verified: bool
    kyc_verified: bool
    verification_completed: bool
    failed_fields: list[str] = []
    remarks: str = ""