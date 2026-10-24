from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.integrations.home_assistant import HomeAssistantClient

SMART_HOME_SYSTEM_PROMPT = """
You are the Smart Home Specialist Agent reporting to LUNA (CEO).
You manage IoT hardware, lighting scenes, thermostats, ambient sensors, and physical perimeter security.
Interpret the telemetry and action taken by the Home Assistant connector, and produce a concise status update.
"""

class SmartHomeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SmartHome Specialist",
            domain="smart_home",
            system_prompt=SMART_HOME_SYSTEM_PROMPT
        )
        self.ha_client = HomeAssistantClient()

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        
        # Execute action using the Home Assistant connector
        connector_output = await self.ha_client.execute_directive(instruction)
        output_text = connector_output

        # Optional LLM refinement if live LLM is accessible
        if self.client:
            llm_summary = await self.call_llm(
                f"Action executed on IoT devices: '{connector_output}'. "
                f"Original Founder instruction: '{instruction}'. "
                "Confirm the status to LUNA in one concise sentence."
            )
            if llm_summary:
                output_text = f"{connector_output} | {llm_summary}"

        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="smart_home",
            status="success",
            output=output_text,
            details={"ha_connected": self.ha_client.is_configured}
        )
