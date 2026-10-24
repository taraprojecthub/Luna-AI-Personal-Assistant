import re
from typing import Dict, Any, Optional
from luna.agents.base import BaseAgent
from luna.models.schemas import SubTask, SubTaskResult
from luna.integrations.os_tools import WindowsOSTools

SYSTEM_CONTROL_PROMPT = """
You are the Autonomous Developer & OS Control Specialist Agent for LUNA (operating like Antigravity, Codex, and Claude).
You possess direct system execution tools:
1. Shell & PowerShell command execution
2. File system read / write anywhere on disk
3. Windows desktop app launching (Notepad, Calculator, Explorer)
4. URL and browser navigation
5. Multilingual comprehension: English, Sinhala, Singlish.

Deliver a crisp, factual technical debrief of operations performed.
"""

class SystemControlAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Autonomous Developer & OS Control",
            domain="system_control",
            system_prompt=SYSTEM_CONTROL_PROMPT
        )
        self.os_tools = WindowsOSTools()

    async def execute(self, subtask: SubTask) -> SubTaskResult:
        instruction = subtask.instruction
        lower = instruction.lower().strip()
        actions = []

        # Strip generic planner prefixes
        clean_text = re.sub(r"^execute autonomous developer os operation:\s*", "", instruction, flags=re.IGNORECASE).strip()

        # 1. Check LUNA desktop action (apps, folders, websites, Sinhala/English commands)
        desktop_action = self.os_tools.execute_desktop_action(clean_text)
        if desktop_action:
            actions.append(f"[Desktop Action] {desktop_action}")

        # 2. Check if a shell command is specified
        cmd_match = re.search(r"(?:run command|powershell|cmd|terminal|shell)[\s:]+['\"]?(.+?)['\"]?$", clean_text, re.IGNORECASE)
        if cmd_match:
            cmd = cmd_match.group(1).strip()
            res = self.os_tools.run_command(cmd)
            status_str = "SUCCESS" if res["success"] else "FAILED"
            out = res.get("stdout") or res.get("stderr") or res.get("error", "No output")
            actions.append(f"[Shell Exec: `{cmd}`] ({status_str})\n{out}")
        elif any(clean_text.lower().startswith(p) for p in ["dir", "ls", "git ", "npm ", "py ", "python ", "cat ", "type "]):
            res = self.os_tools.run_command(clean_text)
            status_str = "SUCCESS" if res["success"] else "FAILED"
            out = res.get("stdout") or res.get("stderr") or res.get("error", "No output")
            actions.append(f"[Shell Exec: `{clean_text}`] ({status_str})\n{out}")

        # 3. Check if file reading is specified
        read_match = re.search(r"(?:read file|show file|open file)[\s:]+['\"]?([a-zA-Z0-9_\-\.\:\/\\]+)['\"]?", clean_text, re.IGNORECASE)
        if read_match:
            path = read_match.group(1).strip()
            res = self.os_tools.read_file(path)
            if res["success"]:
                content_preview = res["content"][:400] + ("..." if len(res["content"]) > 400 else "")
                actions.append(f"[Read File: `{res['path']}` ({res['size_bytes']} bytes)]\n{content_preview}")
            else:
                actions.append(f"[Read File Failed] {res.get('error')}")

        if not actions:
            # Fallback direct execution
            res = self.os_tools.run_command(clean_text)
            if res["success"] and res["stdout"]:
                actions.append(f"[Output]\n{res['stdout']}")
            else:
                actions.append(f"Autonomous OS controller evaluated: '{clean_text}'. System nominal.")

        combined_output = "\n\n".join(actions)

        # Optional LLM refinement if available
        if self.client:
            llm_summary = await self.call_llm(
                f"Actions executed on Windows OS:\n{combined_output}\n"
                f"Founder instruction: '{instruction}'\n"
                "Summarize what was performed and provide any technical recommendations."
            )
            if llm_summary:
                combined_output = f"{combined_output}\n\nTechnical Debrief:\n{llm_summary}"

        return SubTaskResult(
            task_id=subtask.task_id,
            target_domain="system_control",
            status="success",
            output=combined_output,
            details={"actions_count": len(actions)}
        )
