"""Chat endpoint.

Two modes:
- Conversational Q&A: if the user hasn't yet given loan_amount + tenure +
  interest_rate, we invoke the existing sales_agent for a friendly reply
  (fallback: a canned reply if the agent import fails).
- Loan application: once we have the three fields, we run
  LoanOrchestrator.execute(...) in a worker thread and stream stage-by-stage
  progress events over SSE.

We DO NOT modify the orchestrator or the agents. Because the orchestrator
returns synchronously, we emit staged progress events on a light schedule
while it runs, and emit the final result event with the real payload once
execute() returns. If any stage rejects, we surface the reason immediately.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Any, AsyncIterator, Optional

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from .auth import get_current_user
from .schemas import ChatRequest

router = APIRouter(tags=["chat"])

STAGE_SEQUENCE = [
    ("checker", "Verifying your customer profile"),
    ("sales", "Matching you with the best loan offer"),
    ("underwriting", "Running underwriting & credit checks"),
    ("verification", "Verifying KYC documents"),
    ("sanction_letter", "Generating your sanction letter"),
]


# ---------- intent parsing ----------

_AMOUNT_RE = re.compile(
    r"(?:rs\.?|inr|₹)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(lakh|lakhs|lac|lacs|l|k|thousand|crore|cr)?",
    re.IGNORECASE,
)
_TENURE_RE = re.compile(r"([0-9]{1,3})\s*(months?|month|mo|years?|yr|yrs)", re.IGNORECASE)
_RATE_RE = re.compile(r"([0-9]{1,2}(?:\.[0-9]{1,2})?)\s*%")


def _normalise_amount(raw: str, unit: Optional[str]) -> float:
    n = float(raw.replace(",", ""))
    u = (unit or "").lower()
    if u in {"k", "thousand"}:
        n *= 1_000
    elif u in {"lakh", "lakhs", "lac", "lacs", "l"}:
        n *= 100_000
    elif u in {"crore", "cr"}:
        n *= 10_000_000
    return n


def extract_loan_intent(
    text: str,
    hint_amount: Optional[float] = None,
    hint_tenure: Optional[int] = None,
    hint_rate: Optional[float] = None,
) -> dict[str, Optional[float]]:
    amount: Optional[float] = hint_amount
    tenure: Optional[int] = hint_tenure
    rate: Optional[float] = hint_rate

    if amount is None:
        # Take the largest matched amount (avoid confusing 36 months with amount).
        candidates: list[float] = []
        for m in _AMOUNT_RE.finditer(text):
            try:
                val = _normalise_amount(m.group(1), m.group(2))
            except ValueError:
                continue
            # Skip pure "36 months" style tokens: those get matched here without units too.
            if m.group(2) is None and val < 10_000:
                continue
            candidates.append(val)
        if candidates:
            amount = max(candidates)

    if tenure is None:
        m = _TENURE_RE.search(text)
        if m:
            n = int(m.group(1))
            unit = m.group(2).lower()
            tenure = n * 12 if unit.startswith("y") else n

    if rate is None:
        m = _RATE_RE.search(text)
        if m:
            rate = float(m.group(1))

    return {"loan_amount": amount, "tenure_months": tenure, "interest_rate": rate}


def missing_fields(intent: dict[str, Any]) -> list[str]:
    missing = []
    if not intent.get("loan_amount"):
        missing.append("loan amount")
    if not intent.get("tenure_months"):
        missing.append("tenure (in months or years)")
    if not intent.get("interest_rate"):
        missing.append("expected interest rate")
    return missing


# ---------- agent invocations (best-effort, defensive) ----------

def sales_agent_reply(message: str) -> str:
    """Ask the existing sales_agent to answer a conversational query."""
    try:
        from loan_agents import sales_agent  # type: ignore

        # Try a few common signatures without touching the module.
        for call in (
            lambda: sales_agent.run(message),
            lambda: sales_agent.run(query=message),
            lambda: sales_agent.answer(message),
        ):
            try:
                out = call()
                if out:
                    return str(out)
            except TypeError:
                continue
    except Exception:  # noqa: BLE001
        pass
    return (
        "I can help you explore personal loans, home loans, and other products. "
        "To start an application, tell me the amount you need, how many months "
        "you'd like to repay over, and the interest rate you're expecting."
    )


def run_orchestrator(customer_id: str, amount: float, tenure: int, rate: float, query: str) -> dict[str, Any]:
    """Import and run the existing orchestrator without modifying it."""
    from orchestartor.orchestrator import LoanOrchestrator  # type: ignore

    orch = LoanOrchestrator()
    return orch.execute(
        customer_id=customer_id,
        loan_amount=amount,
        tenure=tenure,
        interest_rate=rate,
        sales_query=query,
    )


# ---------- SSE stream ----------

def _sse(event: str, data: dict[str, Any]) -> dict[str, str]:
    return {"event": event, "data": json.dumps(data)}


async def _stream_pipeline(
    customer_id: str,
    intent: dict[str, Any],
    message: str,
) -> AsyncIterator[dict[str, str]]:
    yield _sse("assistant", {
        "content": (
            f"Great — starting your loan application for ₹{int(intent['loan_amount']):,} "
            f"over {int(intent['tenure_months'])} months at {intent['interest_rate']}%. "
            "I'll walk you through each step."
        )
    })

    loop = asyncio.get_running_loop()
    task = loop.run_in_executor(
        None,
        run_orchestrator,
        customer_id,
        float(intent["loan_amount"]),
        int(intent["tenure_months"]),
        float(intent["interest_rate"]),
        message,
    )

    # Emit staged progress while the orchestrator runs in a worker thread.
    stage_idx = 0
    started_at = time.monotonic()
    per_stage_seconds = 1.6  # visual pacing only; result is real
    for stage_key, label in STAGE_SEQUENCE:
        yield _sse("stage", {"stage": stage_key, "status": "running", "label": label})
        deadline = started_at + per_stage_seconds * (stage_idx + 1)
        while time.monotonic() < deadline and not task.done():
            await asyncio.sleep(0.15)
        if task.done():
            # Fast-finish remaining stages visually before emitting final result.
            yield _sse("stage", {"stage": stage_key, "status": "success", "label": label})
            for later_key, later_label in STAGE_SEQUENCE[stage_idx + 1 :]:
                yield _sse("stage", {"stage": later_key, "status": "success", "label": later_label})
            break
        yield _sse("stage", {"stage": stage_key, "status": "success", "label": label})
        stage_idx += 1

    try:
        result = await task
    except Exception as exc:  # noqa: BLE001
        yield _sse("error", {
            "stage": "orchestrator",
            "reason": f"Something went wrong running your application: {exc}",
        })
        yield _sse("done", {})
        return

    status_val = str(result.get("status", "")).lower()
    stage_val = str(result.get("stage", ""))
    if status_val in {"rejected", "failed", "error"} or stage_val != "completed":
        yield _sse("error", {
            "stage": stage_val or "unknown",
            "reason": result.get("reason") or "Your application couldn't be approved at this stage.",
            "raw": result,
        })
    else:
        # Best-effort EMI calc for the summary card.
        p = float(intent["loan_amount"])
        n = int(intent["tenure_months"])
        r_monthly = float(intent["interest_rate"]) / 12.0 / 100.0
        try:
            emi = (p * r_monthly * (1 + r_monthly) ** n) / (((1 + r_monthly) ** n) - 1) if r_monthly else p / n
        except ZeroDivisionError:
            emi = p / n

        yield _sse("result", {
            "loan_amount": p,
            "tenure_months": n,
            "interest_rate": float(intent["interest_rate"]),
            "emi": round(emi, 2),
            "underwriting_decision": result.get("underwriting_decision"),
            "kyc_verification": result.get("kyc_verification"),
            "sanction_letter": result.get("sanction_letter"),
        })

    yield _sse("done", {})


@router.post("/chat")
async def chat(
    req: ChatRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> EventSourceResponse:
    if not req.message or not req.message.strip():
        raise HTTPException(400, "message is required")

    intent = extract_loan_intent(
        req.message,
        hint_amount=req.loan_amount,
        hint_tenure=req.tenure_months,
        hint_rate=req.interest_rate,
    )
    missing = missing_fields(intent)

    async def gen() -> AsyncIterator[dict[str, str]]:
        if missing:
            # Conversational path: use sales_agent to reply, plus a nudge for missing fields.
            base_reply = sales_agent_reply(req.message)
            need = ", ".join(missing)
            yield _sse("assistant", {"content": base_reply})
            yield _sse("assistant", {
                "content": f"To move forward with an application I still need: **{need}**.",
            })
            yield _sse("done", {})
            return

        async for evt in _stream_pipeline(user["customer_id"], intent, req.message):
            yield evt

    return EventSourceResponse(gen())
