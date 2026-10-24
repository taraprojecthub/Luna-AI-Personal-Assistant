import json
from typing import Dict, Any
from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.config import settings

MARKETING_SYSTEM_PROMPT = """
You are the Head of Growth & Marketing Agent reporting to LUNA (CEO).
You manage social media strategies, audience engagement analytics, campaign schedules,
and promotional copy across platforms (X, LinkedIn, Meta, YouTube).
Deliver high-converting, crisp copy or growth analytics tailored exactly to the Founder's mandate.
"""

class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Marketing & Growth Lead",
            domain="marketing",
            system_prompt=MARKETING_SYSTEM_PROMPT
        )
        self.marketing_state: Dict[str, Any] = {
            "active_campaigns": ["Q4 LUNA Launch Sprint", "Developer Outreach"],
            "recent_metrics": {"impressions_7d": 142000, "click_through_rate": "3.8%", "top_post": "Autonomous Agents Architecture"},
            "scheduled_posts": 4
        }

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        
        prompt = (
            f"Marketing State & Metrics: {json.dumps(self.marketing_state)}\n"
            f"Founder instruction via LUNA: '{instruction}'\n"
            "Produce the requested marketing deliverables or analytical assessment."
        )
        report = await self.call_llm(prompt)
        
        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="marketing",
            status="success",
            output=report or f"Marketing mandate executed: {instruction}",
            details={"marketing_state": self.marketing_state}
        )
