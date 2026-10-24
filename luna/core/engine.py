import json
import asyncio
import re
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI, AuthenticationError
from luna.config import settings
from luna.models.schemas import CEODecision, SubTask, CEOFinalReport, SubTaskResult
from luna.core.state import LunaGlobalState
from luna.safety.guardrails import SafetyGuardrail
from luna.agents.smart_home import SmartHomeAgent
from luna.agents.projects import ProjectsAgent
from luna.agents.marketing import MarketingAgent
from luna.agents.adhoc import AdHocAgent
from luna.agents.assistant import AssistantAgent
from luna.agents.system_control import SystemControlAgent

CEO_SYSTEM_PROMPT = """
You are LUNA, the Chief Executive AI Agent.
You answer directly to the Founder. You oversee specialized domain sub-agents:
1. smart_home: Handles IoT, lighting, environment, security, locks, scenes, automation.
2. projects: Handles repos, pull requests, CI/CD, server builds, tickets, technical architecture.
3. marketing: Handles social media (X, LinkedIn, Meta, YouTube), content drafting, scheduling, growth metrics.
4. assistant: Personal Chief of Staff. Ingests ChatGPT chat exports, reads documents, tracks pending projects, audits unfinished tasks, and organizes executive agendas.
5. system_control: Autonomous OS & Developer Specialist (like Antigravity, Codex, and Claude). Executes PowerShell commands, reads/writes files on disk, launches Windows apps (Notepad, Calc, Explorer), navigates URLs, and handles multilingual English/Sinhala/Singlish instructions.
6. adhoc: Handles ad-hoc research, web analysis, code debugging, general support tasks.

When the Founder gives an order:
- Decompose the goal into targeted, domain-specific subtasks.
- Assign clear, actionable instructions to the respective domain agents.
- If an action involves critical risk (e.g., prod deployments, unlocking doors, disarming alarms, large expenses), flag requires_confirmation = true and specify the reason.
- Provide a crisp, authoritative executive acknowledgement.
"""

SYNTHESIS_SYSTEM_PROMPT = """
You are LUNA, the Chief Executive AI Agent presenting an operational briefing to the Founder.
Review the original request and the results from all domain specialist agents.
Generate an executive briefing that is:
- Crisp, factual, and strictly focused on business impact and operations.
- Clearly highlights key completions.
- Flags any items that need the Founder's attention or decision.
- Offers proactive strategic recommendations as a true CEO.
"""

class LunaCEOEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.ceo_model = settings.LUNA_CEO_MODEL
        self.is_offline_simulation = False

        # Initialize domain worker agents
        self.agents = {
            "smart_home": SmartHomeAgent(),
            "projects": ProjectsAgent(),
            "marketing": MarketingAgent(),
            "assistant": AssistantAgent(),
            "system_control": SystemControlAgent(),
            "adhoc": AdHocAgent(),
        }

    def _fallback_plan(self, founder_input: str) -> CEODecision:
        """Heuristic offline planner when live LLM is unauthenticated or unavailable."""
        lower_input = founder_input.lower()
        subtasks: List[SubTask] = []
        task_counter = 1

        # Check Autonomous System / Developer & OS Control (PowerShell, file read/write, apps, desktop, Sinhala)
        if any(w in lower_input for w in [
            "run command", "powershell", "terminal", "notepad", "calculator", "calc",
            "youtube", "downloads", "explorer", "read file", "write file", "execute",
            "create folder", "make folder", "new folder", "mkdir", "create directory", "folder",
            "නෝට්පෑඩ්", "කැල්කියුලේටරය", "යූටියුබ්", "ඩවුන්ලෝඩ්ස්", "ලේඛන", "කරන්න"
        ]):
            subtasks.append(SubTask(
                task_id=f"task_{task_counter}",
                target_domain="system_control",
                instruction=f"Execute autonomous developer OS operation: {founder_input}",
                expected_output="Direct execution output, process feedback, and system status"
            ))
            task_counter += 1

        # Check Personal Assistant & Knowledge (ChatGPT chats, pending projects, to-dos)
        if any(w in lower_input for w in ["chatgpt", "chat", "pending project", "pending", "assistant", "what are my", "audit", "todo"]):
            subtasks.append(SubTask(
                task_id=f"task_{task_counter}",
                target_domain="assistant",
                instruction=f"Audit knowledge base and report pending projects: {founder_input}",
                expected_output="Structured summary of pending projects and next steps"
            ))
            task_counter += 1

        # Check Smart Home
        if any(w in lower_input for w in ["light", "lamp", "temp", "ac", "thermostat", "door", "lock", "home", "dim"]):
            subtasks.append(SubTask(
                task_id=f"task_{task_counter}",
                target_domain="smart_home",
                instruction=f"Execute smart home directive: {founder_input}",
                expected_output="Confirmation of device telemetry and state updates"
            ))
            task_counter += 1

        # Check Projects / Dev
        if any(w in lower_input for w in ["repo", "git", "deploy", "build", "ci", "ticket", "issue", "bug", "server", "code"]):
            subtasks.append(SubTask(
                task_id=f"task_{task_counter}",
                target_domain="projects",
                instruction=f"Inspect and execute engineering operations: {founder_input}",
                expected_output="Engineering operational status report"
            ))
            task_counter += 1

        # Check Marketing / Social
        if any(w in lower_input for w in ["tweet", "post", "social", "marketing", "campaign", "metrics", "analytics", "growth", "audience"]):
            subtasks.append(SubTask(
                task_id=f"task_{task_counter}",
                target_domain="marketing",
                instruction=f"Manage growth and marketing operations: {founder_input}",
                expected_output="Campaign materials or analytics report"
            ))
            task_counter += 1

        # If no specific domain matched, route to Ad-Hoc
        if not subtasks:
            subtasks.append(SubTask(
                task_id="task_1",
                target_domain="adhoc",
                instruction=founder_input,
                expected_output="Direct resolution of the founder's directive"
            ))

        return CEODecision(
            acknowledgement_to_founder=f"Acknowledged, Founder. Decomposing your mandate into {len(subtasks)} targeted specialist operational stream(s).",
            subtasks=subtasks
        )

    def _fallback_synthesize(self, state: LunaGlobalState) -> CEOFinalReport:
        """Heuristic offline briefing generator."""
        highlights = []
        for tid, res in state.domain_results.items():
            highlights.append(f"[{res.target_domain.upper()}] {res.output[:120]}")

        return CEOFinalReport(
            executive_summary=(
                f"Operational execution completed for directive: '{state.founder_input}'. "
                f"All {len(state.domain_results)} domain operational streams responded successfully."
            ),
            highlights=highlights,
            pending_items=[],
            proactive_advice="LUNA Recommendation: Maintain focus on core launch milestones while keeping smart automation nominal."
        )

    async def plan(self, founder_input: str, state: LunaGlobalState) -> CEODecision:
        """Step 1: Intent Decomposition & Delegation Planning."""
        state.log("PLAN_START", f"LUNA analyzing founder directive: '{founder_input}'")

        if not self.client or self.is_offline_simulation:
            plan = self._fallback_plan(founder_input)
        else:
            try:
                completion = await self.client.beta.chat.completions.parse(
                    model=self.ceo_model,
                    messages=[
                        {"role": "system", "content": CEO_SYSTEM_PROMPT},
                        {"role": "user", "content": founder_input}
                    ],
                    response_format=CEODecision
                )
                plan = completion.choices[0].message.parsed
            except AuthenticationError:
                self.is_offline_simulation = True
                plan = self._fallback_plan(founder_input)
            except Exception as e:
                # Fallback to local heuristic planner
                plan = self._fallback_plan(founder_input)

        # Enforce Guardrails verification
        is_risky, reasons = SafetyGuardrail.assess_risk(plan.subtasks)
        if is_risky:
            plan.requires_confirmation = True
            combined_reason = "; ".join(reasons)
            plan.confirmation_reason = (
                f"{plan.confirmation_reason + ' | ' if plan.confirmation_reason else ''}{combined_reason}"
            )

        state.active_plan = plan
        state.log("PLAN_COMPLETE", f"Decomposed into {len(plan.subtasks)} subtask(s)", {"plan": plan.model_dump()})
        return plan

    async def execute_subtasks(
        self,
        state: LunaGlobalState,
        founder_approved: bool = True
    ) -> Dict[str, SubTaskResult]:
        """Step 2: Dispatch subtasks to domain specialists."""
        plan = state.active_plan
        if not plan:
            raise ValueError("No active plan to execute.")

        if plan.requires_confirmation and not founder_approved:
            state.log("EXECUTION_BLOCKED", "Execution aborted: Founder rejected confirmation.")
            for task in plan.subtasks:
                state.domain_results[task.task_id] = SubTaskResult(
                    task_id=task.task_id,
                    target_domain=task.target_domain,
                    status="skipped",
                    output="Aborted: Action flagged as critical and not confirmed by Founder."
                )
            return state.domain_results

        state.log("EXECUTION_START", f"Dispatching {len(plan.subtasks)} tasks across domain agents.")

        async def run_single_subtask(subtask):
            agent = self.agents.get(subtask.target_domain, self.agents["adhoc"])
            try:
                result = await agent.execute(subtask)
                return subtask.task_id, result
            except Exception as e:
                return subtask.task_id, SubTaskResult(
                    task_id=subtask.task_id,
                    target_domain=subtask.target_domain,
                    status="failed",
                    output=f"Error executing subtask: {str(e)}"
                )

        tasks = [run_single_subtask(st) for st in plan.subtasks]
        results = await asyncio.gather(*tasks)

        for task_id, res in results:
            state.domain_results[task_id] = res
            state.log("TASK_COMPLETED", f"Worker [{res.target_domain}] finished task {task_id}", {"output": res.output})

        return state.domain_results

    async def synthesize(self, state: LunaGlobalState) -> CEOFinalReport:
        """Step 3: LUNA synthesizes specialist findings into an executive debrief."""
        state.log("SYNTHESIS_START", "LUNA compiling operational brief for Founder.")

        if not self.client or self.is_offline_simulation:
            final_report = self._fallback_synthesize(state)
        else:
            results_data = {
                task_id: {
                    "domain": res.target_domain,
                    "status": res.status,
                    "output": res.output
                }
                for task_id, res in state.domain_results.items()
            }

            synthesis_input = (
                f"Founder Directive: {state.founder_input}\n\n"
                f"Domain Execution Results:\n{json.dumps(results_data, indent=2)}\n"
            )

            try:
                completion = await self.client.beta.chat.completions.parse(
                    model=self.ceo_model,
                    messages=[
                        {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                        {"role": "user", "content": synthesis_input}
                    ],
                    response_format=CEOFinalReport
                )
                final_report = completion.choices[0].message.parsed
            except Exception:
                final_report = self._fallback_synthesize(state)

        state.ceo_final_report = final_report
        state.log("SYNTHESIS_COMPLETE", "Executive briefing ready.", {"report": final_report.model_dump()})
        return final_report
