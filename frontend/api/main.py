# frontend/api/main.py — add at the top, before other imports
from __future__ import annotations

import sys, os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))   # makes `loan_agents`, `orchestartor`, `tools`, `models` importable
os.chdir(BACKEND_DIR)                   # makes tools' relative "data/..." paths resolve correctly

from fastapi import FastAPI
# ...rest of the existing file unchanged

"""FastAPI entrypoint.

Run:
    uvicorn api.main:app --reload --port 9000
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import me_router, router as auth_router
from .chat_stream import router as chat_router
from .config import CORS_ORIGINS

app = FastAPI(title="Loan Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(me_router)
app.include_router(chat_router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
