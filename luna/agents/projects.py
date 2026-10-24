import json
from typing import Dict, Any
from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.config import settings

PROJECTS_SYSTEM_PROMPT = """
You are the Technical & Project Lead Agent reporting to LUNA (CEO).
You manage software repositories, CI/CD pipelines, issue trackers (Linear/Jira/GitHub),
and infrastructure operations (Docker/VPS/Cloud).
Analyze the instruction, execute the necessary checks or operations,
and return a precise, senior-engineering debrief of the results and status.
"""

class ProjectsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Projects & Tech Lead",
            domain="projects",
            system_prompt=PROJECTS_SYSTEM_PROMPT
        )
        self.repo_state: Dict[str, Any] = {
            "active_repos": ["luna-core", "frontend-dashboard", "api-gateway"],
            "ci_pipeline": {"build": "passing", "coverage": "94%", "last_deploy": "v1.4.2"},
            "open_tickets": [
                {"id": "ENG-101", "title": "Implement WebSockets for LUNA streaming", "status": "in_progress"},
                {"id": "ENG-102", "title": "Add OAuth2 integration for social platforms", "status": "todo"}
            ]
        }

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        
        prompt = (
            f"Active Project Environment: {json.dumps(self.repo_state)}\n"
            f"Founder instruction via LUNA: '{instruction}'\n"
            "Provide a concise, technical operational summary of the action taken or findings."
        )
        report = await self.call_llm(prompt)
        
        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="projects",
            status="success",
            output=report or f"Project operation completed: {instruction}",
            details={"project_env": self.repo_state}
        )
