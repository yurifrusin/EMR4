from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "raisa-reception-one-multi-change-request-atomicity-orientation-plan.md"
)
ARCHITECTURE = (
    ROOT / "docs" / "raisa-reception-one-multi-change-request-atomicity-architecture.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-reception-one-multi-change-request-atomicity-orientation-threat-model-delta.md"
)
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-reception-one-multi-change-request-atomicity-orientation"
)
SCHEMA_PATH = CONTINUITY / "multi-change-action-atomicity-contract.schema.json"
CONTRACT_PATH = CONTINUITY / "multi-change-action-atomicity-contract.json"
UPDATE_SCHEMA = ROOT / "app" / "schemas" / "appointments.py"
ROUTER = ROOT / "app" / "routers" / "appointments.py"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"
UPDATE_TESTS = ROOT / "tests" / "test_appointment_update_proposal.py"
STATUS_TESTS = ROOT / "tests" / "test_appointment_status_mutations.py"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _class_fields(path: Path, class_name: str) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    klass = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    return [
        node.target.id
        for node in klass.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    ]


def test_contract_is_closed_and_schema_valid() -> None:
    schema = _json(SCHEMA_PATH)
    contract = _json(CONTRACT_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    assert contract["result"] == (
        "raisa_reception_one_multi_change_request_atomicity_orientation_pass"
    )
    assert contract["evidence_label"] == "repository_static_authored_synthetic"


def test_exact_update_and_status_schema_families_are_distinct() -> None:
    update_fields = _class_fields(UPDATE_SCHEMA, "AppointmentUpdateProposalIn")
    status_fields = _class_fields(UPDATE_SCHEMA, "AppointmentStatusProposalIn")
    assert update_fields == [
        "patient_id",
        "patient_name_provisional",
        "practitioner_id",
        "appointment_type_id",
        "location_id",
        "appointment_date",
        "start_time_local",
        "duration_minutes",
        "reason",
        "notes",
    ]
    assert status_fields == ["status", "waiting_area_id", "status_reason_code"]
    assert "status" not in update_fields

    openapi = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    components = openapi["components"]["schemas"]
    patch = components["AppointmentUpdateProposalCommand"]["properties"]["patch"]
    assert patch["additionalProperties"] is False
    assert list(patch["properties"]) == update_fields
    assert (
        components["AppointmentStatusProposalCommand"]["additionalProperties"] is False
    )


def test_existing_update_path_is_one_full_command_with_confirm_time_revalidation() -> (
    None
):
    source = ROUTER.read_text(encoding="utf-8")
    proposal = source[
        source.index("def propose_update_appointment(") : source.index(
            "def _bernie_tool_issue("
        )
    ]
    confirm = source[
        source.index("def confirm_update_proposal(") : source.index(
            "def _appointment_status_command_payload("
        )
    ]
    route = source[
        source.index("def confirm_update_proposal_route(") : source.index(
            "def propose_update_appointment("
        )
    ]
    apply_update = source[
        source.index("def _apply_appointment_update(") : source.index(
            '@router.put("/{appointment_id}"'
        )
    ]

    for field in (
        "practitioner_id",
        "appointment_date",
        "start_time_local",
        "duration_minutes",
    ):
        assert (
            f'incoming.get("{field}"' in proposal
            or f'"{field}" in incoming' in proposal
        )
        assert f"{field}=command.{field}" in confirm
    assert "command = AppointmentUpdateCommand(" in proposal
    assert "mint_signed_confirmation_evidence(" in proposal
    assert "revalidated = propose_update_appointment(" in confirm
    assert "if not _same_update_command(command, revalidated.command):" in confirm
    assert ".with_for_update()" in route
    assert "commit=False" in route
    assert "db.rollback()" in route
    assert "complete_appointment_command(" in route
    assert "db.commit()" in route
    assert "_write_audit(" in apply_update


def test_direct_evidence_is_narrower_than_structural_support() -> None:
    contract = _json(CONTRACT_PATH)
    update = contract["command_families"]["update"]
    directly_proven = set(update["directly_proven"])
    unproved = set(update["unproved"])
    assert (
        "date_time_duration_combined_confirmation_updates_one_appointment_and_one_audit"
        in directly_proven
    )
    assert (
        "successful_changed_practitioner_plus_time_plus_duration_confirmation"
        in unproved
    )

    tests = UPDATE_TESTS.read_text(encoding="utf-8")
    assert (
        "def test_update_proposal_confirm_payload_writes_with_signed_audit_evidence"
        in tests
    )
    assert '"appointment_date": THURSDAY.isoformat()' in tests
    assert '"start_time_local": "10:00:00"' in tests
    assert '"duration_minutes": 30' in tests
    assert "assert len(audit_rows) == 1" in tests
    assert "def test_update_confirm_rechecks_target_practitioner_activity" in tests


def test_same_family_composes_once_and_cross_family_never_auto_sequences() -> None:
    contract = _json(CONTRACT_PATH)
    rules = {row["classification"]: row for row in contract["composition_rules"]}
    same = rules["same_update_family"]
    assert same["fields"] == ["time", "duration", "practitioner"]
    assert same["execution"] == (
        "one_update_proposal_then_one_explicit_update_confirmation"
    )
    assert same["automatic_sequence"] is False

    cross = rules["cross_family"]
    assert "status" in cross["fields"] and "time" in cross["fields"]
    assert cross["presentation"] == (
        "non_executable_review_plan_with_no_all_or_nothing_claim"
    )
    assert cross["automatic_sequence"] is False
    assert contract["future_complex_button"]["cross_family_rule"] == (
        "requires_separately_proven_kernel_owned_atomic_command"
    )


def test_model_and_channel_candidates_have_no_button_or_command_authority() -> None:
    contract = _json(CONTRACT_PATH)
    console = contract["human_console"]
    boundary = contract["candidate_boundary"]
    assert console == {
        "operator": "authorised_human_staff",
        "action_order": ["status", "time", "duration", "practitioner"],
        "button_effect": "route_inert_presentation_only_editor_activation",
        "provider_model_can_press": False,
        "channel_adapter_can_press": False,
    }
    assert boundary["authority"] == {
        "dom": "none",
        "route": "none",
        "confirmation": "none",
        "write": "none",
    }
    assert {"email", "sms", "whatsapp", "voice", "external_chatbot"} <= set(
        boundary["origin_kinds"]
    )
    for example in contract["authored_synthetic_examples"]:
        assert example["write_authority"] == "none"
        assert example["confirmation_authority"] == "none"
        assert example["automatic_execution"] is False


def test_status_family_is_directly_separate_and_tamper_denies_write() -> None:
    contract = _json(CONTRACT_PATH)
    status = contract["command_families"]["status"]
    assert status["candidate_fields"] == ["status"]
    assert "atomic_status_plus_update_family_transaction" in status["unproved"]
    tests = STATUS_TESTS.read_text(encoding="utf-8")
    assert "def test_status_confirm_route_writes_once_with_signed_evidence" in tests
    assert "def test_status_confirm_route_blocks_tampered_status_without_write" in tests


def test_recorded_product_and_api_sources_are_unchanged() -> None:
    contract = _json(CONTRACT_PATH)
    for relative_path, expected_blob in contract["source_map"].items():
        observed = subprocess.check_output(
            ["git", "hash-object", relative_path],
            cwd=ROOT,
            text=True,
        ).strip()
        assert observed == expected_blob, relative_path


def test_plan_architecture_and_threat_keep_runtime_closed() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").split())
    architecture = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").split())
    assert "buttons are human presentation affordances" in plan
    assert "not provider- model actuators" in plan
    assert "semantic keyboard" in architecture
    assert "candidate has no DOM," in architecture
    assert "confirmation, route or write authority" in architecture
    assert "Classify it `cross_family`" in threat
    assert (
        "A future all-or-nothing cross-family action requires its own kernel command"
        in threat
    )
    assert "No product implementation" in plan


def test_native_scope_incidents_are_contained_without_protected_content() -> None:
    first = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-reception-one-multi-change-contract-map-native-scope-incident.json"
    )
    second = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-reception-one-multi-change-adapter-authority-native-protected-scope-incident.json"
    )
    assert first["incident_id"] == "AER-0306"
    assert second["incident_id"] == "AER-0307"
    assert first["sensitive_content_retained"] is False
    assert second["sensitive_content_retained"] is False
    assert (
        "complete_worker_output_quarantined_and_inadmissible" in second["containment"]
    )
    assert "tests/fixtures" not in json.dumps(second)


def test_next_rehearsal_is_kernel_first_and_ui_free() -> None:
    contract = _json(CONTRACT_PATH)
    architecture = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    assert contract["next_tranche"] == (
        "raisa_reception_one_same_update_family_multi_change_kernel_rehearsal"
    )
    assert "existing update proposal/confirm path" in architecture
    assert "It should change no UI" in architecture
    assert "Only after that rehearsal passes" in architecture
