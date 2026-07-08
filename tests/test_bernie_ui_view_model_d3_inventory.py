from pathlib import Path


INVENTORY = Path("docs/bernie-ui-derived-state-dag-d3-inventory.md")
DIARY_JS = Path("docs/diary/diary.js")


def _compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_inventory_maps_current_switch_points_to_view_model_fields():
    text = _compact(INVENTORY)

    for current in [
        "BERNIE_STATUS_COPY",
        "BERNIE_HEADLINE_COPY",
        "scrubBernieStaffCopy",
        "bernieStatusCopy",
        "bernieHeadlineCopy",
        "isBernieConfirmReady",
        "hasBernieSelectedSlotEvidence",
        "bernieReviewTransition",
        "bernieStatusCopyForPayload",
        "bernieHeadlineCopyForPayload",
        "bernieReviewActionCopy",
        "createBernieServerSessionBanner",
        "bernieComposerPlaceholder",
        "renderBernieReview",
        "handleBernieConfirmShortcut",
        "bernie-review-confirm-button",
    ]:
        assert current in text

    for field in [
        "session_phase",
        "clarification_state",
        "candidate_state",
        "proposal_state",
        "confirmation_state",
        "freshness_state",
        "identity_state",
        "copy_mode",
        "flags.show_confirm_button",
        "flags.enable_confirm_button",
        "flags.show_stale_warning",
    ]:
        assert field in text


def test_inventory_is_d3_only_and_keeps_d4_wiring_blocked():
    text = _compact(INVENTORY)

    for phrase in [
        "inventory/review only",
        "docs/diary/diary.js`. This file remains unchanged in D3",
        "D4 should use route-intercepted fixtures only",
        "must not reimplement the Python selector in frontend JavaScript",
        "UI wiring into `docs/diary/diary.js`",
        "route or response wiring for `BernieUiViewModel`",
        "provider prompt or provider dry-run wiring",
        "model-to-database writes",
    ]:
        assert phrase in text


def test_inventory_preserves_command_payload_boundary():
    text = _compact(INVENTORY)

    for phrase in [
        "command payloads must still use existing signed proposal/freshness/evidence fields",
        "must not include `BernieUiViewModel` fields",
        "bernie-review-confirm-button",
        "out of scope for view-model fields",
        "existing signed REST command handlers",
    ]:
        assert phrase in text


def test_inventory_switch_points_exist_in_current_diary_source():
    source = DIARY_JS.read_text(encoding="utf-8", errors="replace")

    for current in [
        "const BERNIE_STATUS_COPY",
        "const BERNIE_HEADLINE_COPY",
        "function scrubBernieStaffCopy",
        "function bernieStatusCopy",
        "function bernieHeadlineCopy",
        "function isBernieConfirmReady",
        "function hasBernieSelectedSlotEvidence",
        "function bernieReviewTransition",
        "function bernieStatusCopyForPayload",
        "function bernieHeadlineCopyForPayload",
        "function bernieReviewActionCopy",
        "function createBernieServerSessionBanner",
        "function bernieComposerPlaceholder",
        "function renderBernieReview",
        "function handleBernieConfirmShortcut",
        "bernie-review-confirm-button",
    ]:
        assert current in source


def test_inventory_keeps_provider_memory_trove_graphql_and_write_gates_closed():
    text = _compact(INVENTORY)

    for phrase in [
        "live provider evidence",
        "memory/RAG/GraphRAG runtime wiring",
        "H15/H-series runtime imports",
        "historical diary material access",
        "GraphQL resolvers or mutations",
        "appointment writes outside existing signed REST command handlers",
    ]:
        assert phrase in text
