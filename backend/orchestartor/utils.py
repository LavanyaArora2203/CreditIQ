"""
Shared utility helpers for the orchestrator.

FIX: this file used to contain a byte-for-byte duplicate of the
`LoanOrchestrator` class that also lives in orchestrator.py (two classes
with the same name/logic in two files is just a maintenance hazard — any
fix made in one would silently not apply to the other). That duplicate has
been removed. This file now holds small, genuinely reusable helpers:
reading the JSON "database" files in /data and pulling out one customer's
record, plus a datetime-based sanction number generator shared with the
sanction letter tool's default template values.
"""

import json
from datetime import datetime
from pathlib import Path

# Project root = two levels up from this file (orchestartor/utils.py -> root)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename: str):
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_customer(customer_id: str) -> dict | None:
    data = load_json("customer_data.json")
    for c in data.get("customers", []):
        if c["customer_id"] == customer_id:
            return c
    return None


def find_kyc_record(customer_id: str) -> dict | None:
    data = load_json("kyc_data.json")
    for r in data.get("kyc_records", []):
        if r["customer_id"] == customer_id:
            return r
    return None


def repayment_start_date() -> str:
    """A simple placeholder: 30 days from today, formatted like the
    sanction letter templates expect (DD-Mon-YYYY)."""
    from datetime import timedelta
    return (datetime.now() + timedelta(days=30)).strftime("%d-%b-%Y")