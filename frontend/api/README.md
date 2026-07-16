# CreditIQ — Loan Assistant API

Thin FastAPI layer around the existing CrewAI orchestrator. Adds JWT auth,
a users store (JSON), and a Server-Sent-Events `/chat` endpoint that
streams pipeline progress to the frontend.

## Files

```
api/
  main.py           # FastAPI app (mount here)
  auth.py           # /auth/signup, /auth/login, /me, JWT deps
  chat_stream.py    # /chat SSE endpoint (calls LoanOrchestrator.execute)
  users_store.py    # data/users.json + customer_data.json lookup
  schemas.py        # pydantic models
  config.py         # env + paths
  requirements.txt
  .env.example
```

**No changes to `loan_agents/` or `orchestartor/`.** This layer imports them.

## Setup

```bash
cd <repo-root>
python -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt

cp api/.env.example api/.env
# Edit api/.env — at minimum set JWT_SECRET to a long random string:
#   python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Run

```bash
# From repo root (so `loan_agents` and `orchestartor` are importable)
uvicorn api.main:app --reload --port 9000
```

The frontend expects `http://localhost:9000` by default. Change with
`VITE_LOAN_API_URL` in the frontend `.env`.

Also make sure the existing FastAPI apps in `APIs/` are running on
`localhost:8000` if your agents depend on them.

## Endpoints

- `POST /auth/signup` — body `{ customer_id, password }`. Only accepts
  customer IDs already present in `data/customer_data.json` (per the
  rule you specified: "if customer_id matches, sign up; otherwise tell
  the user to create a new account with the bank").
- `POST /auth/login` — body `{ customer_id, password }` → JWT.
- `GET /me` — returns the logged-in customer's profile.
- `POST /chat` — body `{ message }`, Bearer JWT required. Responds with
  `text/event-stream`. Event types:
  - `assistant` `{ content }` — conversational text
  - `stage` `{ stage, status: running|success|failed, label }`
  - `result` `{ loan_amount, tenure_months, interest_rate, emi, underwriting_decision, kyc_verification, sanction_letter }`
  - `error` `{ stage, reason }`
  - `done`

The chat endpoint extracts loan intent (amount/tenure/rate) from the
message with regex. If any field is missing, it uses `sales_agent` for
a conversational reply and asks for the missing fields. Once all three
are present, it runs `LoanOrchestrator.execute(...)` in a worker thread
and streams staged progress while it runs, then emits the real final
result.
