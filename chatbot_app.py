"""
chatbot_app.py

A Streamlit chat interface for the AI Credit Analysis multi-agent system.

The user only ever talks to the Master Agent. Behind the scenes, the
Master Agent (using the OpenAI Agents SDK) routes the conversation to
whichever specialist agent is needed - Sales, Verification,
Underwriting, or Sanction - exactly per loan_agents/master_agent.py.

Run with:
    streamlit run chatbot_app.py
"""

import os
import sys
import time
import json
import threading
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------
# Make sure the project root is importable (Services, Utils, loan_agents, ...)
# --------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

st.set_page_config(
    page_title="AI Credit Analyst",
    page_icon="🏦",
    layout="wide",
)

# --------------------------------------------------------------------
# Sidebar - API key
# --------------------------------------------------------------------

with st.sidebar:
    st.title("🏦 AI Credit Analyst")
    st.caption("Multi-Agent Personal Loan Sanctioning System")
    st.divider()

    st.subheader("🔑 OpenAI API Key")

    env_key = "XXXXX"
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=env_key,
        type="password",
        placeholder="sk-...",
        label_visibility="collapsed",
        help="Required to run the agents. Stored only for this session.",
    )

    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    api_key_ready = bool(os.environ.get("OPENAI_API_KEY"))

    if api_key_ready:
        st.success("API key set")
    else:
        st.warning("Enter your OpenAI API key to start chatting.")

# --------------------------------------------------------------------
# Start the mock backend APIs (OfferMart / CRM / Credit Bureau) once,
# in a background thread, on port 8000 - exactly where the existing
# tools/services already expect to find them.
# --------------------------------------------------------------------


@st.cache_resource(show_spinner=False)
def start_mock_backend():
    import uvicorn
    from backend.APIs.offer_mart import app as mock_app

    config = uvicorn.Config(
        mock_app,
        host="127.0.0.1",
        port=8000,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Give uvicorn a moment to boot before the first tool call hits it.
    time.sleep(1.2)
    return True


start_mock_backend()

# --------------------------------------------------------------------
# Import agents (after sys.path is set up)
# --------------------------------------------------------------------

from agents import Runner  # noqa: E402
from agents.items import (  # noqa: E402
    MessageOutputItem,
    HandoffCallItem,
    HandoffOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
)
from agents import ItemHelpers  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from backend.loan_agents.master_agent import master_agent  # noqa: E402

# --------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []  # what's shown in the chat window

if "agent_input_list" not in st.session_state:
    st.session_state.agent_input_list = []  # full conversation state for the SDK

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []  # backend agent/tool activity, per turn

if "current_agent_name" not in st.session_state:
    st.session_state.current_agent_name = master_agent.name

if "known_pdfs" not in st.session_state:
    st.session_state.known_pdfs = set()

GENERATED_LETTERS_DIR = ROOT_DIR / "GeneratedLetters"
GENERATED_LETTERS_DIR.mkdir(exist_ok=True)
for p in GENERATED_LETTERS_DIR.glob("*.pdf"):
    st.session_state.known_pdfs.add(p.name)


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

STAGE_ICONS = {
    "MasterAgent": "🧭",
    "Sales Agent": "💼",
    "VerificationAgent": "🪪",
    "UnderwritingAgent": "📊",
    "Sanction Agent": "📄",
}

WORKFLOW_STAGES = [
    ("MasterAgent", "Routing"),
    ("Sales Agent", "Sales"),
    ("VerificationAgent", "Verification"),
    ("UnderwritingAgent", "Underwriting"),
    ("Sanction Agent", "Sanction"),
]


def format_final_output(final_output) -> str:
    """Turn the agent's final output (plain text or a pydantic model) into markdown."""

    if isinstance(final_output, BaseModel):
        data = final_output.model_dump()
        lines = [f"**{type(final_output).__name__}**", ""]
        for key, value in data.items():
            pretty_key = key.replace("_", " ").title()
            lines.append(f"- **{pretty_key}:** {value}")
        return "\n".join(lines)

    if isinstance(final_output, dict):
        return "```json\n" + json.dumps(final_output, indent=2, default=str) + "\n```"

    return str(final_output)


def describe_item(item) -> str:
    """One-line human readable description of an SDK run item, for the activity log."""

    agent_name = getattr(item.agent, "name", "Agent")

    try:
        if isinstance(item, HandoffCallItem):
            return f"🔀 **{agent_name}** requested a handoff"

        if isinstance(item, HandoffOutputItem):
            source = getattr(getattr(item, "source_agent", None), "name", agent_name)
            target = getattr(getattr(item, "target_agent", None), "name", "next agent")
            return f"➡️ Handoff: **{source}** → **{target}**"

        if isinstance(item, ToolCallItem):
            tool_name = getattr(item, "tool_name", "tool")
            return f"🔧 **{agent_name}** called tool `{tool_name}`"

        if isinstance(item, ToolCallOutputItem):
            output = getattr(item, "output", None)
            if output is None:
                output = getattr(item, "custom_data", "")
            preview = str(output)
            if len(preview) > 220:
                preview = preview[:220] + "…"
            return f"✅ **{agent_name}** received tool result: `{preview}`"

        if isinstance(item, MessageOutputItem):
            text = ItemHelpers.text_message_output(item)
            preview = text.strip().replace("\n", " ")
            if len(preview) > 160:
                preview = preview[:160] + "…"
            return f"💬 **{agent_name}**: {preview}"

    except Exception:
        pass

    return f"• **{agent_name}** — {getattr(item, 'type', 'event')}"


def run_turn(user_text: str):
    """Send one user message through the Master Agent (and whichever specialist it routes to)."""

    pending_input = st.session_state.agent_input_list + [
        {"role": "user", "content": user_text}
    ]

    try:
        result = Runner.run_sync(
            starting_agent=master_agent,
            input=pending_input,
        )
    except Exception as e:
        # Don't corrupt the conversation state - just surface the error in chat.
        st.session_state.chat_messages.append({"role": "user", "content": user_text})
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": f"⚠️ Something went wrong while processing that: {e}",
                "agent": st.session_state.current_agent_name,
            }
        )
        return

    st.session_state.agent_input_list = result.to_input_list()
    st.session_state.current_agent_name = result.last_agent.name

    turn_log = [describe_item(item) for item in result.new_items]
    st.session_state.activity_log.append(
        {"turn": len(st.session_state.chat_messages) // 2 + 1, "events": turn_log}
    )

    assistant_text = format_final_output(result.final_output)

    st.session_state.chat_messages.append({"role": "user", "content": user_text})
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": assistant_text,
            "agent": result.last_agent.name,
        }
    )


# --------------------------------------------------------------------
# Sidebar - workflow status & activity log
# --------------------------------------------------------------------

with st.sidebar:
    st.divider()
    st.subheader("📍 Workflow Stage")

    current = st.session_state.current_agent_name
    for name, label in WORKFLOW_STAGES:
        icon = STAGE_ICONS.get(name, "•")
        if name == current:
            st.markdown(f"**{icon} {label} ← current**")
        else:
            st.markdown(f"{icon} {label}")

    st.divider()
    st.subheader("🗂️ Try a demo customer")
    st.caption("CUST001 – CUST010 exist in the mock CRM / Credit Bureau data.")

    st.divider()
    st.subheader("🛠️ Agent Activity Log")

    if not st.session_state.activity_log:
        st.caption("No activity yet — send a message to get started.")
    else:
        for entry in reversed(st.session_state.activity_log):
            with st.expander(f"Turn {entry['turn']}", expanded=False):
                if not entry["events"]:
                    st.caption("No tool calls or handoffs this turn.")
                for line in entry["events"]:
                    st.markdown(line)

    st.divider()

    if GENERATED_LETTERS_DIR.exists():
        pdfs = sorted(GENERATED_LETTERS_DIR.glob("*.pdf"))
        if pdfs:
            st.subheader("📄 Sanction Letters")
            for pdf in pdfs:
                with open(pdf, "rb") as f:
                    st.download_button(
                        label=f"Download {pdf.name}",
                        data=f.read(),
                        file_name=pdf.name,
                        mime="application/pdf",
                        key=f"dl_{pdf.name}",
                    )

    st.divider()
    if st.button("🔄 Reset conversation"):
        st.session_state.chat_messages = []
        st.session_state.agent_input_list = []
        st.session_state.activity_log = []
        st.session_state.current_agent_name = master_agent.name
        st.rerun()

# --------------------------------------------------------------------
# Main chat window
# --------------------------------------------------------------------

st.title("🏦 AI Credit Analyst")
st.caption(
    "Chat with the Master Agent — it will route your request to the right "
    "specialist (Sales → Verification → Underwriting → Sanction) behind the scenes."
)

if not st.session_state.chat_messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hi! I'm your AI loan assistant. Tell me your **Customer ID** "
            "(e.g. `CUST002`) and how much you'd like to borrow, and I'll take "
            "it from there."
        )

for msg in st.session_state.chat_messages:
    role = msg["role"]
    with st.chat_message(role):
        if role == "assistant" and msg.get("agent"):
            icon = STAGE_ICONS.get(msg["agent"], "🤖")
            st.caption(f"{icon} {msg['agent']}")
        st.markdown(msg["content"])

user_prompt = st.chat_input(
    "Type your message..." if api_key_ready else "Enter your OpenAI API key in the sidebar first",
    disabled=not api_key_ready,
)

if user_prompt:
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agents are working on it..."):
            run_turn(user_prompt)
            latest = st.session_state.chat_messages[-1]
            icon = STAGE_ICONS.get(latest["agent"], "🤖")
            st.caption(f"{icon} {latest['agent']}")
            st.markdown(latest["content"])

    st.rerun()
