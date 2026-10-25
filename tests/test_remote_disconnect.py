import sys
import time
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "luna_desktop"))

from dashboard.server import DashboardServer


class MockClient:
    def __init__(self, host):
        self.host = host
        self.port = 54321


class MockWebSocket:
    def __init__(self, host):
        self.client = MockClient(host)
        self.closed = False
        self.sent = []

    async def send_json(self, data):
        self.sent.append(data)

    async def close(self, code=1000):
        self.closed = True


def test_dashboard_server_sessions_and_selective_disconnect():
    server = DashboardServer()
    assert server.get_active_sessions() == []

    ws1 = MockWebSocket("192.168.1.101")
    ws2 = MockWebSocket("192.168.1.102")

    server._tokens["tok1_abcdef123456"] = time.time() + 300
    server._tokens["tok2_fedcba987654"] = time.time() + 300

    server._active_clients[ws1] = {
        "ip": "192.168.1.101",
        "type": "Dashboard",
        "connected_at": time.time() - 30,
        "token": "tok1_abcdef123456",
    }
    server._active_clients[ws2] = {
        "ip": "192.168.1.102",
        "type": "Dashboard",
        "connected_at": time.time() - 10,
        "token": "tok2_fedcba987654",
    }

    sessions = server.get_active_sessions()
    assert len(sessions) == 2
    ips = [s["ip"] for s in sessions]
    assert "192.168.1.101" in ips
    assert "192.168.1.102" in ips

    # Selective disconnect of client 1 only
    s1_id = [s["id"] for s in sessions if s["ip"] == "192.168.1.101"][0]
    ok = server.disconnect_session(s1_id)
    assert ok is True

    # Client 1 token is revoked, client 2 token is still active!
    assert "tok1_abcdef123456" not in server._tokens
    assert "tok2_fedcba987654" in server._tokens

    # Active sessions now only contains client 2
    remaining = server.get_active_sessions()
    assert len(remaining) == 1
    assert remaining[0]["ip"] == "192.168.1.102"

    # Now disconnect all remaining
    server.disconnect_all()
    assert server.get_active_sessions() == []
    assert len(server._tokens) == 0


def test_ui_remote_controls_and_selective_overlay():
    from PyQt6.QtWidgets import QApplication
    import ui

    app = QApplication.instance() or QApplication([])
    lui = ui.LunaUI("")

    win = lui._win
    assert hasattr(win, "_remote_header_btn")
    assert hasattr(win, "_drawer_disconnect_btn")

    # Initial state: 0 active
    win.get_remote_sessions = lambda: []
    win._on_remote_sessions_updated()
    assert "REMOTE" in win._remote_header_btn.text()
    assert win._drawer_disconnect_btn.isHidden() is True

    # Two active sessions
    two_sessions = [
        {"id": "s1", "ip": "192.168.1.101", "types": ["Dashboard"], "duration_secs": 45},
        {"id": "s2", "ip": "192.168.1.102", "types": ["Phone Audio"], "duration_secs": 20},
    ]
    win.get_remote_sessions = lambda: two_sessions
    win._on_remote_sessions_updated()
    assert "2 ACTIVE" in win._remote_header_btn.text()
    assert win._drawer_disconnect_btn.isHidden() is False
    assert "DISCONNECT REMOTE (2)" in win._drawer_disconnect_btn.text()

    # Verify overlay rows
    disconnected_ids = []
    overlay = ui.RemoteKeyOverlay(
        url="http://127.0.0.1:8000",
        key="ABC12345",
        sessions=two_sessions,
        on_disconnect=win._do_disconnect_remote,
        on_disconnect_session=lambda sid: disconnected_ids.append(sid),
    )
    assert overlay._disconnect_btn.isEnabled() is True
    assert "ACTIVE REMOTE SESSIONS (2)" in overlay._sessions_status_lbl.text()
    assert overlay._sessions_list_layout.count() == 2

    # Click individual disconnect on first row
    first_row = overlay._sessions_list_layout.itemAt(0).widget()
    disc_btns = first_row.findChildren(ui.QPushButton)
    assert len(disc_btns) == 1
    disc_btns[0].click()
    assert len(disconnected_ids) == 1
    assert disconnected_ids[0] == "s1"
