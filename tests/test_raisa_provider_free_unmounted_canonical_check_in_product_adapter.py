from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any
from uuid import UUID

import pytest

from app.models.appointments import AppointmentStatus
from app.models.tenancy import UserRole
from app.schemas.appointments import (
    AppointmentCheckInCommand,
    AppointmentCheckInProposalConfirmationIn,
    AppointmentCheckInProposalOut,
    AppointmentProposalIssue,
)
from app.services.appointment_check_in_product_adapter import (
    CHECK_IN_AUDIT_EVIDENCE,
    CHECK_IN_EVENT_SCHEMA_VERSION,
    CHECK_IN_EVENT_TYPE,
    CHECK_IN_OPERATION_ID,
    CHECK_IN_ROUTE_FAMILY,
    CheckInDependencies,
    check_in_command_payload,
    check_in_proposal_freshness_id,
    check_in_state_payload,
    check_in_target_area_id,
    compose_product_check_in,
)


PRACTICE_ID = UUID("10000000-0000-0000-0000-000000000001")
OTHER_PRACTICE_ID = UUID("10000000-0000-0000-0000-000000000002")
ACTOR_ID = UUID("20000000-0000-0000-0000-000000000001")
OTHER_ACTOR_ID = UUID("20000000-0000-0000-0000-000000000002")
APPOINTMENT_ID = UUID("30000000-0000-0000-0000-000000000001")
OTHER_APPOINTMENT_ID = UUID("30000000-0000-0000-0000-000000000002")
LOCATION_ID = UUID("40000000-0000-0000-0000-000000000001")
OTHER_LOCATION_ID = UUID("40000000-0000-0000-0000-000000000002")
AREA_ID = UUID("50000000-0000-0000-0000-000000000001")
OTHER_AREA_ID = UUID("50000000-0000-0000-0000-000000000002")
COMMAND_ID = UUID("60000000-0000-0000-0000-000000000001")
AUDIT_ID = UUID("70000000-0000-0000-0000-000000000001")
EVENT_ID = UUID("80000000-0000-0000-0000-000000000001")
NOW = datetime(2026, 8, 18, 0, 0, tzinfo=timezone.utc)
EVIDENCE = "opaque-authored-synthetic-check-in-evidence"


def _actor(
    *,
    actor_id: UUID = ACTOR_ID,
    practice_id: UUID = PRACTICE_ID,
    role: UserRole = UserRole.Receptionist,
    active: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=actor_id,
        practice_id=practice_id,
        role=role,
        is_active=active,
    )


def _appointment(
    *,
    appointment_id: UUID = APPOINTMENT_ID,
    practice_id: UUID = PRACTICE_ID,
    status: AppointmentStatus | str = AppointmentStatus.Booked,
    waiting_area_id: UUID | None = None,
    location_id: UUID | None = LOCATION_ID,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=appointment_id,
        practice_id=practice_id,
        status=status,
        waiting_area_id=waiting_area_id,
        location_id=location_id,
        patient_id=UUID("90000000-0000-0000-0000-000000000001"),
        patient_name_provisional="Never release",
        reason="Private reason",
        notes="Private note",
    )


def _area(
    *,
    area_id: UUID = AREA_ID,
    practice_id: UUID = PRACTICE_ID,
    location_id: UUID | None = LOCATION_ID,
    active: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=area_id,
        practice_id=practice_id,
        location_id=location_id,
        is_active=active,
    )


class FakeDependencies:
    def __init__(
        self,
        *,
        appointment: Any | None = None,
        current_actor: Any | None = None,
        areas: dict[UUID, Any] | None = None,
        claim_kind: str = "started",
        replay_body: dict[str, Any] | None = None,
        verify_result: tuple[bool, str, dict[str, Any] | None] = (
            True,
            "signed_evidence_verified",
            {},
        ),
        fail_at: str | None = None,
    ) -> None:
        self.appointment = appointment or _appointment()
        self.current_actor = current_actor if current_actor is not None else _actor()
        self.areas = areas or {}
        self.claim_kind = claim_kind
        self.replay_body = replay_body
        self.verify_result = verify_result
        self.fail_at = fail_at
        self.calls: list[str] = []
        self.claim_kwargs: dict[str, Any] = {}
        self.verify_kwargs: dict[str, Any] = {}
        self.effect_plans: list[Any] = []
        self.audit_plans: list[Any] = []
        self.event_plans: list[Any] = []
        self.complete_kwargs: list[dict[str, Any]] = []
        self.commits = 0
        self.rollbacks = 0
        self._snapshot: tuple[Any, Any] | None = None

    def _fail(self, name: str) -> None:
        if self.fail_at == name:
            raise RuntimeError(f"injected {name} failure")

    def claim(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append("claim")
        self.claim_kwargs = kwargs
        self._fail("claim")
        return SimpleNamespace(
            kind=self.claim_kind,
            record=SimpleNamespace(id=COMMAND_ID),
            response_status_code=200,
            response_body_json=self.replay_body,
        )

    def load_locked_appointment(self, **kwargs: Any) -> Any:
        self.calls.append("lock")
        self._fail("lock")
        return self.appointment

    def load_current_actor(self, **kwargs: Any) -> Any:
        self.calls.append("reauthorize")
        self._fail("reauthorize")
        return self.current_actor

    def load_waiting_area(self, **kwargs: Any) -> Any:
        self.calls.append("waiting_area")
        self._fail("waiting_area")
        return self.areas.get(kwargs["waiting_area_id"])

    def verify_evidence(self, evidence: str, **kwargs: Any) -> Any:
        self.calls.append("verify")
        self.verify_kwargs = {"evidence": evidence, **kwargs}
        self._fail("verify")
        return self.verify_result

    def stage_effect(self, **kwargs: Any) -> None:
        self.calls.append("effect")
        self._fail("effect")
        plan = kwargs["plan"]
        self.effect_plans.append(plan)
        self._snapshot = (self.appointment.status, self.appointment.waiting_area_id)
        self.appointment.status = AppointmentStatus.Arrived
        self.appointment.waiting_area_id = plan.waiting_area_id_after

    def write_audit(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append("audit")
        self._fail("audit")
        self.audit_plans.append(kwargs["plan"])
        return SimpleNamespace(id=AUDIT_ID)

    def write_event(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append("event")
        self._fail("event")
        self.event_plans.append(kwargs["plan"])
        return SimpleNamespace(id=EVENT_ID)

    def complete(self, **kwargs: Any) -> None:
        self.calls.append("complete")
        self._fail("complete")
        self.complete_kwargs.append(kwargs)

    def commit(self) -> None:
        self.calls.append("commit")
        self._fail("commit")
        self.commits += 1

    def rollback(self) -> None:
        self.calls.append("rollback")
        self.rollbacks += 1
        if self._snapshot is not None:
            self.appointment.status, self.appointment.waiting_area_id = self._snapshot

    def readback(self, **kwargs: Any) -> Any:
        self.calls.append("readback")
        self._fail("readback")
        return self.appointment

    def bundle(self) -> CheckInDependencies:
        return CheckInDependencies(
            claim=self.claim,
            load_locked_appointment=self.load_locked_appointment,
            load_current_actor=self.load_current_actor,
            load_waiting_area=self.load_waiting_area,
            verify_evidence=self.verify_evidence,
            stage_effect=self.stage_effect,
            write_audit=self.write_audit,
            write_event=self.write_event,
            complete=self.complete,
            commit=self.commit,
            rollback=self.rollback,
            readback=self.readback,
        )


def _body(
    appointment: Any,
    *,
    waiting_area_id: UUID | None = None,
    waiting_area_id_supplied: bool = False,
    warning_codes: list[str] | None = None,
) -> AppointmentCheckInProposalConfirmationIn:
    command = AppointmentCheckInCommand(
        appointment_id=appointment.id,
        waiting_area_id=waiting_area_id,
        waiting_area_id_supplied=waiting_area_id_supplied,
    )
    freshness = check_in_proposal_freshness_id(
        command,
        check_in_state_payload(appointment),
    )
    warnings = [
        AppointmentProposalIssue(code=code, severity="warning", message="Synthetic")
        for code in (warning_codes or [])
    ]
    proposal = AppointmentCheckInProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="execute_with_report",
        summary="Synthetic check-in",
        command=command,
        warnings=warnings,
        blocks=[],
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=EVIDENCE,
        signed_confirmation_evidence_required=True,
    )
    return AppointmentCheckInProposalConfirmationIn(
        confirmed=True,
        check_in_proposal=proposal,
        confirmed_warnings=list(warning_codes or []),
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=EVIDENCE,
        signed_confirmation_evidence_required=True,
    )


def _run(
    deps: FakeDependencies,
    body: AppointmentCheckInProposalConfirmationIn | Any | None = None,
    **overrides: Any,
):
    values = {
        "target_appointment_id": APPOINTMENT_ID,
        "server_practice_id": PRACTICE_ID,
        "authenticated_actor": _actor(),
        "raw_idempotency_key": "synthetic-idempotency-key",
        "now": NOW,
        "dependencies": deps.bundle(),
    }
    values.update(overrides)
    return compose_product_check_in(body or _body(deps.appointment), **values)


def test_helpers_match_the_frozen_route_local_contract_byte_for_byte() -> None:
    appointment = _appointment(waiting_area_id=AREA_ID, status=AppointmentStatus.Confirmed)
    command = AppointmentCheckInCommand(
        appointment_id=APPOINTMENT_ID,
        waiting_area_id=None,
        waiting_area_id_supplied=False,
    )
    state = {
        "appointment_id": str(APPOINTMENT_ID),
        "status": "Confirmed",
        "waiting_area_id": str(AREA_ID),
    }
    command_payload = {
        "appointment_id": str(APPOINTMENT_ID),
        "waiting_area_id": None,
        "waiting_area_id_supplied": False,
    }
    material = json.dumps(
        {
            "kind": "check_in_proposal_v1",
            "current_state": state,
            "command": command_payload,
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    assert check_in_state_payload(appointment) == state
    assert check_in_command_payload(command) == command_payload
    assert check_in_proposal_freshness_id(command, state) == hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest()[:32]
    assert check_in_target_area_id(appointment, command) == AREA_ID


@pytest.mark.parametrize("status", [AppointmentStatus.Booked, AppointmentStatus.Confirmed])
@pytest.mark.parametrize("area_mode", ["none", "assign", "preserve"])
def test_success_matrix_is_ordered_atomic_and_patient_free(
    status: AppointmentStatus,
    area_mode: str,
) -> None:
    existing = AREA_ID if area_mode == "preserve" else None
    appointment = _appointment(status=status, waiting_area_id=existing)
    areas = {AREA_ID: _area()} if area_mode != "none" else {}
    deps = FakeDependencies(appointment=appointment, areas=areas)
    body = _body(
        appointment,
        waiting_area_id=AREA_ID if area_mode == "assign" else None,
        waiting_area_id_supplied=area_mode == "assign",
    )

    result = _run(deps, body)

    assert result.kind == "confirmed_write"
    assert result.committed is True
    expected_calls = ["claim", "lock", "reauthorize", "verify"]
    if area_mode != "none":
        expected_calls.append("waiting_area")
    expected_calls.extend(["effect", "audit", "event", "complete", "commit", "readback"])
    assert deps.calls == expected_calls
    assert deps.commits == 1
    assert deps.rollbacks == 0
    assert len(deps.effect_plans) == len(deps.audit_plans) == len(deps.event_plans) == 1
    target_area = None if area_mode == "none" else AREA_ID
    assert deps.effect_plans[0].waiting_area_id_after == target_area
    assert deps.audit_plans[0].audit_evidence == CHECK_IN_AUDIT_EVIDENCE
    assert deps.event_plans[0].event_type == CHECK_IN_EVENT_TYPE
    assert deps.event_plans[0].schema_version == CHECK_IN_EVENT_SCHEMA_VERSION
    assert deps.event_plans[0].payload["status_before"] == status.value
    assert deps.event_plans[0].payload["status_after"] == "Arrived"
    serialized = json.dumps(result.response_body, sort_keys=True)
    for forbidden in (
        "Never release",
        "Private reason",
        "Private note",
        EVIDENCE,
        "synthetic-idempotency-key",
        "patient_id",
    ):
        assert forbidden not in serialized
    assert result.response_body["receipt"]["schema_version"] == (
        "appointment.check_in_receipt.v1"
    )


def test_same_key_replay_returns_exact_stored_result_before_lock_or_effect() -> None:
    first = FakeDependencies()
    accepted = _run(first)
    stored = dict(accepted.response_body)
    replay = FakeDependencies(claim_kind="replay", replay_body=stored)

    result = _run(replay)

    assert result.kind == "replay"
    assert result.response_body == stored
    assert result.response_body is not stored
    assert replay.calls == ["claim"]
    assert replay.commits == replay.rollbacks == 0


def test_replay_with_extra_patient_or_secret_material_fails_closed() -> None:
    first = FakeDependencies()
    accepted = _run(first)
    stored = dict(accepted.response_body)
    stored["patient_id"] = str(UUID("90000000-0000-0000-0000-000000000001"))
    replay = FakeDependencies(claim_kind="replay", replay_body=stored)

    result = _run(replay)

    assert result.kind == "stopped"
    assert result.reason == "stored_replay_invalid"
    assert replay.calls == ["claim", "rollback"]


def test_replay_with_non_success_status_fails_closed() -> None:
    first = FakeDependencies()
    accepted = _run(first)
    replay = FakeDependencies(claim_kind="replay", replay_body=dict(accepted.response_body))
    original_claim = replay.claim

    def invalid_status_claim(**kwargs: Any) -> SimpleNamespace:
        decision = original_claim(**kwargs)
        decision.response_status_code = 201
        return decision

    bundle = replay.bundle()
    bundle = CheckInDependencies(**{**bundle.__dict__, "claim": invalid_status_claim})
    result = compose_product_check_in(
        _body(replay.appointment),
        target_appointment_id=APPOINTMENT_ID,
        server_practice_id=PRACTICE_ID,
        authenticated_actor=_actor(),
        raw_idempotency_key="synthetic-idempotency-key",
        now=NOW,
        dependencies=bundle,
    )

    assert result.kind == "stopped"
    assert result.reason == "stored_replay_invalid"
    assert replay.calls == ["claim", "rollback"]


@pytest.mark.parametrize(
    ("fail_at", "expected_committed", "expects_rollback"),
    [
        ("audit", False, True),
        ("event", False, True),
        ("complete", False, True),
        ("commit", None, False),
        ("readback", None, False),
    ],
)
def test_injected_failures_never_release_a_false_success(
    fail_at: str,
    expected_committed: bool | None,
    expects_rollback: bool,
) -> None:
    deps = FakeDependencies(fail_at=fail_at)

    result = _run(deps)

    assert result.kind == "stopped"
    assert result.committed is expected_committed
    assert deps.rollbacks == int(expects_rollback)
    assert result.response_body["receipt"] is None
    if fail_at in {"commit", "readback"}:
        assert result.reason in {"commit_outcome_unknown", "committed_readback_unavailable"}


HOSTILE_MUTATIONS = (
    "false_confirmation",
    "unsafe_proposal",
    "confirmation_not_required",
    "blocked_tier",
    "blocked_issue",
    "proposal_evidence_optional",
    "body_evidence_optional",
    "evidence_missing",
    "evidence_blank",
    "evidence_mismatch",
    "warning_missing_ack",
    "duplicate_body_warning",
    "duplicate_proposal_warning",
    "freshness_missing",
    "freshness_short",
    "freshness_mismatch",
    "command_target_mismatch",
    "command_type_wrong",
    "proposal_type_wrong",
    "confirmation_type_wrong",
    "initial_actor_inactive",
    "initial_actor_wrong_practice",
    "initial_actor_gp",
    "initial_actor_admin",
    "initial_actor_malformed",
    "claim_conflict",
    "claim_in_progress",
    "claim_stale_in_progress",
    "claim_failed_transient",
    "claim_evidence_reuse",
    "claim_unknown",
    "appointment_missing",
    "appointment_wrong_id",
    "appointment_wrong_practice",
    "appointment_malformed",
    "appointment_arrived",
    "appointment_in_consult",
    "appointment_completed",
    "appointment_cancelled",
    "appointment_dna",
    "appointment_no_show",
    "appointment_invalid_status",
    "current_actor_missing",
    "current_actor_inactive",
    "current_actor_wrong_practice",
    "current_actor_wrong_id",
    "current_actor_gp",
    "current_actor_admin",
    "evidence_missing_code",
    "evidence_tampered",
    "evidence_malformed",
    "evidence_wrong_version",
    "evidence_wrong_purpose",
    "evidence_expired",
    "evidence_binding_mismatch",
    "evidence_unexpected_success_code",
    "waiting_area_move",
    "waiting_area_location_missing",
    "waiting_area_lookup_missing",
    "waiting_area_wrong_id",
    "waiting_area_wrong_practice",
    "waiting_area_inactive",
    "waiting_area_locationless",
    "waiting_area_location_mismatch",
    "preserved_area_location_missing",
    "preserved_area_lookup_missing",
    "preserved_area_inactive",
    "preserved_area_location_mismatch",
)


def _apply_hostile_mutation(
    name: str,
    deps: FakeDependencies,
    body: AppointmentCheckInProposalConfirmationIn,
    overrides: dict[str, Any],
) -> Any:
    proposal = body.check_in_proposal
    command = proposal.command
    issue = AppointmentProposalIssue(code="warning", severity="warning", message="Synthetic")
    if name == "false_confirmation":
        body.confirmed = False
    elif name == "unsafe_proposal":
        proposal.safe = False
    elif name == "confirmation_not_required":
        proposal.requires_confirmation = False
    elif name == "blocked_tier":
        proposal.autonomy_tier = "blocked"
    elif name == "blocked_issue":
        proposal.blocks = [AppointmentProposalIssue(code="blocked", severity="blocked", message="x")]
    elif name == "proposal_evidence_optional":
        proposal.signed_confirmation_evidence_required = False
    elif name == "body_evidence_optional":
        body.signed_confirmation_evidence_required = False
    elif name == "evidence_missing":
        proposal.signed_confirmation_evidence = None
        body.signed_confirmation_evidence = None
    elif name == "evidence_blank":
        proposal.signed_confirmation_evidence = None
        body.signed_confirmation_evidence = "   "
    elif name == "evidence_mismatch":
        body.signed_confirmation_evidence = "different-evidence"
    elif name == "warning_missing_ack":
        proposal.warnings = [issue]
    elif name == "duplicate_body_warning":
        proposal.warnings = [issue]
        body.confirmed_warnings = ["warning", "warning"]
    elif name == "duplicate_proposal_warning":
        proposal.warnings = [issue, issue]
        body.confirmed_warnings = ["warning"]
    elif name == "freshness_missing":
        proposal.check_in_proposal_freshness_id = None
        body.check_in_proposal_freshness_id = None
    elif name == "freshness_short":
        proposal.check_in_proposal_freshness_id = "short"
        body.check_in_proposal_freshness_id = "short"
    elif name == "freshness_mismatch":
        body.check_in_proposal_freshness_id = "0" * 32
    elif name == "command_target_mismatch":
        command.appointment_id = OTHER_APPOINTMENT_ID
    elif name == "command_type_wrong":
        proposal.command = SimpleNamespace(appointment_id=APPOINTMENT_ID)
    elif name == "proposal_type_wrong":
        body.check_in_proposal = SimpleNamespace()
    elif name == "confirmation_type_wrong":
        class ConfirmationSubclass(AppointmentCheckInProposalConfirmationIn):
            pass

        body = ConfirmationSubclass.model_validate(body.model_dump(mode="json"))
    elif name == "initial_actor_inactive":
        overrides["authenticated_actor"] = _actor(active=False)
    elif name == "initial_actor_wrong_practice":
        overrides["authenticated_actor"] = _actor(practice_id=OTHER_PRACTICE_ID)
    elif name == "initial_actor_gp":
        overrides["authenticated_actor"] = _actor(role=UserRole.GP)
    elif name == "initial_actor_admin":
        overrides["authenticated_actor"] = _actor(role=UserRole.Admin)
    elif name == "initial_actor_malformed":
        overrides["authenticated_actor"] = SimpleNamespace(id=ACTOR_ID)
    elif name.startswith("claim_"):
        deps.claim_kind = {
            "claim_conflict": "conflict",
            "claim_in_progress": "in_progress",
            "claim_stale_in_progress": "stale_in_progress",
            "claim_failed_transient": "failed_transient",
            "claim_evidence_reuse": "evidence_replay_rejected",
            "claim_unknown": "unknown",
        }[name]
    elif name == "appointment_missing":
        deps.appointment = None
    elif name == "appointment_wrong_id":
        deps.appointment = _appointment(appointment_id=OTHER_APPOINTMENT_ID)
    elif name == "appointment_wrong_practice":
        deps.appointment = _appointment(practice_id=OTHER_PRACTICE_ID)
    elif name == "appointment_malformed":
        deps.appointment = SimpleNamespace(id=APPOINTMENT_ID)
    elif name.startswith("appointment_"):
        value = {
            "appointment_arrived": AppointmentStatus.Arrived,
            "appointment_in_consult": AppointmentStatus.InConsult,
            "appointment_completed": AppointmentStatus.Completed,
            "appointment_cancelled": AppointmentStatus.Cancelled,
            "appointment_dna": AppointmentStatus.DNA,
            "appointment_no_show": AppointmentStatus.NoShow,
            "appointment_invalid_status": "Invented",
        }[name]
        deps.appointment.status = value
    elif name == "current_actor_missing":
        deps.current_actor = None
    elif name == "current_actor_inactive":
        deps.current_actor = _actor(active=False)
    elif name == "current_actor_wrong_practice":
        deps.current_actor = _actor(practice_id=OTHER_PRACTICE_ID)
    elif name == "current_actor_wrong_id":
        deps.current_actor = _actor(actor_id=OTHER_ACTOR_ID)
    elif name == "current_actor_gp":
        deps.current_actor = _actor(role=UserRole.GP)
    elif name == "current_actor_admin":
        deps.current_actor = _actor(role=UserRole.Admin)
    elif name.startswith("evidence_"):
        if name == "evidence_unexpected_success_code":
            deps.verify_result = (True, "unexpected_success", {})
        else:
            code = {
                "evidence_missing_code": "signed_evidence_missing",
                "evidence_tampered": "signed_evidence_tampered",
                "evidence_malformed": "signed_evidence_malformed",
                "evidence_wrong_version": "signed_evidence_wrong_version",
                "evidence_wrong_purpose": "signed_evidence_wrong_purpose",
                "evidence_expired": "signed_evidence_expired",
                "evidence_binding_mismatch": "signed_evidence_mismatch",
            }[name]
            deps.verify_result = (False, code, None)
    else:
        supplied = not name.startswith("preserved_")
        existing = AREA_ID if not supplied or name == "waiting_area_move" else None
        deps.appointment.waiting_area_id = existing
        command.waiting_area_id = AREA_ID if supplied else None
        command.waiting_area_id_supplied = supplied
        refreshed = check_in_proposal_freshness_id(command, check_in_state_payload(deps.appointment))
        proposal.check_in_proposal_freshness_id = refreshed
        body.check_in_proposal_freshness_id = refreshed
        if name in {"waiting_area_location_missing", "preserved_area_location_missing"}:
            deps.appointment.location_id = None
        elif name in {"waiting_area_lookup_missing", "preserved_area_lookup_missing"}:
            deps.areas = {}
        elif name == "waiting_area_wrong_id":
            deps.areas = {AREA_ID: _area(area_id=OTHER_AREA_ID)}
        elif name == "waiting_area_wrong_practice":
            deps.areas = {AREA_ID: _area(practice_id=OTHER_PRACTICE_ID)}
        elif name in {"waiting_area_inactive", "preserved_area_inactive"}:
            deps.areas = {AREA_ID: _area(active=False)}
        elif name == "waiting_area_locationless":
            deps.areas = {AREA_ID: _area(location_id=None)}
        elif name in {
            "waiting_area_location_mismatch",
            "preserved_area_location_mismatch",
        }:
            deps.areas = {AREA_ID: _area(location_id=OTHER_LOCATION_ID)}
        elif name == "waiting_area_move":
            deps.areas = {AREA_ID: _area()}
    return body


@pytest.mark.parametrize("mutation", HOSTILE_MUTATIONS)
def test_at_least_sixty_hostile_contract_mutations_fail_closed_without_commit(
    mutation: str,
) -> None:
    deps = FakeDependencies()
    body = _body(deps.appointment)
    overrides: dict[str, Any] = {}
    body = _apply_hostile_mutation(mutation, deps, body, overrides)

    result = _run(deps, body, **overrides)

    assert len(HOSTILE_MUTATIONS) >= 60
    assert result.kind == "stopped", mutation
    assert result.response_body["receipt"] is None
    assert deps.commits == 0
    assert not deps.effect_plans, mutation


def test_claim_and_verifier_receive_exact_bounded_bindings_without_release() -> None:
    deps = FakeDependencies()

    result = _run(deps)

    assert result.kind == "confirmed_write"
    assert deps.claim_kwargs["operation_id"] == CHECK_IN_OPERATION_ID
    assert deps.claim_kwargs["route_family"] == CHECK_IN_ROUTE_FAMILY
    assert deps.claim_kwargs["confirmation_evidence_hash"] == hashlib.sha256(
        EVIDENCE.encode("utf-8")
    ).hexdigest()
    assert deps.verify_kwargs["expected_practice_id"] == str(PRACTICE_ID)
    assert deps.verify_kwargs["expected_actor_user_id"] == str(ACTOR_ID)
    assert deps.verify_kwargs["expected_appointment_id"] == str(APPOINTMENT_ID)
    assert deps.verify_kwargs["expected_status_before"] == "Booked"
    assert deps.verify_kwargs["expected_waiting_area_id_before"] is None
    assert deps.verify_kwargs["expected_waiting_area_id_target"] is None


def test_non_utc_or_naive_injected_time_fails_before_claim() -> None:
    for invalid in (
        datetime(2026, 8, 18, 0, 0),
        datetime(2026, 8, 18, 10, 0, tzinfo=timezone(timedelta(hours=10))),
    ):
        deps = FakeDependencies()
        result = _run(deps, now=invalid)
        assert result.kind == "stopped"
        assert deps.calls == []
