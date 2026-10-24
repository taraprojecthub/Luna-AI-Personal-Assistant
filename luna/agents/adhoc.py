from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult

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

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        prompt = f"Perform this specialized ad-hoc task: '{instruction}'"
        report = await self.call_llm(prompt)
        
        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="adhoc",
            status="success",
            output=report or f"Ad-hoc task completed: {instruction}",
            details={}
        )
