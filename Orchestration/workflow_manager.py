"""
workflow_manager.py

Maintains the execution state of the loan processing workflow.
"""

from datetime import datetime


class WorkflowManager:
    def __init__(self):
        self.current_stage = "INITIALIZED"
        self.status = "RUNNING"

        # Stores outputs from each stage
        self.results = {}

        # Stores execution logs
        self.history = []

    def update_stage(self, stage: str):
        """Update the current workflow stage."""
        self.current_stage = stage

        self.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stage": stage
        })

    def save_result(self, stage: str, result):
        """Save output of an agent."""
        self.results[stage] = result

    def get_result(self, stage: str):
        """Retrieve output of a completed stage."""
        return self.results.get(stage)

    def fail(self, reason: str):
        """Mark workflow as failed."""
        self.status = "FAILED"

        self.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stage": "FAILED",
            "reason": reason
        })

    def complete(self):
        """Mark workflow as completed."""
        self.status = "COMPLETED"

        self.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stage": "COMPLETED"
        })

    def summary(self):
        """Return workflow summary."""
        return {
            "status": self.status,
            "current_stage": self.current_stage,
            "results": self.results,
            "history": self.history
        }