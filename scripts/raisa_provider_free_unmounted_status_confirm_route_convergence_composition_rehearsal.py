"""Run the provider-free, unmounted status-confirm composition rehearsal."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterator

from jsonschema import Draft202012Validator

from app.services.appointment_status_composition import (
    StatusConfirmCompositionResult,
    StatusConfirmEffectResult,
    StatusConfirmServerIngress,
    canonical_status_confirm_envelope_bytes,
    compose_status_confirm,
    status_confirm_envelope_projection,
)
from app.services.appointment_status_physical import (
    STATUS_CONFIRM_RECEIPT_VERSION,
    StatusConfirmAuthorityRevoked,
    StatusConfirmPhysicalDecision,
    StatusConfirmScaffoldIncomplete,
    StatusConfirmTargetUnavailable,
)
from scripts.raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract import (
    adapt,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal"
)
CONTRACT_PATH = OUT / "composition-contract.json"
SCHEMA_PATH = OUT / "composition-contract.schema.json"
EVIDENCE_PATH = OUT / "provider-free-composition-evidence.json"

APPOINTMENT_ID = "11111111-1111-4111-8111-111111111111"
PRACTICE_ID = "22222222-2222-4222-8222-222222222222"
ACTOR_ID = "33333333-3333-4333-8333-333333333333"
PRACTITIONER_ID = "44444444-4444-4444-8444-444444444444"
AUDIT_ID = "55555555-5555-4555-8555-555555555555"

SOURCE_BINDINGS = [
    {
        "path": "app/routers/appointments.py",
        "sha256": "59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb",
    },
    {
        "path": "app/schemas/appointments.py",
        "sha256": "d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d",
    },
    {
        "path": "docs/api-spine/openapi/appointment-commands.yaml",
        "sha256": "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6",
    },
    {
        "path": "app/services/appointment_idempotency.py",
        "sha256": "c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410",
    },
    {
        "path": "app/services/appointment_status_physical.py",
        "sha256": "4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b",
    },
    {
        "path": "app/models/appointments.py",
        "sha256": "d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915",
    },
    {
        "path": "scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py",
        "sha256": "a45b601a375c7dec7ee08e46be53e23991542cf9699a9ac75798c2e70d2865d8",
    },
    {
        "path": "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture.md",
        "sha256": "aa2eab6fddc0f8394ea3950965d525222917506a04b0ef10ab22999e2e442363",
    },
    {
        "path": "docs/raisa-provider-free-read-only-status-confirm-route-mounting-admission-review-closeout.md",
        "sha256": "cfc63d42c16de0c62ee19a6df7d29a374479c890bb52e7fd0c7398739a5fb933",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_transport() -> dict[str, Any]:
    return {
        "operation_id": "confirmAppointmentStatusProposal",
        "route_family": "status-confirm",
        "idempotency_key": "authored-synthetic-key-001",
        "confirmed": True,
        "proposal_intent": "update_appointment_status",
        "proposal_safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "execute_with_report",
        "command": {
            "kind": "status",
            "appointment_id": APPOINTMENT_ID,
            "status": "Confirmed",
            "status_reason_code": None,
            "waiting_area_id": None,
            "waiting_area_id_supplied": False,
            "clears_waiting_area": False,
        },
        "proposal_warning_codes": [],
        "confirmed_warning_codes": [],
        "freshness_id": "fresh-authored-synthetic-001",
        "signed_evidence_required": True,
    }


def base_ingress() -> StatusConfirmServerIngress:
    return StatusConfirmServerIngress(
        practice_id=PRACTICE_ID,
        actor_id=ACTOR_ID,
        actor_role="Receptionist",
        session_id="session-authored-synthetic-001",
        authority_current=True,
        current_state={
            "appointment_id": APPOINTMENT_ID,
            "status": "Booked",
            "status_reason_code": None,
            "waiting_area_id": None,
            "source_version": 7,
        },
        expected_freshness_id="fresh-authored-synthetic-001",
        evidence_status="verified",
        evidence_purpose="appointment.status.confirm.v1",
        expected_evidence_purpose="appointment.status.confirm.v1",
        evidence_binding="exact",
    )


def successful_envelope(status: str = "Confirmed") -> dict[str, Any]:
    return {
        "intent": "confirm_status_appointment",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "confirmed_write",
        "summary": "Confirmed status proposal and updated one appointment.",
        "appointment": {
            "id": APPOINTMENT_ID,
            "practice_id": PRACTICE_ID,
            "patient_id": None,
            "patient_name_provisional": None,
            "practitioner_id": PRACTITIONER_ID,
            "appointment_type_id": None,
            "location_id": None,
            "start_time": "2026-08-12T09:00:00+10:00",
            "appointment_date": "2026-08-12",
            "start_time_local": "09:00:00",
            "end_time": "2026-08-12T09:15:00+10:00",
            "duration_minutes": 15,
            "status": status,
            "reason": None,
            "notes": None,
            "cancellation_reason": None,
            "status_reason_code": None,
            "booked_via": "Receptionist",
            "waiting_room": None,
            "waiting_area_id": None,
            "queue_position": None,
            "created_at": "2026-08-12T08:00:00+10:00",
            "patient": None,
            "practitioner": {
                "id": PRACTITIONER_ID,
                "first_name": "Authored",
                "last_name": "Synthetic",
                "provider_number": None,
                "ahpra_number": None,
            },
            "appointment_type": None,
            "breaks_overlap": [],
        },
        "warnings": [],
        "blocks": [],
        "audit_evidence": ["status_confirmation_explicit"],
    }


class FakeDatabase:
    def __init__(self, mode: str = "new_command") -> None:
        self.mode = mode
        self.appointment = SimpleNamespace(
            id=APPOINTMENT_ID,
            practice_id=PRACTICE_ID,
            status="Booked",
            status_reason_code=None,
            waiting_area_id=None,
            appointment_state_version=7,
        )
        self.record: Any = None
        self.transaction_calls = 0
        self.effect_count = 0
        self.audit_count = 0
        self.commit_count = 0
        self.rollback_count = 0

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(
            {
                "appointment": self.appointment,
                "record": self.record,
                "effect_count": self.effect_count,
                "audit_count": self.audit_count,
                "commit_count": self.commit_count,
            }
        )

    def restore(self, snapshot: dict[str, Any]) -> None:
        self.appointment = snapshot["appointment"]
        self.record = snapshot["record"]
        self.effect_count = snapshot["effect_count"]
        self.audit_count = snapshot["audit_count"]
        self.commit_count = snapshot["commit_count"]


def _new_record(arguments: Mapping[str, Any]) -> Any:
    return SimpleNamespace(
        state="in_progress",
        operation_id="confirmAppointmentStatusProposal",
        route_family="status-confirm",
        actor_role=arguments["actor_role"],
        request_body_hash=arguments["request_body_hash"],
        session_binding_digest=arguments["session_binding_digest"],
        response_status_code=None,
        response_body_json=None,
        response_body_hash=None,
        result_kind=None,
        target_appointment_id=arguments["target_appointment_id"],
        audit_log_id=None,
        completed_receipt_version=None,
        pre_state_version=None,
        post_state_version=None,
        response_body_canonical_bytes=None,
    )


@contextmanager
def fake_transaction(db: FakeDatabase, **arguments: Any) -> Iterator[StatusConfirmPhysicalDecision]:
    db.transaction_calls += 1
    snapshot = db.snapshot()
    try:
        if db.mode == "authority_revoked":
            raise StatusConfirmAuthorityRevoked("authored-synthetic revocation")
        if db.mode == "target_unavailable":
            raise StatusConfirmTargetUnavailable("authored-synthetic target loss")
        if db.mode == "new_command" or db.mode == "incomplete_scaffold":
            db.record = _new_record(arguments)
            kind = "new_command"
            response_bytes = None
        else:
            if db.record is None:
                db.record = _new_record(arguments)
            kind = db.mode
            response_bytes = (
                db.record.response_body_canonical_bytes if kind == "replay" else None
            )
        decision = StatusConfirmPhysicalDecision(
            kind=kind,
            appointment=db.appointment,
            record=db.record,
            pre_state_version=db.appointment.appointment_state_version,
            response_body_canonical_bytes=response_bytes,
        )
        yield decision
        if db.mode == "incomplete_scaffold":
            raise StatusConfirmScaffoldIncomplete("authored-synthetic incomplete write set")
        if kind == "new_command":
            if (
                db.record.completed_receipt_version != STATUS_CONFIRM_RECEIPT_VERSION
                or db.record.audit_log_id is None
                or db.record.post_state_version != db.record.pre_state_version + 1
                or db.appointment.appointment_state_version != db.record.post_state_version
            ):
                raise StatusConfirmScaffoldIncomplete("authored-synthetic incomplete receipt")
            db.commit_count += 1
    except Exception:
        db.restore(snapshot)
        db.rollback_count += 1
        raise


def locked_server(appointment: Any, ingress: StatusConfirmServerIngress) -> dict[str, Any]:
    value = ingress.as_adapter_mapping()
    value["current_state"] = {
        "appointment_id": str(appointment.id),
        "status": str(appointment.status),
        "status_reason_code": appointment.status_reason_code,
        "waiting_area_id": appointment.waiting_area_id,
        "source_version": appointment.appointment_state_version,
    }
    return value


def locked_server_stale(
    appointment: Any, ingress: StatusConfirmServerIngress
) -> dict[str, Any]:
    value = locked_server(appointment, ingress)
    value["current_state"]["source_version"] += 1
    return value


def stage_effect(
    decision: StatusConfirmPhysicalDecision, request: Mapping[str, Any]
) -> StatusConfirmEffectResult:
    appointment = decision.appointment
    appointment.status = request["command"]["status"]
    appointment.status_reason_code = request["command"]["status_reason_code"]
    appointment.waiting_area_id = request["command"]["waiting_area_id"]
    appointment.appointment_state_version += 1
    return StatusConfirmEffectResult(successful_envelope(), AUDIT_ID)


def compose(
    db: FakeDatabase,
    *,
    transport: dict[str, Any] | None = None,
    ingress: StatusConfirmServerIngress | None = None,
    locked_factory: Any = locked_server,
    effect: Any = stage_effect,
) -> StatusConfirmCompositionResult:
    def counted_effect(decision: Any, request: Mapping[str, Any]) -> Any:
        db.effect_count += 1
        db.audit_count += 1
        return effect(decision, request)

    return compose_status_confirm(
        transport or base_transport(),
        server_ingress=ingress or base_ingress(),
        db=db,
        idempotency_secret=b"authored-synthetic-idempotency-secret",
        session_binding_secret=b"authored-synthetic-session-secret",
        admission_adapter=adapt,
        locked_server_factory=locked_factory,
        stage_effect=counted_effect,
        practice_is_active=lambda _practice: True,
        current_authority=lambda _practice, _appointment: True,
        transaction_factory=fake_transaction,
    )


def _scenario_row(
    scenario_id: str,
    result: StatusConfirmCompositionResult,
    db: FakeDatabase,
    *,
    expected_kind: str,
    expected_status: int,
    expected_effects: int,
    expected_commits: int,
) -> dict[str, Any]:
    passed = (
        result.kind == expected_kind
        and result.status_code == expected_status
        and db.effect_count == expected_effects
        and db.commit_count == expected_commits
    )
    return {
        "id": scenario_id,
        "result_kind": result.kind,
        "status_code": result.status_code,
        "effect_count": db.effect_count,
        "audit_count": db.audit_count,
        "commit_count": db.commit_count,
        "rollback_count": db.rollback_count,
        "stored_body_released": result.stored_response_bytes is not None,
        "passed": passed,
    }


def run_scenarios() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    committed_db = FakeDatabase()
    committed = compose(committed_db)
    rows.append(_scenario_row("src-001-clean-execute", committed, committed_db, expected_kind="committed", expected_status=200, expected_effects=1, expected_commits=1))

    committed_db.mode = "replay"
    replay = compose(committed_db)
    replay_row = _scenario_row("src-002-same-digest-replay", replay, committed_db, expected_kind="replay", expected_status=200, expected_effects=1, expected_commits=1)
    replay_row["byte_identical"] = committed.stored_response_bytes == replay.stored_response_bytes
    replay_row["passed"] = replay_row["passed"] and replay_row["byte_identical"]
    rows.append(replay_row)

    for scenario_id, mode, kind, status in (
        ("src-003-different-digest-conflict", "conflict", "error", 409),
        ("src-004-authority-revoked", "authority_revoked", "error", 403),
        ("src-005-target-unavailable", "target_unavailable", "error", 404),
    ):
        db = FakeDatabase(mode)
        rows.append(_scenario_row(scenario_id, compose(db), db, expected_kind=kind, expected_status=status, expected_effects=0, expected_commits=0))

    incomplete_db = FakeDatabase("incomplete_scaffold")
    rows.append(_scenario_row("src-006-incomplete-scaffold", compose(incomplete_db), incomplete_db, expected_kind="error", expected_status=503, expected_effects=0, expected_commits=0))

    stale_db = FakeDatabase()
    rows.append(_scenario_row("src-007-locked-generation-changed", compose(stale_db, locked_factory=locked_server_stale), stale_db, expected_kind="blocked", expected_status=200, expected_effects=0, expected_commits=0))

    waiting = base_transport()
    waiting["proposal_intent"] = "update_appointment_waiting_area"
    waiting_db = FakeDatabase()
    rows.append(_scenario_row("src-008-waiting-area-discriminated", compose(waiting_db, transport=waiting), waiting_db, expected_kind="blocked", expected_status=200, expected_effects=0, expected_commits=0))

    warnings = base_transport()
    warnings["proposal_warning_codes"] = ["synthetic_warning"]
    warnings_db = FakeDatabase()
    rows.append(_scenario_row("src-009-warning-mismatch", compose(warnings_db, transport=warnings), warnings_db, expected_kind="blocked", expected_status=200, expected_effects=0, expected_commits=0))

    terminal_ingress = replace(base_ingress(), current_state={**base_ingress().current_state, "status": "Completed"})
    terminal_db = FakeDatabase()
    rows.append(_scenario_row("src-010-terminal-transition-deferred", compose(terminal_db, ingress=terminal_ingress), terminal_db, expected_kind="blocked", expected_status=200, expected_effects=0, expected_commits=0))

    corrupt_db = copy.deepcopy(committed_db)
    corrupt_db.mode = "replay"
    corrupt_db.record.response_body_canonical_bytes += b" "
    rows.append(_scenario_row("src-011-corrupt-stored-bytes", compose(corrupt_db), corrupt_db, expected_kind="error", expected_status=503, expected_effects=1, expected_commits=1))

    response_loss_db = FakeDatabase()
    first = compose(response_loss_db)
    response_loss_db.mode = "replay"
    recovered = compose(response_loss_db)
    row = _scenario_row("src-012-response-loss-recovery", recovered, response_loss_db, expected_kind="replay", expected_status=200, expected_effects=1, expected_commits=1)
    row["byte_identical"] = first.stored_response_bytes == recovered.stored_response_bytes
    row["passed"] = row["passed"] and row["byte_identical"]
    rows.append(row)
    return rows


def _set_path(value: Any, path: tuple[Any, ...], replacement: Any) -> Any:
    candidate = copy.deepcopy(value)
    cursor = candidate
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = replacement
    return candidate


def hostile_inputs() -> list[dict[str, Any]]:
    base = base_transport()
    mutations: list[dict[str, Any]] = []
    values = [
        (("operation_id",), "rawStatusPatch"),
        (("operation_id",), ""),
        (("route_family",), "status"),
        (("route_family",), ""),
        (("proposal_intent",), "update_appointment_waiting_area"),
        (("proposal_intent",), "delete_appointment"),
        (("command", "kind"), "waiting_area"),
        (("command", "kind"), ""),
        (("command", "appointment_id"), "other-target"),
        (("idempotency_key",), ""),
        (("idempotency_key",), " "),
        (("confirmed",), False),
        (("confirmed",), None),
        (("proposal_safe",), False),
        (("requires_confirmation",), False),
        (("autonomy_tier",), "blocked"),
        (("autonomy_tier",), "autonomous"),
        (("signed_evidence_required",), False),
        (("freshness_id",), "stale"),
        (("proposal_warning_codes",), ["warning-a"]),
        (("confirmed_warning_codes",), ["warning-a"]),
        (("proposal_warning_codes",), ["warning-a", "warning-a"]),
        (("confirmed_warning_codes",), ["warning-a", "warning-a"]),
        (("proposal_warning_codes",), "warning-a"),
        (("confirmed_warning_codes",), "warning-a"),
    ]
    for path, replacement in values:
        mutations.append(_set_path(base, path, replacement))
    for key in (
        "operation_id",
        "route_family",
        "idempotency_key",
        "confirmed",
        "proposal_intent",
        "proposal_safe",
        "requires_confirmation",
        "autonomy_tier",
        "command",
        "proposal_warning_codes",
        "confirmed_warning_codes",
        "freshness_id",
        "signed_evidence_required",
    ):
        candidate = copy.deepcopy(base)
        candidate.pop(key)
        mutations.append(candidate)
    for key in (
        "kind",
        "appointment_id",
        "status",
        "status_reason_code",
        "waiting_area_id",
        "waiting_area_id_supplied",
        "clears_waiting_area",
    ):
        candidate = copy.deepcopy(base)
        candidate["command"].pop(key)
        mutations.append(candidate)
    return mutations


def hostile_responses() -> list[dict[str, Any]]:
    base = successful_envelope()
    variants = []
    top_level = (
        "intent",
        "safe",
        "requires_confirmation",
        "autonomy_tier",
        "summary",
        "appointment",
        "warnings",
        "blocks",
        "audit_evidence",
    )
    for key in top_level:
        candidate = copy.deepcopy(base)
        candidate.pop(key)
        variants.append(candidate)
    for path, value in (
        (("intent",), "confirm_update_appointment"),
        (("safe",), False),
        (("requires_confirmation",), True),
        (("autonomy_tier",), "blocked"),
        (("appointment", "id"), "66666666-6666-4666-8666-666666666666"),
        (("appointment", "status"), "Booked"),
        (("blocks",), [{"code": "x", "severity": "blocked", "message": "x"}]),
        (("warnings",), [{"code": "x", "severity": "blocked", "message": "x"}]),
        (("warnings",), [{"code": "x", "severity": "warning", "message": "x"}]),
        (("warnings",), [{"code": "x", "severity": "warning", "message": "x"}, {"code": "x", "severity": "warning", "message": "x"}]),
    ):
        variants.append(_set_path(base, path, value))
    candidate = copy.deepcopy(base)
    candidate["unexpected"] = True
    variants.append(candidate)
    return variants


def run_hostile_mutations() -> dict[str, int]:
    attempted = 0
    rejected = 0
    for transport in hostile_inputs():
        attempted += 1
        db = FakeDatabase()
        result = compose(db, transport=transport)
        if result.kind != "committed" and db.commit_count == 0:
            rejected += 1
    for envelope in hostile_responses():
        attempted += 1
        db = FakeDatabase()

        def invalid_effect(_decision: Any, _request: Any, body: Any = envelope) -> Any:
            return StatusConfirmEffectResult(body, AUDIT_ID)

        result = compose(db, effect=invalid_effect)
        if result.kind != "committed" and db.commit_count == 0:
            rejected += 1
    if attempted < 50 or rejected != attempted:
        raise ValueError(f"hostile mutation rejection incomplete: {rejected}/{attempted}")
    return {"attempted": attempted, "rejected": rejected}


def build_contract() -> dict[str, Any]:
    return {
        "schema_version": "raisa.status-confirm-route-composition-contract.v1",
        "source_head": "83db576fc2c95f513de38ae57d5b4b1ac6fe5027",
        "mode": "provider_free_authored_synthetic_unmounted",
        "source_bindings": SOURCE_BINDINGS,
        "composition_order": [
            "status_only_admission",
            "server_owned_ingress",
            "request_and_session_digests",
            "physical_transaction",
            "locked_readmission",
            "atomic_effect_and_complete_envelope_receipt",
            "stored_initial_or_replay_delivery",
        ],
        "scenario_ids": [f"src-{index:03d}" for index in range(1, 13)],
        "canonical_response": {
            "storage": "complete_current_public_envelope_bytes",
            "json_matches_bytes": True,
            "hash_matches_bytes": True,
            "five_field_status_projection_is_response": False,
            "initial_and_replay_byte_identical": True,
        },
        "implementation_authorized": False,
        "forbidden": {
            "route_mount_or_call": False,
            "real_database_or_source": False,
            "product_or_patient_data": False,
            "provider_or_network": False,
            "credential_or_iam": False,
            "external_tool_or_product_command": False,
            "deployment_or_release": False,
            "pages_or_protected_ref": False,
        },
        "next_candidate": "provider_free_read_only_status_confirm_route_mounting_readiness_rereview",
    }


def build_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "source_head",
            "mode",
            "source_bindings",
            "composition_order",
            "scenario_ids",
            "canonical_response",
            "implementation_authorized",
            "forbidden",
            "next_candidate",
        ],
        "properties": {
            "schema_version": {"const": "raisa.status-confirm-route-composition-contract.v1"},
            "source_head": {"const": "83db576fc2c95f513de38ae57d5b4b1ac6fe5027"},
            "mode": {"const": "provider_free_authored_synthetic_unmounted"},
            "source_bindings": {"type": "array", "minItems": 9, "maxItems": 9},
            "composition_order": {"type": "array", "minItems": 7, "maxItems": 7},
            "scenario_ids": {"type": "array", "minItems": 12, "maxItems": 12},
            "canonical_response": {
                "type": "object",
                "required": [
                    "storage",
                    "json_matches_bytes",
                    "hash_matches_bytes",
                    "five_field_status_projection_is_response",
                    "initial_and_replay_byte_identical",
                ],
            },
            "implementation_authorized": {"const": False},
            "forbidden": {
                "type": "object",
                "additionalProperties": {"const": False},
            },
            "next_candidate": {
                "const": "provider_free_read_only_status_confirm_route_mounting_readiness_rereview"
            },
        },
    }


def validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator(schema).validate(contract)
    if contract["source_bindings"] != SOURCE_BINDINGS:
        raise ValueError("source bindings differ from the frozen contract")
    for source in SOURCE_BINDINGS:
        if _sha256(ROOT / source["path"]) != source["sha256"]:
            raise ValueError("source hash mismatch: " + source["path"])
    if set(contract["forbidden"].values()) != {False}:
        raise ValueError("forbidden authority opened")


def build_evidence() -> dict[str, Any]:
    contract = build_contract()
    schema = build_schema()
    validate_contract(contract, schema)
    scenarios = run_scenarios()
    if not all(row["passed"] for row in scenarios):
        failed = [row["id"] for row in scenarios if not row["passed"]]
        raise ValueError("composition scenarios failed: " + ", ".join(failed))
    envelope_bytes = canonical_status_confirm_envelope_bytes(successful_envelope())
    return {
        "schema_version": "raisa.status-confirm-route-composition-evidence.v1",
        "result": "raisa_provider_free_unmounted_status_confirm_route_convergence_composition_rehearsal_pass",
        "source_head": contract["source_head"],
        "source_hashes": {item["path"]: item["sha256"] for item in SOURCE_BINDINGS},
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "hostile_mutations": run_hostile_mutations(),
        "canonical_response_sha256": hashlib.sha256(envelope_bytes).hexdigest(),
        "canonical_response_projection": status_confirm_envelope_projection(envelope_bytes),
        "mounted_route_imports_composition": False,
        "implementation_authorized": False,
        "forbidden": contract["forbidden"],
        "next_candidate": contract["next_candidate"],
    }


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    if args.write:
        _write(CONTRACT_PATH, build_contract())
        _write(SCHEMA_PATH, build_schema())
        _write(EVIDENCE_PATH, evidence)
    else:
        print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
