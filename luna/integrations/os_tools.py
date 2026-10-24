import os
import re
import sys
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class WindowsOSTools:
    """Provides autonomous OS execution, shell commands, and desktop application controls."""

    APP_MAP = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "files": "explorer.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "taskmgr": "taskmgr.exe",
    }

    FOLDER_MAP = {
        "downloads": Path.home() / "Downloads",
        "documents": Path.home() / "Documents",
        "desktop": Path.home() / "Desktop",
    }

    @staticmethod
    def run_command(command: str, cwd: Optional[str] = None, timeout: int = 45) -> Dict[str, Any]:
        """Runs a PowerShell or shell command with full output capture."""
        try:
            res = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def read_file(path: str) -> Dict[str, Any]:
        """Reads content from any accessible file path."""
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return {"success": False, "error": f"File not found: {p}"}
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            return {"success": True, "path": str(p), "size_bytes": len(text), "content": text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def write_file(path: str, content: str) -> Dict[str, Any]:
        """Creates or overwrites a file at the specified path."""
        p = Path(path).expanduser().resolve()
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return {"success": True, "path": str(p), "size_bytes": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def create_directory(cls, instruction: str) -> Optional[Dict[str, Any]]:
        """Parses natural language requests to create folders and directories anywhere on the PC."""
        lower = instruction.lower().strip()
        
        # Check if folder creation is requested
        keywords = ["create folder", "make folder", "create a folder", "new folder", "mkdir", "make directory", "create directory", "folder එක හදන්න"]
        if not any(k in lower for k in keywords):
            return None

        # Determine target base directory
        base_dir = Path.cwd()
        if "desktop" in lower:
            base_dir = Path.home() / "Desktop"
        elif "documents" in lower:
            base_dir = Path.home() / "Documents"
        elif "downloads" in lower:
            base_dir = Path.home() / "Downloads"

        # Extract folder name
        folder_name = None
        # Pattern 1: called/named 'FolderName'
        m = re.search(r'(?:called|named|name)\s+["\']?([a-zA-Z0-9_\-]+)["\']?', instruction, re.IGNORECASE)
        if m:
            folder_name = m.group(1).strip()
        else:
            # Pattern 2: create folder FolderName
            m2 = re.search(r'(?:create|make|new)\s+(?:a\s+)?(?:folder|directory|dir)\s+["\']?([a-zA-Z0-9_\-]+)["\']?', instruction, re.IGNORECASE)
            if m2 and m2.group(1).lower() not in ["on", "in", "called", "named", "at"]:
                folder_name = m2.group(1).strip()
            else:
                m3 = re.search(r'(?:mkdir)\s+["\']?([^"\']+)["\']?', instruction, re.IGNORECASE)
                if m3:
                    folder_name = m3.group(1).strip()

        if not folder_name:
            folder_name = "New_Folder"

        target_path = Path(folder_name)
        if not target_path.is_absolute():
            target_path = base_dir / folder_name

        try:
            target_path.mkdir(parents=True, exist_ok=True)
            return {
                "success": True,
                "path": str(target_path),
                "name": target_path.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def execute_desktop_action(cls, text: str) -> Optional[str]:
        """
        Executes LUNA desktop actions (apps, browser, folders).
        Understands English, Sinhala, and Singlish.
        """
        normalized = text.lower().strip()

        # 1. Apps (Notepad, Calculator, File Explorer)
        if re.search(r"\b(open|launch|start|දෙන්න|කරන්න)\s*(notepad|නෝට්පෑඩ්)\b", normalized):
            subprocess.Popen([cls.APP_MAP["notepad"]])
            return "Launched Notepad."

        if re.search(r"\b(open|launch|start|දෙන්න|කරන්න)\s*(calculator|calc|කැල්කියුලේටරය)\b", normalized):
            subprocess.Popen([cls.APP_MAP["calculator"]])
            return "Launched Calculator."

        if re.search(r"\b(open|launch|start)\s*(file explorer|explorer|files)\b", normalized):
            subprocess.Popen([cls.APP_MAP["explorer"]])
            return "Launched File Explorer."

        # 2. Web browsing (YouTube, GitHub, etc.)
        if re.search(r"\b(open|go to|visit|යන්න)\s*(youtube|යූටියුබ්)\b", normalized):
            webbrowser.open("https://www.youtube.com")
            return "Opened YouTube in default browser."

        if re.search(r"\b(open|go to|visit)\s*(github|ගිට්හබ්)\b", normalized):
            webbrowser.open("https://github.com")
            return "Opened GitHub in default browser."

        # 3. Special folders (Downloads, Documents, Desktop)
        if re.search(r"\b(open|show|පෙන්නන්න)\s*(downloads|download folder|ඩවුන්ලෝඩ්ස්)\b", normalized):
            dl = cls.FOLDER_MAP["downloads"]
            if dl.exists():
                os.startfile(str(dl))
                return f"Opened Downloads folder: {dl}"

        if re.search(r"\b(open|show|පෙන්නන්න)\s*(documents|ලේඛන)\b", normalized):
            doc = cls.FOLDER_MAP["documents"]
            if doc.exists():
                os.startfile(str(doc))
                return f"Opened Documents folder: {doc}"

        return None
