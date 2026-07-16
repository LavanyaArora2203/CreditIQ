"""Pydantic schemas for the API layer."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    customer_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer_id: str


class UserProfile(BaseModel):
    customer_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    # Optional structured hints from a quick-apply form:
    loan_amount: Optional[float] = None
    tenure_months: Optional[int] = None
    interest_rate: Optional[float] = None
