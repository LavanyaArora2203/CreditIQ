"""App configuration loaded from env."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
BACKEND_DIR=ROOT_DIR.parent/"backend"
# JSON stores (sit alongside the existing data/customer_data.json).
DATA_DIR = ROOT_DIR / "data"
CUSTOMERS_FILE = BACKEND_DIR / "data" / "customer_data.json"   # ← changed
USERS_FILE = DATA_DIR / "users.json"  

allow_origins=[
    "http://localhost:5173",
    "https://credit-iq-psi.vercel.app",   # ← your actual Vercel domain, exact match
]
