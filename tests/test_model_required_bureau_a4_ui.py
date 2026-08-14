"""Deterministic UI and client-reconciliation acceptance for Rayleen A4."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT / "node_modules" / ".bin" / "node"
MODULE = ROOT / "docs/diary/rayleen-waiting-room-projection.mjs"
DIARY_JS = ROOT / "docs/diary/diary.js"
DIARY_HTML = ROOT / "docs/diary/diary.html"
DIARY_CSS = ROOT / "docs/diary/diary.css"
ACCEPTANCE = ROOT / "scripts/model_required_bureau_a4_ui_acceptance.mjs"


def _run_acceptance(output: Path) -> dict[str, object]:
    completed = subprocess.run(
        ["node", str(ACCEPTANCE), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    stdout = json.loads(completed.stdout)
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert stdout == persisted
    return persisted


def test_ui_state_machine_acceptance_passes(tmp_path: Path) -> None:
    evidence = _run_acceptance(tmp_path / "evidence.json")
    assert evidence["result"] == "provider_free_rayleen_a4_ui_state_machine_pass"
    assert evidence["case_count"] == evidence["passed_case_count"]
    assert evidence["failed_case_count"] == 0
    assert evidence["properties"] == {
        "strict_true_default_off": True,
        "latest_read_wins": True,
        "interruption_suppresses_release": True,
        "response_schema_closed": True,
        "provider_or_external_effect": False,
        "command_or_write_authority": False,
        "browser_or_backend_claim": False,
    }


def test_new_module_has_no_direct_effectful_surface() -> None:
    source = MODULE.read_text(encoding="utf-8")
    for pattern in (
        r"\bfetch\s*\(",
        r"XMLHttpRequest",
        r"\bdocument\s*\.",
        r"\bwindow\s*\.",
        r"\blocalStorage\b",
        r"\bsessionStorage\b",
        r"\bWebSocket\b",
        r"\bEventSource\b",
        r"\bindexedDB\b",
    ):
        assert not re.search(pattern, source)


def test_diary_wiring_is_local_default_off_receptionist_only_and_non_persistent() -> None:
    source = DIARY_JS.read_text(encoding="utf-8")
    assert 'isLocalHarnessCapabilityEnabled("rayleen_waiting_room")' in source
    assert 'currentUserRole === "Receptionist"' in source
    assert 'bootstrap.enabled === true' in source
    assert 'import("./rayleen-waiting-room-projection.mjs?v=2")' in source
    assert "closeRayleenWaitingRoom({ restoreFocus: false });" in source
    rayleen_slice = source[
        source.index("const RAYLEEN_WAITING_ROOM_BOOTSTRAP_GLOBAL") :
        source.index("function getApplicationSessionPractitionerBootstrap")
    ]
    assert "localStorage" not in rayleen_slice
    assert "sessionStorage" not in rayleen_slice
    assert "apiFetch(" not in rayleen_slice
    assert "fetch(" not in rayleen_slice


def test_ui_is_separate_read_only_accessible_and_responsive() -> None:
    html = DIARY_HTML.read_text(encoding="utf-8")
    css = DIARY_CSS.read_text(encoding="utf-8")
    assert 'id="btn-rayleen-waiting-room"' in html
    assert 'class="btn-rayleen-toggle hidden"' in html
    assert 'id="rayleen-waiting-room-panel"' in html
    assert 'aria-live="polite"' in html
    assert "No booking is reserved, confirmed or changed" in html
    assert html.index('id="rayleen-waiting-room-panel"') > html.index(
        'id="diary-flow-panel"'
    )
    assert "#diary-flow-panel .rayleen" not in css
    assert ".rayleen-waiting-room-panel" in css
    assert "@media (max-width: 768px)" in css
    assert "@media (max-width: 420px)" in css
    assert ":focus-visible" in css
    assert 'diary.css?v=140' in html
    assert 'diary.js?v=201' in html


def test_ui_has_refresh_close_escape_stale_and_fallback_states() -> None:
    source = DIARY_JS.read_text(encoding="utf-8")
    for marker in (
        "btn-refresh-rayleen-waiting-room",
        "btn-close-rayleen-waiting-room",
        'event.key === "Escape"',
        'document.addEventListener("keydown", handleRayleenWaitingRoomEscape)',
        "Attention — this read expires in 30 seconds.",
        "request_interrupted",
        "request_superseded",
        "ordinary Waiting Room is unchanged",
        "nothing was released",
        "invalidateAndResetRayleenWaitingRoom",
        "renderRayleenWaitingRoomFrame",
    ):
        assert marker in source

    assert re.search(
        r'clearRayleenWaitingRoomContent\(\s*"This Rayleen projection expired\.[^"]*",\s*"expired"\s*\)',
        source,
    )

    css = DIARY_CSS.read_text(encoding="utf-8")
    assert ".rayleen-waiting-room-status.is-expiring" in css
    assert '[data-freshness-state="expired"] .rayleen-waiting-room-card' in css
    assert "display: none !important" in css


def test_ordinary_diary_refresh_does_not_preempt_rayleen_ttl() -> None:
    source = DIARY_JS.read_text(encoding="utf-8")
    refresh_slice = source[
        source.index("function doRefresh()") : source.index("function focusDiaryWindow()")
    ]
    assert "invalidateAndResetRayleenWaitingRoom" not in refresh_slice
    assert "expireRayleenWaitingRoomFrame" not in refresh_slice
    assert "loadDiary();" in refresh_slice
    assert "scheduleRefresh();" in refresh_slice
