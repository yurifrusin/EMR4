from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "docs" / "diary" / "meta-grid.css"
HTML = ROOT / "docs" / "diary" / "diary.html"
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-cost-bounded-occupied-retry"
    / "projection-overflow-evidence.json"
)


def test_result_heavy_projection_uses_content_aware_height_and_canvas_scroll() -> None:
    css = CSS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")

    assert 'href="meta-grid.css?v=12"' in html
    assert "height: min(84vh, 760px);" in css
    canvas = css[css.rindex(".meta-grid-canvas {") :]
    for contract in (
        "min-height: 0;",
        "overflow-y: auto;",
        "overscroll-behavior: contain;",
        "scrollbar-color: #78958f #eef1ed;",
        "scrollbar-gutter: stable;",
        ".meta-grid-canvas::-webkit-scrollbar-thumb",
    ):
        assert contract in canvas


def test_rendered_overflow_evidence_passes_without_provider_or_database_use() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert evidence["result"] == (
        "reception_one_projection_overflow_acceptance_pass"
    )
    assert all(evidence["checks"].values())
    assert evidence["desktop_initial"]["slot_count"] >= 8
    assert evidence["desktop_initial"]["shell"]["height"] > 690
    assert evidence["desktop_after_scroll"]["last_slot_visible"] is True
    assert evidence["bounded_after_scroll"]["last_slot_visible"] is True
    assert evidence["provider_calls"] == 0
    assert evidence["credential_reads"] == 0
    assert evidence["database_reads"] == 0
    assert evidence["database_writes"] == 0
