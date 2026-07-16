"""Auth: signup, login, JWT, current-user dependency."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET
from .schemas import LoginRequest, SignupRequest, TokenResponse, UserProfile
from .users_store import create_user, customer_exists, get_customer, get_user

router = APIRouter(prefix="/auth", tags=["auth"])
me_router = APIRouter(tags=["me"])

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _make_token(customer_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": customer_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        customer_id = payload.get("sub")
        if not customer_id:
            raise JWTError("no sub")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    user = get_user(customer_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer exists")
    return user


@router.post("/signup", response_model=TokenResponse)
def signup(req: SignupRequest) -> TokenResponse:
    cid = req.customer_id.strip().upper()

    # Rule: only allow signup if the customer_id exists in customer_data.json.
    if not customer_exists(cid):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Customer ID not found. Please create a new account with your bank first.",
        )
    if get_user(cid):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "An account already exists for this Customer ID. Please log in.",
        )

    create_user(cid, pwd_ctx.hash(req.password))
    return TokenResponse(access_token=_make_token(cid), customer_id=cid)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest) -> TokenResponse:
    cid = req.customer_id.strip().upper()
    user = get_user(cid)
    if not user or not pwd_ctx.verify(req.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Customer ID or password")
    return TokenResponse(access_token=_make_token(cid), customer_id=cid)


@me_router.get("/me", response_model=UserProfile)
def me(user: dict[str, Any] = Depends(get_current_user)) -> UserProfile:
    cid = user["customer_id"]
    customer = get_customer(cid) or {}
    return UserProfile(
        customer_id=cid,
        name=customer.get("name") or customer.get("full_name"),
        email=customer.get("email"),
        phone=customer.get("phone") or customer.get("mobile"),
    )
