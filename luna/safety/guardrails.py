from typing import Tuple, List
from luna.models.schemas import SubTask

CRITICAL_ACTION_KEYWORDS = [
    "prod deploy",
    "production deployment",
    "drop table",
    "delete database",
    "wipe",
    "rm -rf",
    "unlock front door",
    "unlock door",
    "disarm security",
    "disable alarm",
    "revoke access",
    "spend",
    "transfer money",
    "publish live without review",
]

class SafetyGuardrail:
    """Enforces Founder Sign-Off for critical / destructive actions."""

    @staticmethod
    def assess_risk(subtasks: List[SubTask]) -> Tuple[bool, List[str]]:
        """
        Scans subtasks for high-risk operations.
        Returns (is_risky, list_of_reasons).
        """
        reasons = []
        is_risky = False

        for task in subtasks:
            text = f"{task.instruction} {task.target_domain}".lower()
            if task.is_critical:
                is_risky = True
                reasons.append(f"Task '{task.task_id}' was explicitly marked critical: {task.instruction}")
            
            for keyword in CRITICAL_ACTION_KEYWORDS:
                if keyword in text:
                    task.is_critical = True
                    is_risky = True
                    reasons.append(f"Detected sensitive operation keyword '{keyword}' in task {task.task_id}: {task.instruction}")
                    break

        return is_risky, reasons
