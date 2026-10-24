import os
import re
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from luna.config import settings
from luna.integrations.os_tools import WindowsOSTools
from luna.integrations.chatgpt_reader import ChatGPTKnowledgeReader
from luna.integrations.home_assistant import HomeAssistantClient
from luna.integrations.web_research import WebResearchConnector

SYSTEM_PROMPT = """You are LUNA, an autonomous executive AI assistant operating on the Founder's Windows PC.
You are equipped with direct OS execution tools, file system access, smart home controls, and knowledge audit engines.
You converse naturally, concisely, and authoritatively (just like Antigravity, Claude, or ChatGPT).
When the Founder asks you to perform a task:
- You execute the appropriate tools directly on the PC.
- You analyze the results and provide a natural, clear conversational answer.
- You answer questions, explain findings, and suggest proactive next steps.
- You understand English, Sinhala, and Singlish.
"""

class LunaConversationAgent:
    """Autonomous Conversational ReAct Agent with real PC tools and multi-turn dialog."""

    def __init__(self):
        self.os_tools = WindowsOSTools()
        self.chatgpt_reader = ChatGPTKnowledgeReader()
        self.ha_client = HomeAssistantClient()
        self.web_research = WebResearchConnector()
        self.history: List[Dict[str, str]] = []

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Executes real local tools on the host system."""
        try:
            if tool_name == "run_command":
                cmd = args.get("command", "")
                res = self.os_tools.run_command(cmd)
                out = res.get("stdout") or res.get("stderr") or res.get("error", "Executed without output")
                return f"[Exit: {res.get('exit_code', 0)}]\n{out}"

            elif tool_name == "create_folder":
                name = args.get("name", "New_Folder")
                location = args.get("location", "Desktop")
                base = Path.home() / "Desktop" if "desktop" in location.lower() else (Path.home() / "Documents" if "document" in location.lower() else Path.cwd())
                target = base / name
                target.mkdir(parents=True, exist_ok=True)
                return f"Successfully created folder at: {target}"

            elif tool_name == "read_file":
                path = args.get("path", "")
                res = self.os_tools.read_file(path)
                return res.get("content", f"Error: {res.get('error')}")[:1500]

            elif tool_name == "write_file":
                path = args.get("path", "")
                content = args.get("content", "")
                res = self.os_tools.write_file(path, content)
                return f"Successfully written {res.get('size_bytes', 0)} bytes to {path}"

            elif tool_name == "launch_app":
                app_name = args.get("app_name", "")
                res = self.os_tools.execute_desktop_action(f"open {app_name}")
                return res or f"Attempted desktop action for {app_name}"

            elif tool_name == "audit_chatgpt_projects":
                return self.chatgpt_reader.format_assistant_briefing()

            elif tool_name == "web_search":
                query = args.get("query", "")
                return asyncio.run(self.web_research.execute_directive(query))

            elif tool_name == "smart_home":
                cmd = args.get("directive", "")
                return asyncio.run(self.ha_client.execute_directive(cmd))

            return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Tool execution error: {str(e)}"

    async def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Processes a conversational message from the Founder.
        Interprets intent, runs necessary OS tools, and returns conversational response.
        """
        lower = user_message.lower().strip()
        tools_executed = []
        assistant_reply = ""

        # Tool Heuristics / Intent Recognition (When offline or operating locally)
        # 1. Folder creation
        if any(k in lower for k in ["create folder", "create a folder", "make folder", "make a folder", "new folder", "mkdir", "folder එකක් හදන්න", "folder හදන්න"]):
            folder_res = self.os_tools.create_directory(user_message)
            if folder_res and folder_res["success"]:
                tools_executed.append({
                    "tool": "create_folder",
                    "args": {"path": folder_res["path"]},
                    "result": f"Created: {folder_res['path']}"
                })
                assistant_reply = (
                    f"I've created the folder for you at `{folder_res['path']}`.\n\n"
                    "Let me know if you would like me to generate any files or project structure inside it!"
                )
            else:
                assistant_reply = f"I encountered an issue creating the folder: {folder_res.get('error') if folder_res else 'Invalid path'}"

        # 2. Desktop apps / Launch actions
        elif any(k in lower for k in ["open notepad", "open calc", "open calculator", "open youtube", "open downloads", "open explorer", "නෝට්පෑඩ්", "කැල්කියුලේටරය"]):
            action_res = self.os_tools.execute_desktop_action(user_message)
            tools_executed.append({
                "tool": "launch_app",
                "args": {"action": user_message},
                "result": action_res or "Launched"
            })
            assistant_reply = f"Done! {action_res}"

        # 3. Read ChatGPT chats / pending projects
        elif any(k in lower for k in ["chatgpt", "pending project", "what are my project", "audit project", "todo"]):
            brief = self.chatgpt_reader.format_assistant_briefing()
            tools_executed.append({
                "tool": "audit_chatgpt_projects",
                "args": {},
                "result": f"Scanned local ChatGPT and project workspaces"
            })
            assistant_reply = (
                f"I've scanned your ChatGPT sessions and local project workspaces. Here is your current project status:\n\n"
                f"{brief}\n\n"
                "Would you like me to prioritize any of these tasks or help you build one right now?"
            )

        # 4. Run PowerShell / Shell command
        elif any(k in lower for k in ["run command", "powershell", "execute", "dir", "get-process", "git status"]):
            clean_cmd = re.sub(r"^(?:run command|powershell|execute)[\s:]+", "", user_message, flags=re.IGNORECASE).strip()
            res = self.os_tools.run_command(clean_cmd)
            out = res.get("stdout") or res.get("stderr") or "No output returned"
            tools_executed.append({
                "tool": "run_command",
                "args": {"command": clean_cmd},
                "result": out[:500]
            })
            assistant_reply = f"I executed `{clean_cmd}` in PowerShell:\n\n```text\n{out}\n```"

        # 5. Smart Home / Lights / AC
        elif any(k in lower for k in ["light", "lights", "dim", "thermostat", "ac", "cool", "door lock"]):
            ha_res = await self.ha_client.execute_directive(user_message)
            tools_executed.append({
                "tool": "smart_home",
                "args": {"directive": user_message},
                "result": ha_res
            })
            assistant_reply = f"Smart Home adjusted: {ha_res}."

        # 6. Conversational / General Assistance
        else:
            assistant_reply = (
                f"I'm on it, Founder. I'm connected directly to your Windows system, projects, and smart home. "
                f"You asked: *\"{user_message}\"*\n\n"
                "I can execute PowerShell commands, create/edit files, audit your ChatGPT projects, launch desktop apps, or research anything on the web. "
                "What would you like me to do next?"
            )

        # Append to conversational memory
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_reply})

        return {
            "reply": assistant_reply,
            "tools_executed": tools_executed,
            "history_length": len(self.history)
        }

conversation_agent = LunaConversationAgent()
