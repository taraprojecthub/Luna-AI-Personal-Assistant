from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

DomainType = Literal["smart_home", "projects", "marketing", "adhoc", "assistant", "system_control"]

class SubTask(BaseModel):
    task_id: str = Field(description="Unique identifier for the subtask, e.g. task_1")
    target_domain: DomainType = Field(description="Target specialist domain: smart_home, projects, marketing, or adhoc")
    instruction: str = Field(description="Specific actionable instruction for the domain specialist agent")
    expected_output: str = Field(default="", description="What the CEO expects to see returned")
    dependencies: List[str] = Field(default_factory=list, description="IDs of subtasks that must be completed before this one")
    is_critical: bool = Field(default=False, description="Whether this task involves destructive or high-risk actions")

class CEODecision(BaseModel):
    acknowledgement_to_founder: str = Field(
        description="Crisp executive acknowledgement to the Founder outlining understanding of the command"
    )
    subtasks: List[SubTask] = Field(
        default_factory=list,
        description="Decomposed list of domain-specific subtasks to execute"
    )
    requires_confirmation: bool = Field(
        default=False,
        description="True if any subtask involves critical risk (prod deployment, unlocking doors, financial changes, deletion)"
    )
    confirmation_reason: Optional[str] = Field(
        default=None,
        description="Clear explanation of what needs confirmation and why"
    )

class SubTaskResult(BaseModel):
    task_id: str
    target_domain: DomainType
    status: Literal["success", "failed", "requires_action", "skipped"]
    output: str
    details: Dict[str, Any] = Field(default_factory=dict)

class CEOFinalReport(BaseModel):
    executive_summary: str = Field(description="Executive briefing for the Founder summarizing all executed operations")
    highlights: List[str] = Field(default_factory=list, description="Key accomplishments and data points")
    pending_items: List[str] = Field(default_factory=list, description="Any items requiring attention, confirmation, or next steps")
    proactive_advice: Optional[str] = Field(default=None, description="Strategic recommendation from LUNA as CEO")
