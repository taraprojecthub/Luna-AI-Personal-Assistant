from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.integrations.web_research import WebResearchConnector

ADHOC_SYSTEM_PROMPT = """
You are an On-Demand Ad-Hoc Specialist Agent dynamically spawned by LUNA (CEO).
You perform specialized research, data synthesis, rapid script generation, or exploratory analysis.
Provide a clear, fact-based output addressing the task directly.
"""

class AdHocAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Ad-Hoc Spawner",
            domain="adhoc",
            system_prompt=ADHOC_SYSTEM_PROMPT
        )
        self.researcher = WebResearchConnector()

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        
        # Execute web research
        connector_output = await self.researcher.execute_directive(instruction)
        output_text = connector_output

        if self.client:
            llm_summary = await self.call_llm(
                f"Web Research Findings:\n{connector_output}\n"
                f"Directive: '{instruction}'\n"
                "Synthesize the key points into a crisp 2-paragraph brief."
            )
            if llm_summary:
                output_text = f"{connector_output}\nSynthesis: {llm_summary}"

        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="adhoc",
            status="success",
            output=output_text,
            details={}
        )
