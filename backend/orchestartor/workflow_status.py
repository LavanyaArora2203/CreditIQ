from enum import Enum


class WorkflowStage(str, Enum):

    CHECKER = "checker"

    SALES = "sales"

    UNDERWRITING = "underwriting"

    VERIFICATION = "verification"

    SANCTION = "sanction"

    COMPLETED = "completed"

    FAILED = "failed"

WORKFLOW = {

    WorkflowStage.CHECKER:
        WorkflowStage.SALES,

    WorkflowStage.SALES:
        WorkflowStage.UNDERWRITING,

    WorkflowStage.UNDERWRITING:
        WorkflowStage.VERIFICATION,

    WorkflowStage.VERIFICATION:
        WorkflowStage.SANCTION,

    WorkflowStage.SANCTION:
        WorkflowStage.COMPLETED
}