from enum import Enum


class WorkflowStage(str, Enum):
    SALES = "sales"
    VERIFICATION = "verification"
    RISK = "risk"
    DECISION = "decision"
    COMPLETED = "completed"