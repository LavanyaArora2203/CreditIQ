"""
streamlit_app.py

Frontend for the AI Credit Analysis backend.

WHERE TO PUT THIS FILE
-----------------------
Save this file as: AICreditAnalysis/backend/frontend/streamlit_app.py
(i.e. next to the existing backend/frontend/app.py — this file does not
touch or depend on that file, you can delete/ignore it).

HOW TO RUN
-----------------------
This app talks to the existing "Services" layer of your backend, and
`Services/underwriting_service.py` calls a live HTTP API
(APIs/credit_bureau.py) at http://127.0.0.1:8000. That API is NOT started
automatically — you must run it yourself in a separate terminal first:

    cd AICreditAnalysis/backend
    uvicorn APIs.credit_bureau:app --reload --port 8000

Then, in a second terminal, run this Streamlit app (from the backend/
folder, same as the existing frontend/app.py expects):

    cd AICreditAnalysis/backend
    streamlit run frontend/streamlit_app.py

No new backend logic has been added here — this file only calls
functions that already exist in Services/underwriting_service.py,
Services/chatbot_service.py, Services/sanction_letter_service.py and
Utils/emi_calculator.py.
"""

import os
import sys
from pathlib import Path

import requests
import streamlit as st

# --------------------------------------------------------------------
# Make "Services", "Utils" etc importable, exactly like the existing
# backend/frontend/app.py already does.
# --------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

from backend.Services.underwriting_service import evaluate_loan, CREDIT_API   # noqa: E402
from backend.Services.chatbot_service import generate_response                # noqa: E402
from backend.Services.sanction_letter_service import generate_sanction_letter  # noqa: E402
from backend.Utils.emi_calculator import calculate_emi                        # noqa: E402

LOG_FILE = BACKEND_DIR / "Logs" / "agent_handoff.log"

# --------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------
st.set_page_config(
    page_title="AI Credit Analyst",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 AI Credit Analyst")
st.subheader("Multi-Agent Personal Loan Sanctioning System")
st.divider()

# --------------------------------------------------------------------
# Sidebar: backend / dependency status
# --------------------------------------------------------------------
with st.sidebar:
    st.header("Backend status")

    credit_api_base = CREDIT_API.rsplit("/credit", 1)[0]

    try:
        # Any response (even 404) means the server process is up.
        requests.get(f"{CREDIT_API}/__ping__", timeout=2)
        api_up = True
    except requests.exceptions.RequestException:
        api_up = False

    if api_up:
        st.success(f"Credit Bureau API reachable\n\n{credit_api_base}")
    else:
        st.error(
            "Credit Bureau API not reachable.\n\n"
            "Start it in another terminal:\n\n"
            "```\ncd AICreditAnalysis/backend\n"
            "uvicorn APIs.credit_bureau:app --reload --port 8000\n```"
        )

    st.divider()
    st.caption(
        "Sample customer IDs from Data/customers.json: "
        "CUST001 – CUST010"
    )

# --------------------------------------------------------------------
# Loan application form
# --------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    customer_id = st.text_input("Customer ID", placeholder="Example: CUST002")
    loan_amount = st.number_input(
        "Loan Amount (₹)", min_value=10000, step=10000, value=300000
    )

with col2:
    annual_interest_rate = st.number_input(
        "Annual Interest Rate (%)", min_value=1.0, max_value=36.0,
        value=10.0, step=0.25,
    )
    tenure_months = st.number_input(
        "Tenure (months)", min_value=6, max_value=360, value=60, step=6
    )

evaluate_clicked = st.button("Evaluate Loan", type="primary")

if evaluate_clicked:

    if not customer_id:
        st.warning("Please enter a Customer ID.")

    else:
        with st.spinner("Running Underwriting Agent..."):
            try:
                result = evaluate_loan(
                    customer_id=customer_id,
                    loan_amount=loan_amount,
                    annual_interest_rate=annual_interest_rate,
                    tenure_months=tenure_months,
                )
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not reach the Credit Bureau API at "
                    f"{CREDIT_API}. Make sure it is running "
                    "(see sidebar for the command) and try again."
                )
                result = None

        if result is not None:

            st.divider()
            st.subheader("Loan Decision")

            if result.get("status") == "error":
                st.error(result.get("message", "Something went wrong."))

            else:
                decision = result.get("decision")

                if decision == "APPROVED":
                    st.success(f"Decision: {decision}")
                elif decision == "REJECTED":
                    st.error(f"Decision: {decision}")
                else:
                    st.info(f"Decision: {decision}")

                st.json(result)

                st.divider()
                st.subheader("Assistant")
                st.info(generate_response(result))

                # ----------------------------------------------------
                # Sanction letter (only for approved applications)
                # ----------------------------------------------------
                if decision == "APPROVED":

                    st.divider()
                    st.subheader("Sanction Letter")

                    customer = result.get("customer", {})
                    customer_name = customer.get("Name", customer_id)

                    # emi is only present in the result when salary
                    # verification ran (Rule 2 in evaluate_loan). For a
                    # straight within-limit approval it isn't computed,
                    # so we derive it here using the same utility the
                    # backend already ships with.
                    salary_verification = result.get("salary_verification")
                    if salary_verification:
                        emi = salary_verification["emi"]
                    else:
                        emi = calculate_emi(
                            principal=loan_amount,
                            annual_interest_rate=annual_interest_rate,
                            tenure_months=tenure_months,
                        )

                    try:
                        with st.spinner("Running Sanction Agent..."):
                            letter_result = generate_sanction_letter(
                                customer_name=customer_name,
                                customer_id=customer_id,
                                loan_amount=loan_amount,
                                tenure_months=tenure_months,
                                interest_rate=annual_interest_rate,
                                emi=emi,
                            )

                        pdf_path = letter_result["pdf_path"]

                        # generate_sanction_letter writes to a path
                        # relative to the current working directory.
                        # Resolve robustly regardless of where
                        # Streamlit was launched from.
                        resolved_path = Path(pdf_path)
                        if not resolved_path.exists():
                            resolved_path = BACKEND_DIR / pdf_path

                        if resolved_path.exists():
                            st.success(f"Sanction letter generated: {pdf_path}")
                            with open(resolved_path, "rb") as f:
                                st.download_button(
                                    label="Download Sanction Letter (PDF)",
                                    data=f.read(),
                                    file_name=resolved_path.name,
                                    mime="application/pdf",
                                )
                        else:
                            st.warning(
                                f"Letter reported as generated at '{pdf_path}' "
                                "but the file could not be located."
                            )

                    except Exception as e:
                        st.error(f"Could not generate sanction letter: {e}")

                # ----------------------------------------------------
                # Agent execution log (existing backend logging,
                # just surfaced in the UI)
                # ----------------------------------------------------
                if LOG_FILE.exists():
                    with st.expander("Agent execution log"):
                        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
                        st.code("\n".join(lines[-15:]) or "No log entries yet.")