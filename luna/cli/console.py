import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from luna.core.engine import LunaCEOEngine
from luna.core.state import LunaGlobalState
from luna.config import settings

console = Console()

def render_banner():
    banner_text = Text()
    banner_text.append("✦ ", style="bold magenta")
    banner_text.append("LUNA ", style="bold cyan")
    banner_text.append("— Chief Executive AI Agent\n", style="bold white")
    banner_text.append("Autonomous Multi-Agent Supervisor for Smart Home, Tech Projects & Marketing Growth", style="dim")
    
    console.print(Panel(
        banner_text,
        border_style="cyan",
        subtitle="[bold green]Ready for Founder Directives[/bold green]"
    ))

def display_agent_roster():
    table = Table(title="Specialist Domain Agents", border_style="dim")
    table.add_column("Domain", style="cyan", no_wrap=True)
    table.add_column("Role", style="magenta")
    table.add_column("Tooling / Scope", style="green")
    
    table.add_row("🏠 smart_home", "Smart Home Manager", "Home Assistant REST, MQTT, Climate, Lighting, Locks")
    table.add_row("💻 projects", "Project & Tech Lead", "GitHub REST, CI/CD, Linear Issues, VPS / Cloud Ops")
    table.add_row("📈 marketing", "Growth & Social Lead", "Content Copy, X / LinkedIn / Meta, Audience Metrics")
    table.add_row("📋 assistant", "Personal Chief of Staff", "ChatGPT Ingestion, Document Audits, Pending Projects")
    table.add_row("⚡ adhoc", "Dynamic Spawner", "Deep Web Research, Script Generation, Ad-Hoc Tasks")
    console.print(table)
    console.print()

async def process_directive(engine: LunaCEOEngine, user_input: str):
    state = LunaGlobalState(founder_input=user_input)
    
    # Step 1: LUNA Planning
    with console.status("[bold cyan]LUNA is analyzing directive and formulating operational plan...", spinner="dots"):
        try:
            plan = await engine.plan(user_input, state)
        except Exception as e:
            console.print(f"[bold red]Planning Error:[/bold red] {e}")
            return

    # Render CEO Acknowledgement
    console.print(Panel(
        plan.acknowledgement_to_founder,
        title="[bold cyan]LUNA Executive Acknowledgement[/bold cyan]",
        border_style="cyan"
    ))

    # Render Subtasks Table
    tasks_table = Table(title="Delegated Subtask Graph", border_style="blue")
    tasks_table.add_column("Task ID", style="bold white", width=10)
    tasks_table.add_column("Domain Agent", style="cyan", width=14)
    tasks_table.add_column("Instruction", style="white")
    tasks_table.add_column("Risk Flag", style="bold red", width=12)

    for st in plan.subtasks:
        risk_str = "CRITICAL ⚠️" if st.is_critical else "Standard"
        tasks_table.add_row(st.task_id, st.target_domain, st.instruction, risk_str)

    console.print(tasks_table)
    console.print()

    # Step 2: Safety Gate / Human-in-the-Loop Confirmation
    founder_approved = True
    if plan.requires_confirmation:
        console.print(Panel(
            f"[bold red]ATTENTION FOUNDER:[/bold red] LUNA flagged critical operations:\n{plan.confirmation_reason}",
            border_style="red"
        ))
        founder_approved = Confirm.ask("[bold yellow]Do you authorize execution of these critical tasks?[/bold yellow]", default=False)
        if not founder_approved:
            console.print("[dim red]Founder denied authorization. Critical tasks will be skipped.[/dim red]\n")

    # Step 3: Subtask Execution
    with console.status("[bold green]Domain agents executing operations...", spinner="arc"):
        results = await engine.execute_subtasks(state, founder_approved=founder_approved)

    # Show Specialist Results
    for task_id, res in results.items():
        domain_color = {
            "smart_home": "green",
            "projects": "blue",
            "marketing": "magenta",
            "assistant": "cyan",
            "adhoc": "yellow"
        }.get(res.target_domain, "white")
        
        status_icon = "✓" if res.status == "success" else "✗"
        console.print(Panel(
            res.output,
            title=f"[{domain_color}]{status_icon} {res.target_domain.upper()} ({task_id})[/{domain_color}]",
            border_style=domain_color
        ))

    # Step 4: LUNA Final Executive Debrief
    with console.status("[bold magenta]LUNA synthesizing final debrief for Founder...", spinner="dots"):
        try:
            report = await engine.synthesize(state)
        except Exception as e:
            console.print(f"[bold red]Synthesis Error:[/bold red] {e}")
            return

    report_text = Text()
    report_text.append(f"{report.executive_summary}\n\n", style="bold white")
    
    if report.highlights:
        report_text.append("Key Highlights:\n", style="bold green")
        for h in report.highlights:
            report_text.append(f"  • {h}\n", style="white")
        report_text.append("\n")

    if report.pending_items:
        report_text.append("Action Items / Pending:\n", style="bold yellow")
        for p in report.pending_items:
            report_text.append(f"  • {p}\n", style="yellow")
        report_text.append("\n")

    if report.proactive_advice:
        report_text.append(f"CEO Strategic Insight:\n{report.proactive_advice}\n", style="italic cyan")

    console.print(Panel(
        report_text,
        title="[bold magenta]✦ LUNA Executive Briefing for Founder ✦[/bold magenta]",
        border_style="magenta"
    ))

async def run_cli():
    render_banner()
    display_agent_roster()

    if not settings.OPENAI_API_KEY:
        console.print("[bold red]WARNING:[/bold red] OPENAI_API_KEY is not set. Please add it to your environment or .env file.")
        return

    engine = LunaCEOEngine()

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]Founder[/bold cyan]").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                console.print("[bold cyan]LUNA:[/bold cyan] Standing by. Have a productive day, Founder.")
                break

            if user_input.lower() == "clear":
                console.clear()
                render_banner()
                continue

            if user_input.lower() == "help":
                console.print(
                    "[bold]Sample Directives to test LUNA:[/bold]\n"
                    "1. 'Dim the office lights to 30%, inspect latest build status, and prep a tweet announcing our beta.'\n"
                    "2. 'Deploy current main branch to production and unlock front door for the technician.' (Tests safety confirmation)\n"
                    "3. 'Give me an update on our marketing metrics and check if there are open high-priority tickets.'\n"
                    "4. 'Research top trends in AI agent frameworks for 2026.'\n"
                )
                continue

            await process_directive(engine, user_input)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold cyan]LUNA:[/bold cyan] Session terminated.")
            break
