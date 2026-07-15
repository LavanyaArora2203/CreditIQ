"""
Shared logger for the loan workflow (was an empty 0-byte file originally).

Usage:
    from orchestartor.logger import get_logger
    log = get_logger(__name__)
    log.info("stage started")
"""

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "loan_workflow") -> logging.Logger:
    global _CONFIGURED

    if not _CONFIGURED:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            stream=sys.stdout,
        )
        _CONFIGURED = True

    return logging.getLogger(name)