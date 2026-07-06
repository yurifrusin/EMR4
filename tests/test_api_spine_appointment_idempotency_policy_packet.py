from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "orchestration" / "api_spine_appointment_idempotency_policy_packet.md"


def test_policy_packet_records_scope_and_source_pass():
    text = POLICY.read_text(encoding="utf-8")

    assert "# API Spine Appointment Idempotency Policy Packet" in text
    assert "| Sprint | 125 |" in text
    assert "Policy packet only; no route behavior" in text
    for source in (
        "docs/api-spine/openapi/appointment-commands.yaml",
        "orchestration/api_spine_appointment_idempotency_gap.md",
        "orchestration/api_spine_appointment_command_alignment_inventory.md",
        "app/routers/appointments.py",
        "app/services/bernie/session_store.py",
    ):
        assert f"`{source}`" in text


def test_policy_packet_defines_route_family_decisions():
    text = POLICY.read_text(encoding="utf-8")

    for phrase in (
        "Proposal routes in OpenAPI",
        "Confirmation routes in OpenAPI",
        "Backend alias confirmation routes",
        "Bernie create confirmation",
        "Slot-search command-style reads",
        "Bernie intent/interpreter/supervised/no-slot command-style reads",
        "Raw compatibility writes",
    ):
        assert phrase in text
    assert "Alias naming must not weaken command-plane policy" in text
    assert "Explicit migration decision required before enforcement" in text


def test_policy_packet_defines_replay_ledger_binding_and_uniqueness():
    text = POLICY.read_text(encoding="utf-8")

    for field in (
        "practice_id",
        "actor_user_id",
        "actor_role",
        "operation_id",
        "route_family",
        "idempotency_key_hash",
        "request_body_hash",
        "target_appointment_id",
        "expires_at",
    ):
        assert f"`{field}`" in text
    assert "unique `(practice_id, actor_user_id, operation_id, idempotency_key_hash)`" in text
    assert "409 idempotency_key_conflict" in text
    assert "confirmation-write entries should not expire" in text


def test_policy_packet_preserves_confirmation_safety_ordering():
    text = POLICY.read_text(encoding="utf-8")

    ordered_phrases = (
        "Authenticate and resolve practice/actor",
        "Require and normalize `Idempotency-Key`",
        "Create or lock the replay ledger row",
        "run existing confirmation checks",
        "Perform the appointment write once",
        "same transaction",
    )
    cursor = -1
    for phrase in ordered_phrases:
        next_pos = text.find(phrase)
        assert next_pos > cursor
        cursor = next_pos
    assert "Idempotency must not bypass signed confirmation evidence" in text


def test_policy_packet_resolves_storage_design_hazards_for_next_sprint():
    text = POLICY.read_text(encoding="utf-8")

    for phrase in (
        "sorted object keys",
        "no insignificant whitespace",
        "backend aliases must share the same semantic `operation_id`",
        "status-confirm` shares `confirmAppointmentStatusProposal",
        "delete-confirm` shares `confirmAppointmentDeleteProposal",
        "actor_role` is stored for audit",
        "a later role change by the same user cannot create a second write",
        "Confirmation writes must not commit unless the replay ledger result is committed too",
    ):
        assert phrase in text


def test_policy_packet_requires_duplicate_write_regression_tests():
    text = POLICY.read_text(encoding="utf-8")

    for phrase in (
        "creates only one appointment",
        "does not repeat the mutation",
        "keys are scoped by practice, actor, and operation",
        "missing key on enforced confirmation routes fails",
        "stale proposal evidence still blocks",
        "without exposing raw request bodies",
    ):
        assert phrase in text


def test_policy_packet_keeps_gates_closed_and_names_next_slice():
    text = POLICY.read_text(encoding="utf-8")

    assert "Recommended Sprint 126" in text
    assert "Appointment command idempotency storage design" in text
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
