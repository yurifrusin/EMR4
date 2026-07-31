"""Default-off deterministic/isolated Vertex planner contract."""

from __future__ import annotations

import copy
from datetime import datetime, timedelta, time, timezone
import json
from pathlib import Path

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
from app.routers import appointments as appointments_router
from app.services import reception_one_isolated_vertex_planner as isolated
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_readonly_synthetic_context_bridge as bridge
from scripts import (
    reception_one_default_off_dual_planner_runtime_live as occupied_live,
)
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v68 as frozen_v68
from scripts import reception_one_receptionist_first_v68_runtime as runtime_v68
from scripts import reception_one_structured_source_plan_language as structured
from tests.conftest import make_token


URL = "/api/v1/appointments/proposals/reception-one/compose"


def _enable(monkeypatch, practice, *, vertex: bool = False) -> None:
    monkeypatch.setattr(
        settings,
        "reception_one_product_context_runtime_enabled",
        True,
    )
    monkeypatch.setattr(
        settings,
        "reception_one_product_context_vertex_planner_enabled",
        vertex,
    )
    monkeypatch.setattr(
        settings,
        "reception_one_product_context_synthetic_practice_ids",
        str(practice.id),
    )
    monkeypatch.setattr(settings, "environment", "dev")


def _body(
    instruction: str,
    *,
    planner_mode: str | None = None,
    selected_appointment_id=None,
) -> dict[str, str]:
    value = {
        "contract_version": "reception.one.product-context-request.v1",
        "instruction": instruction,
        "reference_date": "2026-08-03",
        "surface_id": "diary-main",
        "correlation_id": "synthetic-dual-planner-001",
        "data_class": "authored_synthetic",
    }
    if planner_mode is not None:
        value["planner_mode"] = planner_mode
    if selected_appointment_id is not None:
        value["selected_appointment_id"] = str(selected_appointment_id)
    return value


def _post(client, user, body):
    return client.post(
        URL,
        json=body,
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )


def _appointment(
    db,
    *,
    practice,
    patient,
    practitioner,
    appt_type,
) -> Appointment:
    item = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        appointment_type_id=appt_type.id,
        appointment_date=datetime(2026, 8, 3).date(),
        start_time_local=time(10, 0),
        start_time=datetime(2026, 8, 3, 0, 0, tzinfo=timezone.utc),
        duration_minutes=15,
    )
    db.add(item)
    db.flush()
    return item


def _truth_counts(db) -> tuple[int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )


def test_deterministic_mode_remains_default_and_provider_free(
    client,
    monkeypatch,
    practice,
    receptionist_user,
    practitioner,
    patient,
    schedule,
) -> None:
    _enable(monkeypatch, practice)
    response = _post(
        client,
        receptionist_user,
        _body(
            "Make an appointment for Margaret Thompson with Dr Shera "
            "tomorrow morning."
        ),
    )
    assert response.status_code == 200, response.text
    value = response.json()
    assert value["planner_mode"] == "deterministic"
    assert value["provider_calls"] == 0
    assert value["runtime_audit_ref"] is None
    assert value["proposal_only"] is True
    assert value["write_performed"] is False


def test_isolated_mode_is_separately_default_off_before_context_read(
    client,
    monkeypatch,
    practice,
    receptionist_user,
) -> None:
    _enable(monkeypatch, practice)
    monkeypatch.setattr(
        appointments_router,
        "build_product_context_frame",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("context read must not occur")
        ),
    )
    response = _post(
        client,
        receptionist_user,
        _body("Prepare one proposal.", planner_mode="isolated_vertex"),
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Isolated planner not admitted"


def test_isolated_release_reuses_proposal_only_adapter_without_truth_change(
    client,
    db,
    monkeypatch,
    practice,
    receptionist_user,
    practitioner,
    patient,
    appt_type,
    schedule,
) -> None:
    _enable(monkeypatch, practice, vertex=True)
    selected = _appointment(
        db,
        practice=practice,
        patient=patient,
        practitioner=practitioner,
        appt_type=appt_type,
    )
    before = _truth_counts(db)

    def fake_isolated_planner(*, frame, **kwargs):
        current = frame["context"]["selected_appointment"]
        return isolated.IsolatedVertexPlannerResult(
            final_output={
                "proposal_family": "resize",
                "patient_ref": current["patient_ref"],
                "practitioner_ref": current["practitioner_ref"],
                "candidate_slot_ids": [],
                "duration_minutes": 30,
                "warning_codes": [],
                "api_spine_operation_id": "proposeAppointmentUpdate",
                "requires_human_confirmation": True,
                "write_performed": False,
            },
            review={
                "disposition": "admit",
                "normalized_plan_sha256": "a" * 64,
                "admitted_operator_ids": [
                    "resolve_selected_appointment",
                    "set_duration",
                    "prepare_update_proposal",
                ],
                "safe_repairs": [],
                "violations": [],
                "reviewed_context_revision": frame["context_revision"],
            },
            normalized_plan={"goal": "resize"},
            provider_calls=1,
            runtime_audit_ref="runtime-0123456789abcdef",
            terminal_status="admitted_first_turn",
            receptionist_response=(
                "I can prepare a 30-minute duration-change proposal. "
                "No appointment was changed."
            ),
        )

    monkeypatch.setattr(
        appointments_router,
        "run_isolated_vertex_planner",
        fake_isolated_planner,
    )
    response = _post(
        client,
        receptionist_user,
        _body(
            "Extend Margaret Thompson's appointment with Dr Shera "
            "to 30 minutes.",
            planner_mode="isolated_vertex",
            selected_appointment_id=selected.id,
        ),
    )
    assert response.status_code == 200, response.text
    value = response.json()
    assert value["result"] == "proposal_ready"
    assert value["goal"] == "resize"
    assert value["planner_mode"] == "isolated_vertex"
    assert value["provider_calls"] == 1
    assert value["runtime_audit_ref"] == "runtime-0123456789abcdef"
    assert value["adapter_review"]["adapter_kind"] == "update_proposal"
    assert value["adapter_review"]["freshness_verified"] is True
    assert value["proposed_duration_minutes"] == 30
    assert value["requires_confirmation"] is True
    assert value["proposal_only"] is True
    assert value["write_performed"] is False
    assert _truth_counts(db) == before


def test_isolated_failure_is_502_with_no_deterministic_fallback(
    client,
    monkeypatch,
    practice,
    receptionist_user,
    practitioner,
    patient,
    schedule,
) -> None:
    _enable(monkeypatch, practice, vertex=True)

    def fail_isolated(**kwargs):
        raise isolated.IsolatedVertexPlannerError(
            "isolated_vertex_attempt_failed"
        )

    monkeypatch.setattr(
        appointments_router,
        "run_isolated_vertex_planner",
        fail_isolated,
    )
    monkeypatch.setattr(
        appointments_router,
        "proofread_provider_blocked_plan",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("deterministic fallback must not run")
        ),
    )
    response = _post(
        client,
        receptionist_user,
        _body(
            "Make an appointment for Margaret Thompson with Dr Shera "
            "tomorrow morning.",
            planner_mode="isolated_vertex",
        ),
    )
    assert response.status_code == 502
    assert response.json()["detail"]["code"] == (
        "isolated_vertex_attempt_failed"
    )


def test_request_cannot_supply_provider_model_region_or_identity(
    client,
    monkeypatch,
    practice,
    receptionist_user,
) -> None:
    _enable(monkeypatch, practice, vertex=True)
    for key, value in (
        ("provider", "other"),
        ("model_id", "other"),
        ("location", "global"),
        ("service_account", "other@example.invalid"),
    ):
        body = _body("Prepare one proposal.", planner_mode="isolated_vertex")
        body[key] = value
        response = _post(client, receptionist_user, body)
        assert response.status_code == 422, key


def _reference_form(frame: dict) -> tuple[dict, dict]:
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v6_cohort.v5_cohort._operator_note(plan["goal"]),
    )
    return program, frozen_v68.model_form_body(program, frame=frame)


def test_runtime_proofreader_uses_wall_clock_without_changing_frozen_v68() -> None:
    frame = json.loads(bridge.FRAME_PATH.read_text(encoding="utf-8"))
    program, body = _reference_form(frame)
    turn_input = runtime_v68.build_turn_input(frame)
    observed_at = datetime.fromisoformat(
        frame["observed_at"].replace("Z", "+00:00")
    )
    expires_at = datetime.fromisoformat(
        frame["expires_at"].replace("Z", "+00:00")
    )

    admitted = runtime_v68.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
        turn_input=turn_input,
        now=observed_at,
    )
    rejected = runtime_v68.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
        turn_input=turn_input,
        now=expires_at + timedelta(seconds=1),
    )
    frozen = frozen_v68.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
        turn_input=frozen_v68.build_turn_input(frame),
    )

    assert admitted["disposition"] == "admit"
    assert rejected["disposition"] == "edge_abort"
    assert {"code": "stale_context", "path": "$.context_revision"} in (
        rejected["violations"]
    )
    assert frozen["disposition"] == "admit"
    assert runtime_v68.BASELINE_METADATA[
        "frozen_v68_prompt_or_schema_changed"
    ] is False


def test_busy_runtime_creates_no_request_attempt_directory(
    tmp_path: Path,
) -> None:
    frame = json.loads(bridge.FRAME_PATH.read_text(encoding="utf-8"))
    observed_at = datetime.fromisoformat(
        frame["observed_at"].replace("Z", "+00:00")
    )
    authority = tmp_path / "authority.json"
    preflight = tmp_path / "preflight.json"
    evidence = tmp_path / "evidence"
    authority.write_text("{}", encoding="utf-8")
    preflight.write_text("{}", encoding="utf-8")

    isolated._RUNTIME_LOCK.acquire()
    try:
        try:
            isolated.run_isolated_vertex_planner(
                frame=copy.deepcopy(frame),
                observed_at=observed_at,
                authority_path=str(authority),
                preflight_path=str(preflight),
                evidence_dir=str(evidence),
            )
        except isolated.IsolatedVertexPlannerError as error:
            assert str(error) == "isolated_vertex_runtime_busy"
        else:
            raise AssertionError("busy runtime did not fail closed")
    finally:
        isolated._RUNTIME_LOCK.release()

    assert evidence.is_dir()
    assert list(evidence.iterdir()) == []


def test_isolated_runtime_reads_exact_authority_call_ceiling(
    tmp_path: Path,
) -> None:
    authority = tmp_path / "authority.json"
    authority.write_text(
        json.dumps({"absolute_call_ceiling": 1}),
        encoding="utf-8",
    )
    assert isolated._authority_call_ceiling(authority) == 1
    authority.write_text(
        json.dumps({"absolute_call_ceiling": 2}),
        encoding="utf-8",
    )
    assert isolated._authority_call_ceiling(authority) == 2
    authority.write_text(
        json.dumps({"absolute_call_ceiling": 3}),
        encoding="utf-8",
    )
    try:
        isolated._authority_call_ceiling(authority)
    except isolated.IsolatedVertexPlannerError as error:
        assert str(error) == "isolated_vertex_call_ceiling_invalid"
    else:
        raise AssertionError("invalid authority call ceiling was accepted")


def test_api_spine_declares_exact_default_off_exception() -> None:
    openapi = Path(
        "docs/api-spine/openapi/appointment-commands.yaml"
    ).read_text(encoding="utf-8")
    manifest = Path(
        "docs/api-spine/manifests/agent-capability-charters.yaml"
    ).read_text(encoding="utf-8")
    assert "planner_mode:" in openapi
    assert "enum: [deterministic, isolated_vertex]" in openapi
    assert '\"502\":' in openapi
    assert "blocked_except_exact_default_off_synthetic_product_context" in (
        manifest
    )
    for exact_value in isolated.EXPECTED_BINDING.values():
        if isinstance(exact_value, str):
            assert exact_value in manifest


def test_windows_runtime_directory_cleanup_retries_closed_log_race(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runtime_dir = tmp_path / f"emr4-{occupied_live.RUNTIME_TAG}"
    runtime_dir.mkdir()
    (runtime_dir / "backend.stderr.log").write_text("", encoding="utf-8")
    original_rmtree = occupied_live.shutil.rmtree
    calls = 0

    def transient_rmtree(path):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise PermissionError("closed handle not released yet")
        original_rmtree(path)

    monkeypatch.setattr(occupied_live, "RUNTIME_DIR", runtime_dir)
    monkeypatch.setattr(
        occupied_live.tempfile,
        "gettempdir",
        lambda: str(tmp_path),
    )
    monkeypatch.setattr(occupied_live.shutil, "rmtree", transient_rmtree)
    monkeypatch.setattr(occupied_live.time, "sleep", lambda _: None)

    occupied_live._remove_runtime_dir()

    assert calls == 2
    assert runtime_dir.exists() is False


def test_closed_occupied_evidence_has_one_call_and_zero_call_recovery() -> None:
    root = Path(
        "orchestration/continuity/"
        "reception-one-default-off-dual-planner-runtime"
    )
    evidence = json.loads(
        (root / "occupied-route-evidence.json").read_text(encoding="utf-8")
    )
    residue = json.loads(
        (root / "occupied-final-residue-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    occupied = evidence["occupied_attempt"]
    recovery = evidence["provider_free_route_recovery"]

    assert evidence["result"] == (
        "reception_one_default_off_dual_planner_"
        "occupied_model_and_recovered_route_pass"
    )
    assert evidence["continuity_binding"] == {
        "graph_revision": 152,
        "compass_revision": 133,
        "compass_source_graph_revision": 152,
    }
    assert occupied["provider_http_status"] == 200
    assert occupied["provider_calls"] == 1
    assert occupied["proofreader_disposition"] == "admit"
    assert occupied["proposal_family"] == "resize"
    assert occupied["duration_minutes"] == 45
    assert occupied["write_performed"] is False
    assert recovery["http_status"] == 200
    assert recovery["planner_mode"] == "deterministic"
    assert recovery["provider_calls"] == 0
    assert recovery["adapter_safe"] is True
    assert recovery["write_performed"] is False
    assert evidence["call_budget"]["actual_provider_calls"] == 1
    assert evidence["call_budget"]["additional_call_during_recovery"] is False
    assert all(evidence["cleanup"].values())
    assert residue["clear"] is True
    assert evidence["explicit_exclusions"]["raw_prompt_retained"] is False
    assert (
        evidence["explicit_exclusions"]["raw_provider_response_retained"]
        is False
    )

    artifact_dir = root / occupied["runtime_audit_ref"]
    assert (artifact_dir / "runtime-frame.json").exists() is False
    manifest = json.loads(
        (artifact_dir / "runtime-frame-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["raw_frame_retained"] is False
    ledgers = list(artifact_dir.glob("occupied-turn-*-ledger.json"))
    assert len(ledgers) == 1
    ledger = json.loads(ledgers[0].read_text(encoding="utf-8"))
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 1
