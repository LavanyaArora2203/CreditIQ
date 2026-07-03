"""
state_machine.py

Controls valid workflow state transitions for the
AI Credit Analysis System.
"""

from enum import Enum


class WorkflowState(Enum):
    INITIALIZED = "INITIALIZED"
    SALES = "SALES"
    VERIFICATION = "VERIFICATION"
    UNDERWRITING = "UNDERWRITING"
    SANCTION = "SANCTION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class StateMachine:

    VALID_TRANSITIONS = {

        WorkflowState.INITIALIZED: [
            WorkflowState.SALES,
            WorkflowState.FAILED
        ],

        WorkflowState.SALES: [
            WorkflowState.VERIFICATION,
            WorkflowState.FAILED
        ],

        WorkflowState.VERIFICATION: [
            WorkflowState.UNDERWRITING,
            WorkflowState.FAILED
        ],

        WorkflowState.UNDERWRITING: [
            WorkflowState.SANCTION,
            WorkflowState.FAILED
        ],

        WorkflowState.SANCTION: [
            WorkflowState.COMPLETED,
            WorkflowState.FAILED
        ],

        WorkflowState.COMPLETED: [],

        WorkflowState.FAILED: []
    }

    def __init__(self):
        self.current_state = WorkflowState.INITIALIZED

    def transition(self, next_state: WorkflowState):

        allowed = self.VALID_TRANSITIONS[self.current_state]

        if next_state not in allowed:
            raise ValueError(
                f"Invalid transition: "
                f"{self.current_state.value} -> {next_state.value}"
            )

        self.current_state = next_state

    def get_state(self):
        return self.current_state

    def reset(self):
        self.current_state = WorkflowState.INITIALIZED