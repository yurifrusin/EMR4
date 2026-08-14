from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "orchestration" / "api_spine_confirm_client_surface_checkpoint.md"
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_confirm_client_checkpoint_names_all_covered_surfaces():
    text = _read(CHECKPOINT)

    for phrase in (
        "Create proposal",
        "Staff create confirm",
        "Bernie create confirm",
        "Ordinary update confirm",
        "Status confirm",
        "Delete confirm",
        "Covered",
    ):
        assert phrase in text


def test_confirm_client_checkpoint_keeps_remaining_decisions_separate():
    text = _read(CHECKPOINT)

    for phrase in (
        "Bernie tool-intent update confirm",
        "Proposal-only update/status/waiting-area/delete",
        "Strict `minLength: 8` runtime enforcement",
        "confirmBernieToolIntentChange()` sends `update-confirm-<freshness>`",
        "Deferred, broader",
        "Deferred, compatibility hardening",
    ):
        assert phrase in text

    assert "not** using the next sprint on strict `minLength: 8`" in text
    assert "real non-intercepted click can fail" in text


def test_confirm_client_checkpoint_recommends_tool_intent_then_review_prep():
    text = _read(CHECKPOINT)

    for phrase in (
        "Recommended Sprint 159",
        'wire `confirmBernieToolIntentChange()`',
        "freshness-derived key from `update_proposal_freshness_id`",
        "tool-intent confirm click",
        "After Sprint 159, recommended Sprint 160",
        "Bernie/Diary review-readiness packet",
        "provider-boundary/readiness commands",
        "Pause for Yuri after the Sprint 160 packet",
    ):
        assert phrase in text


def test_confirm_client_checkpoint_closed_gates_remain_closed():
    text = _read(CHECKPOINT)

    for phrase in (
        "live provider enablement",
        "runtime memory/RAG/GraphRAG wiring",
        "H15/H-series runtime imports",
        "broad historical diary material access",
        "GraphQL mutations",
        "raw compatibility write idempotency changes",
        "backend idempotency ledger changes",
    ):
        assert phrase in text


def test_diary_client_surface_matches_checkpoint_summary():
    source = _read(DIARY_JS)

    for phrase in (
        "idempotencyHeadersFor(ensureElementIdempotencyKey(saveBtn))",
        "idempotencyHeadersFor(ensureElementConfirmIdempotencyKey(saveBtn))",
        '"create-confirm-bernie"',
        "updateConfirmIdempotencyKey(proposal, confirmPayload)",
        "statusConfirmIdempotencyKey(proposal, confirmPayload)",
        "deleteConfirmIdempotencyKey(proposal, confirmPayload)",
    ):
        assert phrase in source

    tool_intent_start = source.index("async function confirmBernieToolIntentChange(")
    next_function = source.index("\nfunction ", tool_intent_start)
    tool_intent = source[tool_intent_start:next_function]
    assert "apiFetch(allowlistedConfirmApiPath(envelope.confirm_endpoint)" in tool_intent
    assert "updateConfirmIdempotencyKey(envelope, confirmPayload)" in tool_intent
    assert "headers: confirmHeaders" in tool_intent
