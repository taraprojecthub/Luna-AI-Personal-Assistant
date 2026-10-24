from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.integrations.chatgpt_reader import ChatGPTKnowledgeReader

ASSISTANT_SYSTEM_PROMPT = """
You are the Founder's Personal Assistant & Chief of Staff Agent reporting to LUNA (CEO).
You manage the Founder's personal knowledge base, ChatGPT chat history, pending project roadmaps,
and high-priority to-do audits.
Analyze the extracted project data, identify all pending projects and upgrades,
and format a crisp, highly actionable executive summary.
"""

class AssistantAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Personal Assistant & Knowledge Lead",
            domain="assistant",
            system_prompt=ASSISTANT_SYSTEM_PROMPT
        )
        self.reader = ChatGPTKnowledgeReader()

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        lower = instruction.lower()

        # If instruction is to inspect ChatGPT chats or pending projects
        if any(w in lower for w in ["chatgpt", "pending", "project", "todo", "assistant", "what are", "audit"]):
            audit_report = self.reader.format_assistant_briefing()
            output_text = audit_report

            if self.client:
                llm_summary = await self.call_llm(
                    f"Discovered Project Audit:\n{audit_report}\n"
                    f"Founder Instruction: '{instruction}'\n"
                    "Provide an executive assistant debrief organizing these projects by urgency and next steps."
                )
                if llm_summary:
                    output_text = f"{audit_report}\n\nExecutive Assistant Debrief:\n{llm_summary}"
        else:
            output_text = f"Personal Assistant evaluated: '{instruction}'. Knowledge repository nominal."

        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="assistant",
            status="success",
            output=output_text,
            details={"inbox_path": str(self.reader.inbox_dir)}
        )
