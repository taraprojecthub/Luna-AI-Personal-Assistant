import sys
import os
import json
from pathlib import Path

# Add luna_desktop directory to path
base_dir = Path(__file__).resolve().parent.parent / "luna_desktop"
sys.path.insert(0, str(base_dir))
os.chdir(str(base_dir))

def test_luna_config():
    with open("config/api_keys.json", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["assistant_name"] == "LUNA"
    assert cfg["ui_color"] == "#00f2fe"

def test_luna_avatar_mesh():
    from core.avatar import HoloAvatar
    avatar = HoloAvatar()
    assert avatar is not None
    assert avatar._v0 is not None
    assert len(avatar._v0) > 0

def test_luna_actions():
    from core.action_loader import discover_actions
    registry = discover_actions(Path("actions"))
    actions = registry.names()
    assert len(actions) >= 15
    assert "open_app" in actions
    assert "computer_control" in actions
    assert "web_search" in actions

def test_luna_ui_title():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    import ui
    lui = ui.LunaUI("")
    title = lui._win.windowTitle()
    assert "LUNA" in title
