import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Services.underwriting_service import evaluate_loan
from Services.chatbot_service import generate_response
from Services.sanction_letter_service import generate_sanction_letter

st.set_page_config(
    page_title="AI Credit Analyst",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 AI Credit Analyst")
st.subheader("Multi-Agent Personal Loan Sanctioning System")

st.divider()

customer_id = st.text_input(
    "Customer ID",
    placeholder="Example: CUST002"
)

loan_amount = st.number_input(
    "Loan Amount (₹)",
    min_value=10000,
    step=10000
)

if st.button("Evaluate Loan"):

    if not customer_id:

        st.warning("Please enter Customer ID.")

    else:

        with st.spinner("Running AI Agents..."):

            result = evaluate_loan(
                customer_id=customer_id,
                loan_amount=loan_amount
            )

        st.divider()

        st.subheader("Loan Decision")

        st.json(result)

        st.divider()

        st.subheader("Assistant")

        st.success(generate_response(result))

        if result.get("decision") == "APPROVED":

            st.divider()

            st.subheader("Sanction Letter")

            letter = generate_sanction_letter(result)

            st.code(letter)