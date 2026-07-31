#!/usr/bin/env python3
"""Build and rehearse the minimal read-only synthetic Diary-context bridge."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date, time, timedelta
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys
from typing import Any, Iterator
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.models.diary_events import DiaryCommittedEvent
from app.models.patients import Patient
from app.models.tenancy import Practitioner
from app.services.reception_one_proposal_runtime import (
    build_product_context_frame,
)
from scripts import bernie_reception_one_combined_scope_harness as database
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5_live as parent_live
from scripts import reception_one_preprinted_form_v5_multicase as v5_cohort
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v68 as frozen
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-readonly-synthetic-diary-context"
)
FRAME_PATH = ARTIFACT_DIR / "context-frame.json"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
DATABASE_CLEANUP_PATH = ARTIFACT_DIR / "database-cleanup-evidence.json"
DIAGNOSTIC_PATH = ARTIFACT_DIR / "provider-blocked-diagnostic.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-evidence.json"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"
OCCUPIED_DIR = ARTIFACT_DIR / "occupied-retry-001"
LOCKED_DATABASE = (
    "gp_pms_reception_one_readonly_context_71d3c4a8_20260730"
)
RUNTIME_TAG = "reception-one-readonly-context-71d3c4a8"
REFERENCE_DATE = date(2026, 7, 27)
INSTRUCTION = (
    "Extend Margaret Thompson's appointment with Dr Alex Shera to "
    "45 minutes."
)
CASE = {
    "case_code": "context-resize",
    "source_case_id": None,
    "expected_goal": "resize",
    "expected_proposal_family": "resize",
    "expected_proposal_release": True,
}
ATTEMPT_IDS = (
    "reception-one-receptionist-first-v68-eval-context-resize-retry-turn-001",
    "reception-one-receptionist-first-v68-eval-context-resize-retry-turn-002",
)
LEDGER_IDS = (
    "reception-one-receptionist-first-v68-eval-context-resize-retry-ledger-001",
    "reception-one-receptionist-first-v68-eval-context-resize-retry-ledger-002",
)


class BridgeError(RuntimeError):
    """A read-only context, frozen-contract or lifecycle rejection."""


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BridgeError("json_object_required")
    return value


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _content_hash(value: dict[str, Any]) -> str:
    clean = dict(value)
    clean.pop("evidence_hash", None)
    return frozen.canonical_hash(clean)


def _configure_database() -> None:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev",
    )
    database.LOCKED_DATABASE = LOCKED_DATABASE
    database.RUNTIME_TAG = RUNTIME_TAG
    database._prepare_database_target()


def _truth_counts(db: Session) -> dict[str, int]:
    return {
        "appointments": db.query(Appointment).count(),
        "appointment_audit_logs": db.query(AppointmentAuditLog).count(),
        "appointment_command_idempotency": db.query(
            AppointmentCommandIdempotency
        ).count(),
        "diary_committed_events": db.query(DiaryCommittedEvent).count(),
    }


def _selected_appointment(db: Session, practice_id: uuid.UUID) -> Appointment:
    rows = (
        db.query(Appointment)
        .join(Patient, Patient.id == Appointment.patient_id)
        .join(Practitioner, Practitioner.id == Appointment.practitioner_id)
        .filter(
            Appointment.practice_id == practice_id,
            Patient.first_name == "Margaret",
            Patient.last_name == "Thompson",
            Practitioner.first_name == "Alex",
            Practitioner.last_name == "Shera",
            Appointment.appointment_date == REFERENCE_DATE,
            Appointment.start_time_local == time(9, 0),
        )
        .order_by(Appointment.start_time_local)
        .all()
    )
    if len(rows) != 1:
        raise BridgeError("selected_synthetic_appointment_not_exact")
    return rows[0]


def _provider_free_oracle(frame: dict[str, Any]) -> dict[str, Any]:
    plan = typed_plan.deterministic_plan(frame)
    if plan["goal"] != CASE["expected_goal"]:
        raise BridgeError("deterministic_goal_mismatch")
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v5_cohort._operator_note(plan["goal"]),
    )
    body = frozen.model_form_body(program, frame=frame)
    assembled = frozen.assemble_program(body)
    turn_input = frozen.build_turn_input(frame)
    frozen.validate_turn_input(frame, turn_input)
    evaluation = frozen.evaluate_output(
        frame,
        assembled,
        body,
        turn_code=1,
        turn_input=turn_input,
    )
    if (
        evaluation["disposition"] != "admit"
        or evaluation["context_frame_review"]["disposition"] != "admit"
    ):
        _write_json(
            DIAGNOSTIC_PATH,
            {
                "schema_version": (
                    "reception.one.readonly_synthetic_diary_context."
                    "provider_blocked_diagnostic.v1"
                ),
                "disposition": evaluation["disposition"],
                "violation_codes": [
                    item.get("code")
                    for item in evaluation.get("violations", [])
                ],
                "violation_paths": [
                    item.get("path")
                    for item in evaluation.get("violations", [])
                ],
                "context_disposition": evaluation.get(
                    "context_frame_review", {}
                ).get("disposition"),
                "raw_prompt_retained": False,
                "raw_response_retained": False,
            },
        )
        raise BridgeError("provider_free_oracle_not_admitted")
    release = typed_plan.execute_plan(
        frame,
        evaluation["normalized_plan"],
        evaluation["semantic_review"],
    )["final_output"]
    if (
        release.get("proposal_family") != "resize"
        or release.get("duration_minutes") != 45
        or release.get("write_performed") is not False
    ):
        raise BridgeError("provider_free_release_contract_mismatch")
    desk_context = turn_input["task"]["desk_context"]
    if set(desk_context) != {
        "contract_version",
        "data_class",
        "effect_ceiling",
        "authority",
        "current_diary",
        "recent_dialogue",
        "selected_appointment",
        "grounded_mentions",
        "freshness",
        "resolution_precedence",
        "excluded_context",
    }:
        raise BridgeError("model_visible_context_allowlist_changed")
    return {
        "frame_sha256": frozen.canonical_hash(frame),
        "turn_input_sha256": frozen.canonical_hash(turn_input),
        "task_sha256": turn_input["task_sha256"],
        "desk_context_sha256": turn_input["desk_context_sha256"],
        "provider_request_sha256": frozen.canonical_hash(
            frozen.build_vertex_request(turn_input)
        ),
        "provider_response_schema_sha256": frozen.canonical_hash(
            frozen.vertex_response_schema()
        ),
        "system_instruction_sha256": frozen.canonical_hash(
            {"text": frozen.SYSTEM_INSTRUCTION}
        ),
        "program_sha256": frozen.canonical_hash(program),
        "goal": plan["goal"],
        "proofreader_disposition": evaluation["disposition"],
        "context_frame_review": evaluation["context_frame_review"],
        "expected_final_output": release,
        "model_visible_context_keys": sorted(desk_context),
        "model_visible_selected_appointment": True,
        "model_visible_full_diary": False,
        "model_visible_unselected_appointments": False,
    }


def build_provider_blocked_evidence() -> dict[str, Any]:
    if FRAME_PATH.exists() or PROVIDER_BLOCKED_PATH.exists():
        raise BridgeError("provider_blocked_output_already_exists")
    _configure_database()
    created = False
    session: Session | None = None
    cleanup: dict[str, Any] | None = None
    try:
        database.create_database()
        created = True
        database.create_schema_and_seed(
            f"ReadonlyContext-{secrets.token_urlsafe(24)}!"
        )
        before = database.database_readback()
        engine = create_engine(
            os.environ["DATABASE_URL"],
            poolclass=NullPool,
        )
        session = sessionmaker(bind=engine)()
        practice_id = uuid.UUID(str(database.base.PRACTICE_ID))
        selected = _selected_appointment(session, practice_id)
        raw_ids = {
            str(practice_id),
            str(selected.id),
            str(selected.patient_id),
            str(selected.practitioner_id),
        }
        counts_before = _truth_counts(session)
        frame, displays, handle_map = build_product_context_frame(
            session,
            practice_id=practice_id,
            instruction=INSTRUCTION,
            reference_date=REFERENCE_DATE,
            correlation_id="readonly-synthetic-context-001",
            slot_proposal=None,
            selected_appointment_id=selected.id,
            observed_at=typed_plan.EVIDENCE_NOW - timedelta(seconds=30),
            handle_key=hashlib.sha256(
                b"reception-one-readonly-authored-synthetic-context"
            ).digest(),
        )
        counts_after = _truth_counts(session)
        if counts_before != counts_after:
            raise BridgeError("database_truth_changed_during_context_read")
        if len(handle_map) < 3 or len(displays) != 2:
            raise BridgeError("opaque_handle_map_incomplete")
        oracle = _provider_free_oracle(frame)
        turn_input = frozen.build_turn_input(frame)
        serialized_turn = frozen.canonical_json(turn_input)
        if any(raw_id in serialized_turn for raw_id in raw_ids):
            raise BridgeError("raw_database_identifier_entered_cell_packet")
        if turn_input["task"]["desk_context"]["freshness"] != {
            "context_revision": frame["context_revision"],
            "observed_at": frame["observed_at"],
            "expires_at": frame["expires_at"],
            "clock": "frozen_authored_synthetic_scenario",
        }:
            raise BridgeError("freshness_binding_mismatch")
        after = database.database_readback()
        if before["counts"] != after["counts"] or before["sha256"] != after["sha256"]:
            raise BridgeError("database_readback_changed")
        _write_json(FRAME_PATH, frame)
        evidence: dict[str, Any] = {
            "schema_version": (
                "reception.one.readonly_synthetic_diary_context."
                "provider_blocked.v1"
            ),
            "result": (
                "reception_one_readonly_synthetic_diary_context_"
                "provider_blocked_pass"
            ),
            "provider_contacted": False,
            "provider_calls": 0,
            "credential_reads": 0,
            "data_class": "authored_synthetic",
            "trusted_context_builder": (
                "app.services.reception_one_proposal_runtime."
                "build_product_context_frame"
            ),
            "database": {
                "kind": "exact_owned_disposable_postgresql",
                "practice_scoped": True,
                "reads_performed": True,
                "writes_performed_after_seed": False,
                "truth_counts_before": counts_before,
                "truth_counts_after": counts_after,
                "readback_sha256_unchanged": True,
            },
            "frame": {
                "path": str(FRAME_PATH.relative_to(ROOT)).replace("\\", "/"),
                "file_sha256": _file_hash(FRAME_PATH),
                "content_sha256": frozen.canonical_hash(frame),
                "contract_version": frame["contract_version"],
                "context_revision": frame["context_revision"],
                "observed_at": frame["observed_at"],
                "expires_at": frame["expires_at"],
                "opaque_handle_count": len(handle_map),
                "raw_database_ids_serialized": False,
                "handle_map_serialized": False,
            },
            "frozen_v68": oracle,
            "boundaries": {
                "model_database_access": False,
                "cell_credential_access": False,
                "full_diary_exposed": False,
                "unselected_appointments_exposed": False,
                "confirmation_authority": False,
                "appointment_write_authority": False,
                "provider_execution_in_frame": False,
                "product_delivery": False,
            },
        }
        evidence["evidence_hash"] = _content_hash(evidence)
        _write_json(PROVIDER_BLOCKED_PATH, evidence)
        return evidence
    finally:
        if session is not None:
            bind = session.get_bind()
            session.close()
            bind.dispose()
        if created:
            cleanup = database.cleanup_database()
        _write_json(
            DATABASE_CLEANUP_PATH,
            {
                "schema_version": (
                    "reception.one.readonly_synthetic_diary_context."
                    "database_cleanup.v1"
                ),
                "ownership_marker_verified": created,
                "scope": "exact_disposable_authored_synthetic_database",
                "cleanup": cleanup,
                "database_absent": bool(
                    cleanup
                    and cleanup.get("cleanup")
                    == "dropped_exact_verified_disposable_database"
                ),
            },
        )


@contextmanager
def _frozen_live_contract() -> Iterator[None]:
    old_parent = parent_live.preprinted
    old_v6 = v6_cohort.v6
    parent_live.preprinted = frozen
    v6_cohort.v6 = frozen
    try:
        yield
    finally:
        parent_live.preprinted = old_parent
        v6_cohort.v6 = old_v6


def run_occupied(
    *,
    preflight_path: Path,
    authority_path: Path,
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any]:
    if OCCUPIED_PATH.exists():
        raise BridgeError("occupied_output_already_exists")
    provider_free = _load(PROVIDER_BLOCKED_PATH)
    frame = _load(FRAME_PATH)
    if (
        provider_free.get("evidence_hash") != _content_hash(provider_free)
        or provider_free["frame"]["file_sha256"] != _file_hash(FRAME_PATH)
        or provider_free["frame"]["content_sha256"] != frozen.canonical_hash(frame)
    ):
        raise BridgeError("provider_blocked_binding_changed")
    cleanup = _load(DATABASE_CLEANUP_PATH)
    if cleanup.get("database_absent") is not True:
        raise BridgeError("disposable_database_cleanup_not_proven")
    with _frozen_live_contract():
        dialogue = parent_live.run_dialogue(
            artifact_dir=OCCUPIED_DIR,
            preflight_path=preflight_path,
            authority_path=authority_path,
            expected_graph_revision=graph_revision,
            expected_compass_revision=compass_revision,
            frame_path=FRAME_PATH,
            attempt_ids=ATTEMPT_IDS,
            ledger_ids=LEDGER_IDS,
        )
        observation = v6_cohort._case_observation(
            case=CASE,
            oracle=provider_free["frozen_v68"],
            case_dir=OCCUPIED_DIR,
            dialogue=dialogue,
        )
    expected = provider_free["frozen_v68"]["expected_final_output"]
    if (
        observation["expected_safe_outcome"] is not True
        or observation["cleanup_passed"] is not True
        or dialogue.get("release") != expected
    ):
        raise BridgeError("occupied_context_result_not_exact")
    ledgers = sorted(OCCUPIED_DIR.glob("*-ledger.json"))
    if (
        len(ledgers) != dialogue["actual_provider_call_count"]
        or any(_load(path).get("status") != "consumed" for path in ledgers)
    ):
        raise BridgeError("occupied_ledger_consumption_invalid")
    evidence: dict[str, Any] = {
        "schema_version": (
            "reception.one.readonly_synthetic_diary_context.occupied.v1"
        ),
        "result": "reception_one_readonly_synthetic_diary_context_occupied_pass",
        "data_class": "authored_synthetic",
        "continuity_binding": {
            "graph_revision": graph_revision,
            "compass_revision": compass_revision,
        },
        "actual_provider_calls": dialogue["actual_provider_call_count"],
        "absolute_provider_call_ceiling": 2,
        "incremental_cost_ceiling_usd": 1,
        "expected_safe_outcome": True,
        "observation": observation,
        "all_ledgers_consumed": True,
        "database_absent_before_occupied_call": True,
        "trusted_backend_frame_sha256": provider_free["frame"]["content_sha256"],
        "model_database_access": False,
        "cell_credential_access": False,
        "full_diary_exposed": False,
        "unselected_appointments_exposed": False,
        "write_performed": False,
        "confirmation_performed": False,
        "product_delivered": False,
        "raw_prompt_retained": False,
        "raw_provider_response_retained": False,
        "chain_of_thought_retained": False,
    }
    evidence["evidence_hash"] = _content_hash(evidence)
    _write_json(OCCUPIED_PATH, evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("provider-blocked")
    occupied = sub.add_parser("occupied")
    occupied.add_argument("--preflight", type=Path, required=True)
    occupied.add_argument("--authority", type=Path, default=AUTHORITY_PATH)
    occupied.add_argument("--graph-revision", type=int, required=True)
    occupied.add_argument("--compass-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command == "provider-blocked":
            evidence = build_provider_blocked_evidence()
        else:
            evidence = run_occupied(
                preflight_path=args.preflight,
                authority_path=args.authority,
                graph_revision=args.graph_revision,
                compass_revision=args.compass_revision,
            )
    except Exception as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_readonly_synthetic_diary_context_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_calls": evidence.get("actual_provider_calls", 0),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
