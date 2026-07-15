"""
test.py — sanity-checks the whole multi-agent loan system before you move
on to frontend work.

Run from the project root, with your venv active:

    python test.py            # structural checks only (safe, no API calls)
    python test.py --live      # also runs one real end-to-end pipeline call
                                # (needs OPENAI_API_KEY, costs real tokens)

It does NOT stop at the first failure — it runs every check and prints a
PASS/FAIL summary at the end so you can see everything that's broken in
one pass instead of fixing errors one at a time.
"""

import sys
import json
import importlib
from pathlib import Path

results = []  # (check_name, passed: bool, detail: str)


def check(name):
    """Decorator: runs fn(), records PASS/FAIL, never raises."""
    def wrapper(fn):
        try:
            detail = fn() or "ok"
            results.append((name, True, detail))
        except Exception as e:
            results.append((name, False, f"{type(e).__name__}: {e}"))
    return wrapper


ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 1. Environment
# ---------------------------------------------------------------------------
@check("Python version >= 3.12")
def _():
    v = sys.version_info
    assert (v.major, v.minor) >= (3, 12), f"found {v.major}.{v.minor}"
    return f"{v.major}.{v.minor}.{v.micro}"


@check("Running from project root")
def _():
    assert (ROOT / "pyproject.toml").exists(), "pyproject.toml not found next to test.py"
    return str(ROOT)


@check("OPENAI_API_KEY is set")
def _():
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    key = os.environ.get("OPENAI_API_KEY")
    assert key, "not set — add it to a .env file or export it in your shell"
    return "set (value hidden)"


# ---------------------------------------------------------------------------
# 2. Data files
# ---------------------------------------------------------------------------
for fname in ["customer_data.json", "kyc_data.json", "offers.json"]:
    @check(f"data/{fname} parses as JSON")
    def _(fname=fname):
        with open(ROOT / "data" / fname, encoding="utf-8") as f:
            data = json.load(f)
        return f"loaded ({len(json.dumps(data))} bytes)"

for fname in ["company_policies.txt", "bank_info.txt"]:
    @check(f"data/{fname} exists")
    def _(fname=fname):
        p = ROOT / "data" / fname
        assert p.exists(), "missing"
        return f"{p.stat().st_size} bytes"


# ---------------------------------------------------------------------------
# 3. Core imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(ROOT))

CORE_MODULES = [
    "tools.SearchCustomerTool",
    "tools.CreateCustomerTool",
    "tools.KYCRetrivalTool",
    "tools.KYCVerificationTool",
    "tools.PolicyRetrivalTool",
    "tools.credit_bureau_tool",
    "tools.emi_cal_tool",
    "tools.SanctionLetterTool",
    "models.input.sales_input",
    "models.input.underwriting_input",
    "models.input.verification_input",
    "models.input.sanction_input",
    "models.output.sales_output",
    "models.output.underwriting_output",
    "models.output.verification_output",
    "models.output.sanction_output",
    "orchestartor.workflow_status",
    "orchestartor.exceptions",
    "orchestartor.logger",
    "orchestartor.utils",
    "orchestartor.worflow_state",
]

for mod in CORE_MODULES:
    @check(f"import {mod}")
    def _(mod=mod):
        importlib.import_module(mod)
        return "imported"


# ---------------------------------------------------------------------------
# 4. Tool instantiation (catches missing BaseTool imports / untyped fields)
# ---------------------------------------------------------------------------
TOOL_CLASSES = [
    ("tools.SearchCustomerTool", "SearchCustomerTool"),
    ("tools.CreateCustomerTool", "CreateCustomerTool"),
    ("tools.KYCRetrivalTool", "KYCRetrievalTool"),
    ("tools.KYCVerificationTool", "KYCVerificationTool"),
    ("tools.PolicyRetrivalTool", "PolicyRetrieverTool"),
    ("tools.credit_bureau_tool", "CreditBureauTool"),
    ("tools.emi_cal_tool", "EMICalculatorTool"),
]

for mod_name, cls_name in TOOL_CLASSES:
    @check(f"instantiate {cls_name}")
    def _(mod_name=mod_name, cls_name=cls_name):
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        cls()
        return "instantiated"


@check("instantiate SanctionLetterTool (needs weasyprint)")
def _():
    from tools.SanctionLetterTool import SanctionLetterTool
    SanctionLetterTool()
    return "instantiated"


# ---------------------------------------------------------------------------
# 5. Agent modules — importing these builds Agent/Task/Crew objects.
#    This is also where gap #5 (module-level input()/kickoff() blocking
#    on import) would show up again if it ever regressed, since a hang or
#    an unwanted API call here means an agent file broke the import-safety
#    fix.
# ---------------------------------------------------------------------------
AGENT_MODULES = [
    "loan_agents.checker_agent",
    "loan_agents.sales_agent",
    "loan_agents.underwritting_agent",
    "loan_agents.verification_agent",
    "loan_agents.sanction_letter_agent",
]

for mod in AGENT_MODULES:
    @check(f"import {mod} (builds Agent/Task/Crew, no LLM call)")
    def _(mod=mod):
        m = importlib.import_module(mod)
        assert hasattr(m, "run"), "module has no run() function"
        assert hasattr(m, "crew"), "module has no crew object"
        return "Agent/Task/Crew built, run() present"


@check("import orchestartor.orchestrator + build LoanOrchestrator")
def _():
    from orchestartor.orchestrator import LoanOrchestrator
    LoanOrchestrator()
    return "LoanOrchestrator built"


# ---------------------------------------------------------------------------
# 6. Print results
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("STRUCTURAL CHECKS")
print("=" * 72)

passed = sum(1 for _, ok, _ in results if ok)
failed = [r for r in results if not r[1]]

for name, ok, detail in results:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name:<55} {detail}")

print("-" * 72)
print(f"{passed}/{len(results)} checks passed")

if failed:
    print(f"\n{len(failed)} check(s) failed — fix these before moving to frontend work:")
    for name, _, detail in failed:
        print(f"  - {name}: {detail}")


# ---------------------------------------------------------------------------
# 7. Optional live end-to-end run
# ---------------------------------------------------------------------------
if "--live" in sys.argv:
    print("\n" + "=" * 72)
    print("LIVE END-TO-END RUN (real LLM calls, real API cost)")
    print("=" * 72)

    if failed:
        print("Skipping live run — fix the structural failures above first.")
    else:
        from orchestartor.orchestrator import LoanOrchestrator

        orchestrator = LoanOrchestrator()
        try:
            result = orchestrator.execute(
                customer_id="CUST001",
                loan_amount=200000,
                tenure=36,
                interest_rate=11.5,
                sales_query="What is the minimum and maximum personal loan amount?",
            )
            print("\nPipeline result:")
            print(json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"\nLive run failed: {type(e).__name__}: {e}")
else:
    print("\nTip: run `python test.py --live` to also execute one real "
          "end-to-end pipeline call through the LLM (uses your OPENAI_API_KEY).")

print("=" * 72)

sys.exit(0 if not failed else 1)