import os
import re
import json
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional

IGNORED_DIRS = {
    ".git", ".venv", "node_modules", "vendor", "cache", ".cache",
    ".idea", ".vscode", "dist", "build", "pods", "framework",
    "symfony", "laravel", "doctrine", "psr", "illuminate",
    "guzzlehttp", "composer", "storage", ".localappdata", ".npm-cache"
}

class ChatGPTKnowledgeReader:
    """Ingests and analyzes ChatGPT conversation exports, transcripts, and founder projects."""

    def __init__(self, inbox_dir: Optional[Path] = None):
        self.inbox_dir = inbox_dir or (Path(__file__).parent.parent.parent / "inbox")
        self.search_dirs = [
            Path("C:/Users/tharaka/Documents/ChatGPT"),
            Path("C:/Users/tharaka/Documents/Codex"),
            Path("C:/Users/tharaka/Documents/Antigravity"),
        ]

    def _extract_text_from_node(self, node: Dict[str, Any]) -> str:
        """Safely extracts text parts from ChatGPT message JSON node."""
        message = node.get("message")
        if not message:
            return ""
        content = message.get("content", {})
        parts = content.get("parts", [])
        text_pieces = []
        for p in parts:
            if isinstance(p, str):
                text_pieces.append(p)
            elif isinstance(p, dict) and "text" in p:
                text_pieces.append(str(p["text"]))
        return "\n".join(text_pieces)

    def parse_chatgpt_export(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parses an official conversations.json export or zip archive."""
        conversations = []
        try:
            if file_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(file_path, 'r') as z:
                    for name in z.namelist():
                        if name.endswith("conversations.json"):
                            with z.open(name) as f:
                                data = json.load(f)
                                conversations = data if isinstance(data, list) else data.get("conversations", [])
                                break
            elif file_path.suffix.lower() == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conversations = data if isinstance(data, list) else data.get("conversations", [])
        except Exception as e:
            return [{"error": f"Failed to read {file_path.name}: {str(e)}"}]

        extracted_projects = []
        for conv in conversations:
            title = conv.get("title", "Untitled Project")
            mapping = conv.get("mapping", {})
            full_conv_text = []

            for node in mapping.values():
                t = self._extract_text_from_node(node)
                if t:
                    full_conv_text.append(t)

            conv_text = "\n".join(full_conv_text)
            pending_items = self._extract_pending_items(conv_text)
            if pending_items:
                extracted_projects.append({
                    "title": title,
                    "source": f"ChatGPT Chat Export: {file_path.name}",
                    "pending_tasks": pending_items,
                    "summary_snippet": conv_text[:300].strip()
                })

        return extracted_projects

    def _extract_pending_items(self, text: str) -> List[str]:
        """Scans conversation or document text for pending items, todos, and next upgrades."""
        pending = []
        patterns = [
            r"(?:todo|next steps?|next upgrades?|pending|to build|features to add)[\s:]+([^\n]+(?:\n\s*[-*•]\s*[^\n]+)*)",
            r"(?:[-*•]\s*(?:need to|pending|should|will|todo|fix|upgrade|integrate)\s*[^\n]+)",
        ]
        
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                clean = m.strip()
                if clean:
                    for line in clean.splitlines():
                        line_clean = re.sub(r"^[-*•\d\.\s#]+", "", line).strip()
                        if 6 < len(line_clean) < 130 and line_clean not in pending:
                            pending.append(line_clean)

        return pending[:6]

    def scan_all_project_sources(self) -> List[Dict[str, Any]]:
        """Scans ChatGPT folders, inbox drops, and primary project workspaces."""
        projects = []
        seen_titles = set()

        # 1. Scan Inbox for dropped ChatGPT exports or notes
        if self.inbox_dir.exists():
            for file in self.inbox_dir.iterdir():
                if file.is_file():
                    if file.suffix.lower() in [".json", ".zip"]:
                        for p in self.parse_chatgpt_export(file):
                            if p["title"] not in seen_titles:
                                seen_titles.add(p["title"])
                                projects.append(p)
                    elif file.suffix.lower() in [".txt", ".md"]:
                        txt = file.read_text(encoding="utf-8", errors="ignore")
                        pending = self._extract_pending_items(txt)
                        projects.append({
                            "title": file.stem,
                            "source": f"inbox/{file.name}",
                            "pending_tasks": pending if pending else ["Review notes and plan execution milestones"],
                            "summary_snippet": txt[:250].strip()
                        })

        # 2. Scan primary founder projects in Documents
        for base_dir in self.search_dirs:
            if not base_dir.exists():
                continue
            
            # Look at immediate subdirectories to identify main top-level projects
            try:
                for entry in base_dir.iterdir():
                    if not entry.is_dir() or entry.name.lower() in IGNORED_DIRS or entry.name.lower() == "luna":
                        continue
                    
                    project_name = entry.name
                    if project_name in seen_titles:
                        continue

                    # Search for top-level README or roadmap inside this project
                    readme_file = None
                    for candidate in ["README.md", "readme.md", "TODO.md"]:
                        p = entry / candidate
                        if p.exists():
                            readme_file = p
                            break
                    
                    # If not at root of project, check 1 level down (e.g. TARA IoT Dashboard/iot-network-dashboard-windows/README.md)
                    if not readme_file:
                        for sub in entry.iterdir():
                            if sub.is_dir() and sub.name.lower() not in IGNORED_DIRS:
                                for candidate in ["README.md", "readme.md", "TODO.md"]:
                                    p = sub / candidate
                                    if p.exists():
                                        readme_file = p
                                        project_name = f"{entry.name} / {sub.name}"
                                        break
                                if readme_file:
                                    break

                    pending = []
                    snippet = f"Project located at {entry.name}"
                    if readme_file:
                        try:
                            txt = readme_file.read_text(encoding="utf-8", errors="ignore")
                            pending = self._extract_pending_items(txt)
                            snippet = txt[:250].strip()
                        except Exception:
                            pass

                    seen_titles.add(project_name)
                    projects.append({
                        "title": project_name,
                        "source": f"{base_dir.name}/{entry.name}",
                        "pending_tasks": pending if pending else ["Active project workspace; verify open tickets and sprint backlog"],
                        "summary_snippet": snippet
                    })
            except Exception:
                continue

        return projects

    def format_assistant_briefing(self) -> str:
        """Generates a structured personal assistant summary of all pending projects."""
        projects = self.scan_all_project_sources()
        if not projects:
            return (
                "Personal Assistant Audit: No pending projects currently detected.\n"
                f"Drop any ChatGPT export (.json or .zip) into `LUNA/inbox` or your Documents folder."
            )

        lines = [f"Found {len(projects)} primary project(s) across your ChatGPT history and local workspaces:\n"]
        for idx, p in enumerate(projects, 1):
            lines.append(f"{idx}. 📁 **{p['title']}** (Source: `{p['source']}`)")
            if p.get("pending_tasks"):
                for task in p["pending_tasks"]:
                    lines.append(f"   • {task}")
            else:
                lines.append("   • Roadmap review nominal")
            lines.append("")

        lines.append(
            f"💡 **Tip:** Drop any ChatGPT conversation export or project notes directly into `LUNA/inbox` "
            "for deep conversational extraction."
        )
        return "\n".join(lines)
