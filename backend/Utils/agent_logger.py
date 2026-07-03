from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "Logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "agent_handoff.log"


def log_agent(
    agent_name: str,
    action: str,
    status: str,
    details: str = ""
):
    """
    Logs every agent execution.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = (
        f"{timestamp} | "
        f"{agent_name} | "
        f"{action} | "
        f"{status}"
    )

    if details:
        log_line += f" | {details}"

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_line + "\n")