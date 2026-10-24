from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from luna.models.schemas import CEODecision, SubTaskResult, CEOFinalReport

class AuditLogEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: str
    message: str
    data: Optional[Dict[str, Any]] = None

class LunaGlobalState(BaseModel):
    founder_input: str
    active_plan: Optional[CEODecision] = None
    domain_results: Dict[str, SubTaskResult] = Field(default_factory=dict)
    ceo_final_report: Optional[CEOFinalReport] = None
    audit_logs: List[AuditLogEntry] = Field(default_factory=list)

    def log(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        self.audit_logs.append(AuditLogEntry(
            event_type=event_type,
            message=message,
            data=data
        ))
