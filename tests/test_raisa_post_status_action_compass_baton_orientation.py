from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/raisa-post-status-action-compass-baton-orientation.md"
DIARY = ROOT / "docs/diary/diary.js"
META_GRID = ROOT / "docs/diary/meta-grid.js"
OPENAPI = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_orientation_distinguishes_truth_parity_from_feature_parity() -> None:
    report = _text(REPORT)
    head = "\n".join(report.splitlines()[:14])
    assert "Date: 2026-08-13" in head
    assert "Timestamp: 2026-08-13T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    for phrase in (
        "truth-parity conformance rehearsal",
        "truth parity, not feature parity",
        "The kernel therefore sits above every renderer",
        "many modalities, one authoritative meaning",
        "no genuine user-attention fork",
    ):
        assert phrase.lower() in report.lower()


def test_both_renderers_converge_on_the_same_existing_status_interaction() -> None:
    diary = _text(DIARY)
    bridge_start = diary.index("async function metaGridSetAppointmentStatus")
    bridge_end = diary.index("function setMetaGridLaunchAvailability", bridge_start)
    bridge = diary[bridge_start:bridge_end]
    kernel_start = diary.index("async function setAppointmentStatus(")
    kernel_end = diary.index("function toggleFlowPanel", kernel_start)
    kernel = diary[kernel_start:kernel_end]

    assert "setAppointmentStatus(" in bridge
    assert "metaGridReadAppointment(appointmentId)" in bridge
    for forbidden in ("fetch(", "apiFetch(", "status-confirm", "proposals/status"):
        assert forbidden not in bridge
    assert "setAppointmentStatus: metaGridSetAppointmentStatus" in diary
    assert "/appointments/proposals/status/${appt.id}" in kernel
    assert "applySignedStatusProposal(appt, proposal" in kernel
    assert "await loadDiary(true)" in kernel


def test_other_command_families_exist_but_are_not_selected() -> None:
    spec = _text(OPENAPI)
    report = _text(REPORT)
    for operation in (
        "proposeAppointmentCreate",
        "proposeAppointmentUpdate",
        "proposeAppointmentStatus",
        "proposeAppointmentCheckIn",
        "proposeAppointmentDelete",
    ):
        assert f"operationId: {operation}" in spec
    assert "Another existing Diary command in Reception One" in report
    assert "`user_decision`" in report
    assert "explicitly forbids inferring another command-family choice" in report


def test_existing_meta_grid_proposals_do_not_smuggle_command_authority() -> None:
    source = _text(META_GRID)
    report = _text(REPORT)
    assert 'if (["resize", "cancel"].includes(payload.goal) && selected)' in source
    assert 'const isMove = payload.goal === "move";' in source
    assert 'posture: "proposal_only"' in source
    assert "operationalCommandAvailable: false" in source
    assert "Presentation reach therefore exceeds present command authority" in report


def test_candidate_matrix_preserves_every_recorded_gate() -> None:
    report = _text(REPORT)
    for phrase in (
        "Representative Stage 3B sessions",
        "`human_action`",
        "First external patient channel or identity flow",
        "Another event family",
        "Operational watcher/durability runtime",
        "`authority_closed`",
        "General visual polish",
        "`lower_leverage`",
        "must not become a\nruntime session object",
    ):
        assert phrase in report
