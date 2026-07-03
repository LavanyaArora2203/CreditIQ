"""
master_orchestrator.py

Coordinates the complete AI Credit Analysis workflow.
"""

from Orchestration.workflow_manager import WorkflowManager
from Orchestration.execution_context import ExecutionContext
from Orchestration.state_machine import (
    StateMachine,
    WorkflowState,
)
from Orchestration.agent_executor import AgentExecutor
from Orchestration.routing import WorkflowRouter

# Existing services from your project
from Services.salary_service import process_customer
from Services.verification_service import verify_customer
from Services.underwriting_service import evaluate_loan
from Services.sanction_letter_service import generate_sanction_letter


class MasterOrchestrator:

    def __init__(self):

        self.workflow = WorkflowManager()

        self.context = ExecutionContext()

        self.state_machine = StateMachine()

        self.executor = AgentExecutor(self.workflow)

    def process_application(
        self,
        customer_id,
        loan_amount,
        annual_interest_rate=10,
        tenure_months=60,
    ):

        try:

            ##################################################
            # SALES
            ##################################################

            self.state_machine.transition(
                WorkflowState.SALES
            )

            sales_result = self.executor.execute(
                stage="SALES",
                agent_function=process_customer,
                customer_id=customer_id,
            )

            self.context.set_sales_result(
                sales_result
            )

            ##################################################
            # VERIFICATION
            ##################################################

            next_state = WorkflowRouter.after_sales()

            self.state_machine.transition(next_state)

            verification_result = self.executor.execute(
                stage="VERIFICATION",
                agent_function=verify_customer,
                customer_id=customer_id,
            )

            self.context.set_verification_result(
                verification_result
            )

            next_state = WorkflowRouter.after_verification(
                verification_result
            )

            if next_state == WorkflowState.FAILED:

                self.workflow.fail(
                    "Verification Failed"
                )

                return self.workflow.summary()

            ##################################################
            # UNDERWRITING
            ##################################################

            self.state_machine.transition(next_state)

            underwriting_result = self.executor.execute(
                stage="UNDERWRITING",
                agent_function=evaluate_loan,
                customer_id=customer_id,
                loan_amount=loan_amount,
                annual_interest_rate=annual_interest_rate,
                tenure_months=tenure_months,
            )

            self.context.set_underwriting_result(
                underwriting_result
            )

            next_state = WorkflowRouter.after_underwriting(
                underwriting_result
            )

            ##################################################
            # REJECTED
            ##################################################

            if next_state == WorkflowState.COMPLETED:

                self.workflow.complete()

                return {
                    "workflow": self.workflow.summary(),
                    "context": self.context.to_dict(),
                }

            ##################################################
            # SANCTION LETTER
            ##################################################

            self.state_machine.transition(next_state)

            sanction_result = self.executor.execute(
                stage="SANCTION",
                agent_function=generate_sanction_letter,
                underwriting_result=underwriting_result,
            )

            self.context.set_sanction_result(
                sanction_result
            )

            ##################################################
            # COMPLETE
            ##################################################

            self.state_machine.transition(
                WorkflowState.COMPLETED
            )

            self.workflow.complete()

            return {
                "workflow": self.workflow.summary(),
                "context": self.context.to_dict(),
            }

        except Exception as e:

            self.workflow.fail(str(e))

            return {
                "workflow": self.workflow.summary(),
                "error": str(e),
            }