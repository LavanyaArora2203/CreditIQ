from pydantic import BaseModel
from models.workflow_stage import WorkflowStage


class WorkflowState(BaseModel):

    customer_id: str | None = None

    stage: WorkflowStage = WorkflowStage.SALES

    sales_completed: bool = False

    verification_completed: bool = False

    risk_completed: bool = False

    decision_completed: bool = False