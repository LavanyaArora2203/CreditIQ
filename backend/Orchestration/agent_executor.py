"""
agent_executor.py

Executes agents safely with logging and retry support.
"""

import time
import traceback


class AgentExecutor:

    def __init__(self, workflow_manager, max_retries=2):
        self.workflow_manager = workflow_manager
        self.max_retries = max_retries

    def execute(self, stage: str, agent_function, **kwargs):
        """
        Execute an agent function with retries.

        Parameters
        ----------
        stage : str
            Workflow stage name.

        agent_function : callable
            Function that executes the agent.

        kwargs : dict
            Arguments passed to the agent.
        """

        self.workflow_manager.update_stage(stage)

        for attempt in range(1, self.max_retries + 2):

            try:

                print(f"[{stage}] Attempt {attempt}")

                result = agent_function(**kwargs)

                self.workflow_manager.save_result(
                    stage,
                    result
                )

                print(f"[{stage}] Success")

                return result

            except Exception as e:

                print(f"[{stage}] Failed")

                traceback.print_exc()

                if attempt > self.max_retries:

                    self.workflow_manager.fail(str(e))
                    raise

                time.sleep(1)