from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.integrations.social_client import SocialMarketingConnector

MARKETING_SYSTEM_PROMPT = """
You are the Head of Growth & Marketing Agent reporting to LUNA (CEO).
You manage social media strategies, audience engagement analytics, campaign schedules,
and promotional copy across platforms.
Review the marketing telemetry/copy draft and return high-impact output.
"""

class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Marketing & Growth Lead",
            domain="marketing",
            system_prompt=MARKETING_SYSTEM_PROMPT
        )
        self.connector = SocialMarketingConnector()

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        
        # Execute via marketing connector
        connector_output = await self.connector.execute_directive(instruction)
        output_text = connector_output

        if self.client:
            llm_summary = await self.call_llm(
                f"Marketing Telemetry & Draft: '{connector_output}'. "
                f"Founder instruction via LUNA: '{instruction}'. "
                "Refine this into a high-converting growth output."
            )
            if llm_summary:
                output_text = f"{connector_output}\nRefinement: {llm_summary}"

        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="marketing",
            status="success",
            output=output_text,
            details={"has_live_twitter": self.connector.has_live_twitter}
        )
