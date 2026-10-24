from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.integrations.github_client import ProjectsConnector

PROJECTS_SYSTEM_PROMPT = """
You are the Technical & Project Lead Agent reporting to LUNA (CEO).
You manage software repositories, CI/CD pipelines, issue trackers (Linear/GitHub),
and infrastructure operations.
Review the live Git/CI telemetry and return a crisp engineering debrief.
"""

class ProjectsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Projects & Tech Lead",
            domain="projects",
            system_prompt=PROJECTS_SYSTEM_PROMPT
        )
        self.connector = ProjectsConnector()

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        
        # Query local git & GitHub / CI
        connector_output = await self.connector.execute_directive(instruction)
        output_text = connector_output

        if self.client:
            llm_summary = await self.call_llm(
                f"Live Git & Pipeline Telemetry: '{connector_output}'. "
                f"Founder instruction via LUNA: '{instruction}'. "
                "Provide a crisp engineering operational debrief."
            )
            if llm_summary:
                output_text = f"{connector_output} | {llm_summary}"

        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="projects",
            status="success",
            output=output_text,
            details={"has_github_token": self.connector.has_github}
        )
