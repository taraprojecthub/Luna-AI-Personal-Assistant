import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "luna_desktop"))

from memory.config_manager import (
    HUD_STYLES,
    HUD_STYLE_LABELS,
    get_hud_style,
    save_hud_style,
)


def test_hud_styles_definitions():
    expected_styles = [
        "waves",
        "face",
        "quantum_orb",
        "cyber_matrix",
        "audio_sphere",
        "stellar_pulsar",
    ]
    for s in expected_styles:
        assert s in HUD_STYLES
        assert s in HUD_STYLE_LABELS
        assert len(HUD_STYLE_LABELS[s]) > 0


def test_hud_style_persistence():
    orig = get_hud_style()
    try:
        for s in ["quantum_orb", "cyber_matrix", "audio_sphere", "stellar_pulsar", "waves"]:
            save_hud_style(s)
            assert get_hud_style() == s
    finally:
        save_hud_style(orig)


def test_hud_canvas_rendering():
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QImage, QPainter
    import ui

    app = QApplication.instance() or QApplication([])
    hud = ui.HudCanvas("")
    hud.resize(1000, 700)
    img = QImage(1000, 700, QImage.Format.Format_ARGB32_Premultiplied)

    painter = QPainter(img)
    try:
        for s in HUD_STYLES:
            hud.hud_style = s
            # Direct painter call test
            if s == "quantum_orb":
                hud._paint_quantum_orb(painter, 500, 350, 200, 1000, 500)
            elif s == "cyber_matrix":
                hud._paint_cyber_matrix(painter, 500, 350, 200, 1000, 500)
            elif s == "audio_sphere":
                hud._paint_audio_sphere(painter, 500, 350, 200, 1000, 500)
            elif s == "stellar_pulsar":
                hud._paint_stellar_pulsar(painter, 500, 350, 200, 1000, 500)
            elif s == "waves":
                hud._paint_waves(painter, 500, 350, 200, 1000, 500)
            elif s == "core":
                hud._paint_core(painter, 500, 350, 200, 1000, 500)
    finally:
        painter.end()
