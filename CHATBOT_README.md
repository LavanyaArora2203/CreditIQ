# AI Credit Analyst — Chatbot UI

`chatbot_app.py` is a Streamlit chat interface for the existing multi-agent
backend. The user only ever talks to the **Master Agent**; behind the scenes
the Master Agent hands off the conversation to the right specialist —
**Sales → Verification → Underwriting → Sanction** — exactly per
`loan_agents/master_agent.py`, using the OpenAI Agents SDK's handoff
mechanism and each specialist's tools.

## What this adds on top of the original backend

The backend code was almost ready to power a chat UI, but a few gaps had to
be closed to make the full flow actually run:

1. **Mock APIs consolidated** (`APIs/mock_server.py`): OfferMart, CRM, and
   Credit Bureau were three separate FastAPI apps meant for three different
   ports, but every tool/service in the code already hard-codes
   `127.0.0.1:8000`. This file merges all three into one app served on
   port 8000, started automatically in a background thread when you launch
   the Streamlit app — no need to run `uvicorn` manually.
2. **Underwriting agent had no tool** — it couldn't fetch credit score,
   salary, or the pre-approved limit. Added `evaluate_loan_tool`, wrapping
   the existing `Services/underwriting_service.evaluate_loan` rules engine.
3. **Sanction letter tool schema bug** — it accepted a bare `customer: dict`,
   which the current OpenAI Agents SDK's strict-schema mode rejects. Replaced
   it with a small `CustomerInfo` Pydantic model (`customer_id`, `name`).
4. **Missing `name` field** — the Credit Bureau endpoint didn't return the
   customer's name, so the Sanction Agent could never actually build a
   letter. Added `name` to the `/credit/{customer_id}` response.

The original `frontend/app.py` (a form-based, non-chat UI) is untouched and
ignored, per your request.

## Running it

```bash
pip install -r requirements.txt
streamlit run chatbot_app.py
```

Then paste your OpenAI API key into the sidebar. The mock backend APIs start
automatically — you don't need to run anything else.

Try demo customer IDs `CUST001`–`CUST010` (see `Data/customers.json`,
`Data/kyc.json`, `Data/offers.json`).

## What you'll see in the UI

- **Chat window** — the actual conversation with the Master Agent.
- **Workflow Stage** (sidebar) — which agent currently owns the conversation.
- **Agent Activity Log** (sidebar) — per-turn trace of handoffs and tool
  calls happening in the backend, so the multi-agent process isn't a black
  box.
- **Sanction Letters** (sidebar) — download button appears once a PDF has
  been generated in `GeneratedLetters/`.

## A known nuance worth knowing

`Sales Agent` and `VerificationAgent` are configured with a strict
`output_type` (`SalesOutput` / `VerificationOutput` Pydantic models with
required fields). That means every one of their responses — including
follow-up questions like "what's your Customer ID?" — is forced into that
structured schema rather than free-form text (the chatbot renders it as a
small field-by-field card, using the `remarks` field for anything
conversational). This is how the original prompts/models were designed; if
you'd like these two stages to feel more like free-flowing chat, the fix is
to make more of their model fields `Optional` so the agent can respond
before every field is known.
