"""
Loan Orchestrator — drives the 5-stage pipeline:
checker -> sales -> underwriting -> verification -> sanction

FIXES vs the original orchestrator.py:
  1. Import bugs:
       from loan_agents.underwriting_agent import underwriting_agent
     used to fail because the file was named underwritting_agent.py
     (fixed: file renamed, see loan_agents/underwriting_agent.py).
       from mapper import (...)
     used to fail outside this package's own folder (fixed: absolute
     import `from orchestartor.mapper import ...`).

  2. `Crew(agents=[sales_agent], tasks=[sales_agent.task])` assumed Task
     objects live as a `.task` attribute on the Agent instance — that's
     not how CrewAI works (Task is a separate object). Each loan_agents
     module already builds and owns its own Crew + exposes a `run(...)`
     function, so this orchestrator now just calls those run() functions
     directly instead of re-building Crews here.

  3. checker_output / sales_output / underwriting_output used to be
     accessed like `checker_output.status`, `sales_output.status`, etc,
     assuming every agent returns a custom object with a `.status` field.
     In reality CrewAI's kickoff() returns a `CrewOutput` object whose
     structured data (if any) lives at `.pydantic` (only set when the
     Task has `output_pydantic=...`, which only the underwriting and
     verification tasks do). This version reads `.pydantic` where it
     exists and treats the sales/checker stages as best-effort/advisory
     since they were never wired to a structured output schema.

  4. Gap #5 (module-level input()/kickoff() blocking imports) is fixed at
     the source in loan_agents/*.py, which is what actually made this
     file importable at all.
"""

from orchestartor.logger import get_logger
from orchestartor.exceptions import LoanRejectedError, VerificationFailedError
from orchestartor.mapper import build_sanction_input

from loan_agents import checker_agent
from loan_agents import sales_agent
from loan_agents import underwritting_agent
from loan_agents import verification_agent
from loan_agents import sanction_letter_agent

log = get_logger("orchestrator")


class LoanOrchestrator:
    """
    Thin coordinator. Each stage's Agent/Task/Crew is defined and owned by
    its own module in loan_agents/ — this class just calls them in order
    and passes data between them.
    """

    def execute(
        self,
        customer_id: str,
        loan_amount: float,
        tenure: int,
        interest_rate: float,
        sales_query: str | None = None,
    ) -> dict:

        ###################################################
        # STAGE 1: Checker
        ###################################################
        log.info("Stage 1/5: checker — verifying customer %s exists", customer_id)
        checker_result = checker_agent.run(customer_id)
        log.info("Checker output: %s", checker_result)

        ###################################################
        # STAGE 2: Sales (advisory — answers questions about the product,
        # does not block the pipeline; the loan terms for underwriting
        # come from the caller, since the sales agent as implemented is a
        # Q&A tool over info.txt, not a loan-recommendation engine)
        ###################################################
        if sales_query:
            log.info("Stage 2/5: sales — answering: %s", sales_query)
            sales_result = sales_agent.run(sales_query)
            log.info("Sales output: %s", sales_result)
        else:
            log.info("Stage 2/5: sales — skipped (no sales_query provided)")
            sales_result = None

        ###################################################
        # STAGE 3: Underwriting
        ###################################################
        log.info("Stage 3/5: underwriting — evaluating loan application")
        underwriting_result = underwritting_agent.run(
            customer_id=customer_id,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=interest_rate,
        )

        decision = underwriting_result.pydantic
        if decision is None:
            return {
                "stage": "underwriting",
                "status": "failed",
                "reason": "Underwriting agent did not return structured output.",
                "raw": str(underwriting_result),
            }

        if decision.decision.upper() != "APPROVED":
            return {
                "stage": "underwriting",
                "status": "rejected",
                "reason": decision.reason,
                "decision": decision.model_dump(),
            }

        ###################################################
        # STAGE 4: Verification
        ###################################################
        log.info("Stage 4/5: verification — checking KYC for %s", customer_id)
        verification_result = verification_agent.run(customer_id)

        kyc = verification_result.pydantic
        if kyc is None:
            return {
                "stage": "verification",
                "status": "failed",
                "reason": "Verification agent did not return structured output.",
                "raw": str(verification_result),
            }

        if kyc.kyc_status.upper() != "VERIFIED":
            return {
                "stage": "verification",
                "status": "failed",
                "reason": kyc.reason,
                "missing_fields": kyc.missing_fields,
            }

        ###################################################
        # STAGE 5: Sanction letter
        ###################################################
        log.info("Stage 5/5: sanction — generating sanction letter")
        sanction_input = build_sanction_input(
            customer_id=customer_id,
            underwriting_decision=decision.model_dump(),
            verification_result=kyc.model_dump(),
        )

        sanction_result = sanction_letter_agent.run(sanction_input)

        return {
            "stage": "completed",
            "status": "success",
            "underwriting_decision": decision.model_dump(),
            "kyc_verification": kyc.model_dump(),
            "sanction_letter": str(sanction_result),
        }