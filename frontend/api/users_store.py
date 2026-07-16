"""JSON-backed user + customer lookup.

users.json shape:
{
  "users": {
    "CUST001": { "customer_id": "CUST001", "password_hash": "<bcrypt>", "created_at": "..." }
  }
}
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from .config import CUSTOMERS_FILE, USERS_FILE

_LOCK = threading.Lock()


def _ensure_users_file() -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps({"users": {}}, indent=2))


def _read_users() -> dict[str, Any]:
    _ensure_users_file()
    with USERS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_users(data: dict[str, Any]) -> None:
    with USERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_customers() -> list[dict[str, Any]]:
    if not CUSTOMERS_FILE.exists():
        return []
    with CUSTOMERS_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    # Support either {"customers": [...]} or a bare list.
    if isinstance(raw, dict):
        return raw.get("customers", raw.get("data", []))
    return raw


def customer_exists(customer_id: str) -> bool:
    return get_customer(customer_id) is not None


def get_customer(customer_id: str) -> Optional[dict[str, Any]]:
    cid = customer_id.strip().upper()
    for c in _load_customers():
        rec_id = str(c.get("customer_id") or c.get("id") or "").upper()
        if rec_id == cid:
            return c
    return None


def get_user(customer_id: str) -> Optional[dict[str, Any]]:
    cid = customer_id.strip().upper()
    users = _read_users()["users"]
    return users.get(cid)


def create_user(customer_id: str, password_hash: str) -> dict[str, Any]:
    cid = customer_id.strip().upper()
    with _LOCK:
        data = _read_users()
        if cid in data["users"]:
            raise ValueError("account_exists")
        rec = {
            "customer_id": cid,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data["users"][cid] = rec
        _write_users(data)
        return rec
