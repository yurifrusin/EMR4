from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "orchestration" / "api_spine_appointment_idempotency_storage_design.md"


def test_storage_design_records_scope_and_source_pass():
    text = DESIGN.read_text(encoding="utf-8")

    assert "# API Spine Appointment Idempotency Storage Design" in text
    assert "| Sprint | 126 |" in text
    assert "Storage design only; no model, migration, route behavior" in text
    for source in (
        "orchestration/api_spine_appointment_idempotency_policy_packet.md",
        "orchestration/api_spine_appointment_idempotency_gap.md",
        "docs/api-spine/openapi/appointment-commands.yaml",
        "app/routers/appointments.py",
        "app/models/appointments.py",
        "app/models/audit.py",
        "alembic/versions/",
    ):
        assert f"`{source}`" in text


def test_storage_design_defines_required_columns_and_constraints():
    text = DESIGN.read_text(encoding="utf-8")

    for column in (
        "practice_id",
        "actor_user_id",
        "actor_role",
        "operation_id",
        "route_family",
        "idempotency_key_hash",
        "request_body_hash",
        "state",
        "response_body_json",
        "target_appointment_id",
        "audit_log_id",
        "expires_at",
    ):
        assert f"`{column}`" in text
    assert "unique `(practice_id, actor_user_id, operation_id, idempotency_key_hash)`" in text
    assert "completed rows have `response_status_code`, `response_body_hash`, and" in text
    assert "explicit scoped service identity, not a null or shared placeholder" in text


def test_storage_design_pins_alias_operation_identity():
    text = DESIGN.read_text(encoding="utf-8")

    for phrase in (
        "`POST /appointments/proposals/create/confirm-bernie` | `confirmAppointmentCreateProposal`",
        "`POST /appointments/proposals/status-confirm` | `confirmAppointmentStatusProposal`",
        "`POST /appointments/proposals/delete-confirm` | `confirmAppointmentDeleteProposal`",
        "Alias naming must not weaken command-plane policy",
    ):
        assert phrase in text


def test_storage_design_defines_canonical_hashing():
    text = DESIGN.read_text(encoding="utf-8")

    for phrase in (
        "sort object keys recursively",
        "compact separators with no insignificant whitespace",
        "normalize UUIDs, dates, times, and datetimes",
        "exclude transient request metadata such as correlation id",
        "SHA-256 over UTF-8 canonical JSON",
        "HMAC/SHA-256 hashed with a server secret",
    ):
        assert phrase in text


def test_storage_design_requires_ledger_lock_before_write_and_atomic_commit():
    text = DESIGN.read_text(encoding="utf-8")

    ordered_phrases = (
        "insert an `in_progress` ledger row",
        "If insert conflicts, lock the existing row",
        "Only the transaction that owns the new `in_progress` row",
        "Perform the appointment mutation, audit write, and ledger completion",
        "Commit only after the appointment mutation, audit evidence, and completed ledger response",
    )
    cursor = -1
    for phrase in ordered_phrases:
        next_pos = text.find(phrase)
        assert next_pos > cursor
        cursor = next_pos
    assert "concurrent same-key requests cannot both write" in text
    assert "Lock ordering must be ledger-first and appointment-row-second" in text
    assert "mixed ordering could deadlock under retries" in text


def test_storage_design_defines_replay_and_recovery_semantics():
    text = DESIGN.read_text(encoding="utf-8")

    for phrase in (
        "returns the stored response, including the same appointment id",
        "`409 idempotency_key_conflict`",
        "actor role changes do not create a second write",
        "No appointment write may commit without the matching completed ledger row",
        "A crash before transaction commit leaves no durable write",
        "A crash after transaction commit leaves both the appointment/audit result",
        "Stored-response replay should be visible to compliance",
        "without looking like a second appointment mutation",
        "Stale `in_progress` rows require a reviewed recovery policy",
        "avoid a second",
        "Confirmation-write `completed` rows do not expire by default",
        "Any TTL for",
        "non-confirmation proposal/read rows",
    ):
        assert phrase in text


def test_storage_design_records_deepseek_residuals_as_requirements():
    text = DESIGN.read_text(encoding="utf-8")

    for phrase in (
        "stale `in_progress` recovery cannot create a second appointment",
        "any non-confirmation TTL policy is explicit",
        "stored-response replay produces replay-specific audit/telemetry evidence",
        "future system/integration actors use explicit scoped identities",
        "lock ordering is ledger-first and appointment-row-second",
    ):
        assert phrase in text


def test_storage_design_keeps_gates_closed_and_names_next_slice():
    text = DESIGN.read_text(encoding="utf-8")

    assert "Recommended Sprint 127" in text
    assert "Appointment command idempotency storage artifact guard" in text
    for closed_gate in (
        "live providers",
        "runtime FGA clients",
        "external patient clients",
        "GraphQL mutations",
        "broad historical diary trove mining",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ):
        assert closed_gate in text
