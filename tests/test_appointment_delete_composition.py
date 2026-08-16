from __future__ import annotations

import copy
import hashlib
import json
import uuid
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from app.services.appointment_delete_composition import (
    DELETE_CONFIRM_AUDIT_LABELS,
    DELETE_CONFIRM_INTENT,
    DELETE_CONFIRM_PUBLIC_SCHEMA,
    DELETE_CONFIRM_RECEIPT_SCHEMA,
    DELETE_CONFIRM_WARNING_REGISTRY,
    DeleteConfirmEffectResult,
    DeleteConfirmServerIngress,
    canonical_delete_confirm_envelope_bytes,
    compose_delete_confirm,
    delete_confirm_envelope_projection,
    validate_delete_confirm_private_receipt_bytes,
)
from app.services.appointment_delete_physical import (
    DeleteConfirmAuthorityRevoked,
    DeleteConfirmPhysicalDecision,
    DeleteConfirmTargetUnavailable,
    canonical_delete_confirm_response_bytes,
)


IDEMPOTENCY_SECRET = b"idempotency-secret-for-delete-composition"
BINDING_SECRET = b"session-binding-secret-for-delete-composition"

APPOINTMENT_ID = uuid.uuid4()
PRACTICE_ID = uuid.uuid4()
ACTOR_ID = uuid.uuid4()


def _canonical_digest(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _private_receipt(
    *,
    appointment_id=APPOINTMENT_ID,
    status_reason_code="PATIENT_CANCELLED",
    cancellation_reason=None,
    warnings=(),
) -> bytes:
    return canonical_delete_confirm_response_bytes(
        appointment_id=appointment_id,
        status_reason_code=status_reason_code,
        cancellation_reason=cancellation_reason,
        warning_codes=warnings,
    )


def _appointment(*, id=APPOINTMENT_ID, status="Booked", version=7, waiting_area_id=None,
                 status_reason_code=None, cancellation_reason=None) -> SimpleNamespace:
    return SimpleNamespace(
        id=id,
        practice_id=PRACTICE_ID,
        status=status,
        waiting_area_id=waiting_area_id,
        status_reason_code=status_reason_code,
        cancellation_reason=cancellation_reason,
        appointment_state_version=version,
    )


def _ingress(*, current_state=None, authority_generation=3,
             authority_current=True, expected_freshness_id="fresh",
             evidence_status="verified", evidence_purpose="diary_confirm_delete_proposal",
             evidence_binding="exact", session_id="a" * 64) -> DeleteConfirmServerIngress:
    return DeleteConfirmServerIngress(
        practice_id=PRACTICE_ID,
        actor_id=ACTOR_ID,
        actor_role="Receptionist",
        authority_generation=authority_generation,
        session_id=session_id,
        authority_current=authority_current,
        current_state=current_state
        if current_state is not None
        else {
            "appointment_id": str(APPOINTMENT_ID),
            "status": "Booked",
            "status_reason_code": None,
            "waiting_area_id": None,
            "cancellation_reason": None,
            "source_version": 7,
        },
        expected_freshness_id=expected_freshness_id,
        evidence_status=evidence_status,
        evidence_purpose=evidence_purpose,
        expected_evidence_purpose=evidence_purpose,
        evidence_binding=evidence_binding,
    )


def _command(**overrides) -> dict:
    values = {
        "kind": "delete",
        "appointment_id": str(APPOINTMENT_ID),
        "clears_waiting_area": False,
        "cancellation_reason": None,
        "status_reason_code": "PATIENT_CANCELLED",
    }
    values.update(overrides)
    return values


def _kernel_request(*, ingress, command=None, source_version=7, warnings=(),
                    idempotency_key="synthetic-idempotency-key",
                    authority_generation=None) -> dict:
    command = command if command is not None else _command()
    request = {
        "schema_version": "raisa.delete_kernel_request.v1",
        "operation_id": "confirmAppointmentDeleteProposal",
        "route_family": "delete-confirm",
        "practice_id": str(ingress.practice_id),
        "actor_id": str(ingress.actor_id),
        "actor_role": ingress.actor_role,
        "authority_generation": authority_generation
        if authority_generation is not None
        else ingress.authority_generation,
        "session_id": ingress.session_id,
        "idempotency_key": idempotency_key,
        "target_appointment_id": command["appointment_id"],
        "source_version": source_version,
        "command": dict(command),
        "warning_codes": list(warnings),
        "lock_plan": ["user", "appointment", "idempotency_record"],
        "signed_evidence_binding_digest": "0" * 64,
        "effect_authority": False,
    }
    request["request_digest"] = _canonical_digest(request)
    return request


def _ready_adapter(request, *, locked_request=None):
    calls = {"count": 0}

    def adapter(value: dict) -> dict:
        calls["count"] += 1
        chosen = locked_request if calls["count"] > 1 and locked_request is not None else request
        return {
            "kind": "kernel_request_ready",
            "outcome": None,
            "reason": None,
            "kernel_request": chosen,
            "effect_authority": False,
        }

    return adapter


def _stopped_adapter(reason="validation_rejected", outcome="validation_rejected"):
    def adapter(value: dict) -> dict:
        return {
            "kind": "stopped",
            "outcome": outcome,
            "reason": reason,
            "kernel_request": None,
            "effect_authority": False,
        }

    return adapter


def _locked_factory(locked_mapping=None):
    def build(appointment: Any, ingress: DeleteConfirmServerIngress) -> dict:
        if locked_mapping is not None:
            return locked_mapping
        return ingress.as_adapter_mapping()

    return build


def _stage_effect(audit_id=None, *, increment_version=True, bad_audit=False):
    def stage(decision: DeleteConfirmPhysicalDecision, request: dict) -> DeleteConfirmEffectResult:
        appointment = decision.appointment
        command = request["command"]
        appointment.status = "Cancelled"
        appointment.waiting_area_id = None
        appointment.status_reason_code = command["status_reason_code"]
        appointment.cancellation_reason = command["cancellation_reason"]
        if increment_version:
            appointment.appointment_state_version += 1
        if bad_audit:
            return DeleteConfirmEffectResult(audit_log_id=None)
        return DeleteConfirmEffectResult(audit_log_id=audit_id or uuid.uuid4())

    return stage


class FakeCommandSession:
    def __init__(self, appointment: SimpleNamespace) -> None:
        self.appointment = appointment
        self.audits: list[object] = []
        self.closed = False

    def add(self, value: object) -> None:
        self.audits.append(value)

    def flush(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True


class FakeDeleteTransaction:
    def __init__(
        self,
        appointment: SimpleNamespace,
        *,
        conflict: bool = False,
        legacy: bool = False,
        in_progress: bool = False,
        corrupt: bool = False,
    ) -> None:
        self.appointment = appointment
        self.entries = 0
        self.records: dict[tuple[str, str, str], SimpleNamespace] = {}
        self.rolled_back = False
        self.conflict = conflict
        self.legacy = legacy
        self.in_progress = in_progress
        self.corrupt = corrupt

    @contextmanager
    def __call__(self, db: FakeCommandSession, **arguments: object):
        self.entries += 1
        if str(self.appointment.id) != str(arguments["target_appointment_id"]):
            raise DeleteConfirmTargetUnavailable("target unavailable")
        key = (
            str(arguments["practice_id"]),
            str(arguments["actor_user_id"]),
            str(arguments["idempotency_key_hash"]),
        )
        record = self.records.get(key)
        inserted = record is None
        if inserted:
            record = SimpleNamespace(
                id=uuid.uuid4(),
                state="in_progress",
                actor_role=arguments["actor_role"],
                target_appointment_id=self.appointment.id,
                request_body_hash=arguments["request_body_hash"],
                session_binding_digest=arguments["session_binding_digest"],
                authority_generation=arguments["signed_authority_generation"],
                completed_receipt_version=None,
                response_status_code=None,
                response_body_hash=None,
                response_body_json=None,
                response_body_canonical_bytes=None,
                result_kind=None,
                audit_log_id=None,
                pre_state_version=None,
                post_state_version=None,
                bernie_session_id=None,
            )
            self.records[key] = record

        if inserted:
            kind = "new_command"
        elif self.conflict:
            kind = "conflict"
        elif self.legacy:
            kind = "legacy_receipt_not_replayable"
        elif self.in_progress:
            kind = "in_progress_not_replayable"
        elif self.corrupt:
            kind = "receipt_integrity_failure"
        else:
            kind = "replay"

        decision = DeleteConfirmPhysicalDecision(
            kind=kind,
            user=None,
            appointment=self.appointment,
            record=record,
            pre_state_version=self.appointment.appointment_state_version,
            response_body_canonical_bytes=(
                record.response_body_canonical_bytes if kind == "replay" else None
            ),
        )
        before = copy.deepcopy(vars(self.appointment))
        audit_count = len(db.audits)
        try:
            yield decision
        except Exception:
            self.rolled_back = True
            vars(self.appointment).clear()
            vars(self.appointment).update(before)
            del db.audits[audit_count:]
            if inserted:
                self.records.pop(key, None)
            raise


def _run(
    *,
    ingress=None,
    request=None,
    appointment=None,
    db=None,
    physical=None,
    adapter=None,
    locked_factory=None,
    stage=None,
    stopped=None,
):
    ingress = ingress or _ingress()
    appointment = appointment or _appointment()
    request = request or _kernel_request(ingress=ingress)
    db = db or FakeCommandSession(appointment)
    physical = physical or FakeDeleteTransaction(appointment)
    if stopped is not None:
        adapter = _stopped_adapter(reason=stopped, outcome=stopped)
    adapter = adapter or _ready_adapter(request)
    locked_factory = locked_factory or _locked_factory()
    stage = stage or _stage_effect()
    result = compose_delete_confirm(
        {"operation_id": "confirmAppointmentDeleteProposal",
         "route_family": "delete-confirm",
         "idempotency_key": "synthetic-idempotency-key",
         "confirmed": True,
         "proposal_intent": "delete_appointment",
         "proposal_safe": True,
         "requires_confirmation": True,
         "autonomy_tier": "proposal",
         "command": request["command"],
         "proposal_warning_codes": [],
         "confirmed_warning_codes": [],
         "freshness_id": ingress.expected_freshness_id,
         "signed_evidence_required": True,
         },
        server_ingress=ingress,
        db=db,
        idempotency_secret=IDEMPOTENCY_SECRET,
        session_binding_secret=BINDING_SECRET,
        admission_adapter=adapter,
        locked_server_factory=locked_factory,
        stage_effect=stage,
        transaction_factory=physical,
    )
    return result, db, physical


def test_private_receipt_validation_rejects_hostile_bytes() -> None:
    valid = _private_receipt()
    assert validate_delete_confirm_private_receipt_bytes(valid)["status"] == "Cancelled"

    reordered = json.loads(valid)
    items = list(reordered.items())
    reordered = dict(reversed(items))
    with pytest.raises(ValueError, match="field order"):
        validate_delete_confirm_private_receipt_bytes(
            json.dumps(reordered, separators=(",", ":")).encode("utf-8")
        )

    pretty = json.dumps(json.loads(valid), indent=2).encode("utf-8")
    with pytest.raises(ValueError, match="canonical compact"):
        validate_delete_confirm_private_receipt_bytes(pretty)

    with pytest.raises(ValueError, match="Cancelled"):
        bad_status = json.loads(valid)
        bad_status["status"] = "Booked"
        validate_delete_confirm_private_receipt_bytes(
            json.dumps(bad_status, separators=(",", ":")).encode("utf-8")
        )

    with pytest.raises(ValueError, match="waiting area"):
        bad_area = json.loads(valid)
        bad_area["waiting_area_id"] = str(uuid.uuid4())
        validate_delete_confirm_private_receipt_bytes(
            json.dumps(bad_area, separators=(",", ":")).encode("utf-8")
        )

    with pytest.raises(ValueError, match="reason code"):
        bad_reason = json.loads(valid)
        bad_reason["status_reason_code"] = "LEGACY_UNCLASSIFIED"
        validate_delete_confirm_private_receipt_bytes(
            json.dumps(bad_reason, separators=(",", ":")).encode("utf-8")
        )

    with pytest.raises(ValueError, match="too long"):
        bad_text = json.loads(valid)
        bad_text["cancellation_reason"] = "x" * 501
        validate_delete_confirm_private_receipt_bytes(
            json.dumps(bad_text, separators=(",", ":")).encode("utf-8")
        )

    with pytest.raises(ValueError, match="warning codes"):
        bad_warnings = json.loads(valid)
        bad_warnings["warning_codes"] = ["waiting_area_cleared", "unknown_code"]
        validate_delete_confirm_private_receipt_bytes(
            json.dumps(bad_warnings, separators=(",", ":")).encode("utf-8")
        )

    with pytest.raises(ValueError, match="not valid UTF-8 JSON"):
        validate_delete_confirm_private_receipt_bytes(b"{not-json")


def test_public_projection_is_exact_minimal_and_sorted() -> None:
    private_bytes = _private_receipt(warnings=["waiting_area_cleared"])
    envelope = delete_confirm_envelope_projection(private_bytes)
    assert envelope["schema_version"] == DELETE_CONFIRM_PUBLIC_SCHEMA
    assert envelope["intent"] == DELETE_CONFIRM_INTENT
    assert envelope["safe"] is True
    assert envelope["requires_confirmation"] is False
    assert envelope["autonomy_tier"] == "confirmed_write"
    assert envelope["summary"] == "Confirmed delete proposal and cancelled one appointment."
    assert envelope["receipt"]["schema_version"] == DELETE_CONFIRM_RECEIPT_SCHEMA
    assert envelope["audit_evidence"] == list(DELETE_CONFIRM_AUDIT_LABELS)
    assert envelope["warnings"] == [
        {
            "code": "waiting_area_cleared",
            "severity": "warning",
            "message": "Deleting this appointment will remove the patient from the waiting area.",
        }
    ]
    assert envelope["receipt"]["warning_codes"] == ["waiting_area_cleared"]

    for forbidden in (
        "appointment",
        "patient",
        "practitioner",
        "schedule",
        "notes",
        "reason",
        "audit_identity",
        "live_projection",
    ):
        assert forbidden not in envelope
        assert forbidden not in envelope["receipt"]

    raw = canonical_delete_confirm_envelope_bytes(envelope)
    assert json.loads(raw) == envelope
    assert list(json.loads(raw).keys()) == sorted(json.loads(raw).keys())
    assert raw == canonical_delete_confirm_envelope_bytes(
        delete_confirm_envelope_projection(_private_receipt(warnings=["waiting_area_cleared"]))
    )


def test_clean_execute_and_replay_are_byte_identical() -> None:
    appointment = _appointment()
    ingress = _ingress()
    request = _kernel_request(ingress=ingress)
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)

    first, _, _ = _run(
        ingress=ingress,
        request=request,
        appointment=appointment,
        db=db,
        physical=physical,
    )
    second, _, _ = _run(
        ingress=ingress,
        request=request,
        appointment=appointment,
        db=db,
        physical=physical,
    )

    assert first.kind == "committed"
    assert second.kind == "replay"
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.body == second.body
    assert first.stored_response_bytes == second.stored_response_bytes
    assert canonical_delete_confirm_envelope_bytes(first.body) == canonical_delete_confirm_envelope_bytes(
        second.body
    )
    assert first.body["receipt"]["status"] == "Cancelled"
    assert first.body["receipt"]["waiting_area_id"] is None
    assert appointment.status == "Cancelled"
    assert appointment.appointment_state_version == 8
    assert physical.entries == 2
    record = next(iter(physical.records.values()))
    assert record.state == "completed"
    assert record.response_status_code == 200
    assert record.result_kind == "confirmed_write"
    assert record.completed_receipt_version == 1
    assert isinstance(record.session_binding_digest, bytes)
    assert len(record.session_binding_digest) == 32
    assert record.pre_state_version == 7
    assert record.post_state_version == 8
    assert isinstance(record.response_body_canonical_bytes, bytes)
    assert record.authority_generation == 3


def test_admission_stop_returns_typed_200_blocked_envelope() -> None:
    ingress = _ingress()
    appointment = _appointment()
    result, db, physical = _run(
        ingress=ingress,
        appointment=appointment,
        stopped="stale_delete_proposal_freshness_id",
    )
    assert result.kind == "blocked"
    assert result.status_code == 200
    assert result.body["safe"] is False
    assert result.body["requires_confirmation"] is True
    assert result.body["autonomy_tier"] == "blocked"
    assert result.body["receipt"] is None
    assert result.body["blocks"] == [
        {
            "code": "stale_delete_proposal_freshness_id",
            "severity": "blocked",
            "message": "The delete confirmation did not pass current checks.",
        }
    ]
    assert db.audits == []
    assert physical.entries == 0


@pytest.mark.parametrize(
    ("flags", "expected_code"),
    [
        ({"conflict": True}, "idempotency_key_conflict"),
        ({"legacy": True}, "legacy_receipt_not_replayable"),
        ({"in_progress": True}, "idempotency_key_in_progress"),
        ({"corrupt": True}, "receipt_integrity_failure"),
    ],
)
def test_closed_outcome_mappings(flags: dict, expected_code: str) -> None:
    appointment = _appointment()
    ingress = _ingress()
    request = _kernel_request(ingress=ingress)
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)
    # First clean execute creates and completes the record under the same key.
    first, db, physical = _run(
        ingress=ingress,
        request=request,
        appointment=appointment,
        db=db,
        physical=physical,
    )
    assert first.kind == "committed"
    # Reuse the completed record but force the closed classification.
    physical.conflict = flags.get("conflict", False)
    physical.legacy = flags.get("legacy", False)
    physical.in_progress = flags.get("in_progress", False)
    physical.corrupt = flags.get("corrupt", False)
    result, db, physical = _run(
        ingress=ingress,
        request=request,
        appointment=appointment,
        db=db,
        physical=physical,
    )
    assert result.kind == "error"
    assert result.status_code == (
        503 if expected_code == "receipt_integrity_failure" else 409
    )
    assert result.body["detail"]["code"] == expected_code
    assert db.audits == []


def test_authority_revoked_maps_to_403() -> None:
    ingress = _ingress()
    appointment = _appointment()

    class RevokingTransaction(FakeDeleteTransaction):
        @contextmanager
        def __call__(self, db: FakeCommandSession, **arguments: object):
            raise DeleteConfirmAuthorityRevoked("current authority unavailable")

    result, db, physical = _run(
        ingress=ingress,
        appointment=appointment,
        physical=RevokingTransaction(appointment),
    )
    assert result.kind == "error"
    assert result.status_code == 403
    assert result.body["detail"]["code"] == "current_authority_unavailable"
    assert db.audits == []


def test_target_unavailable_maps_to_indistinguishable_404() -> None:
    ingress = _ingress()
    appointment = _appointment()
    other = _appointment(id=uuid.uuid4())
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(other)

    result, db, physical = _run(
        ingress=ingress,
        appointment=appointment,
        db=db,
        physical=physical,
    )
    assert result.kind == "error"
    assert result.status_code == 404
    assert result.body["detail"]["code"] == "appointment_not_found"
    assert db.audits == []


def test_locked_readmission_requires_identical_digest() -> None:
    appointment = _appointment()
    ingress = _ingress()
    request = _kernel_request(ingress=ingress)
    locked_changed = _kernel_request(
        ingress=ingress,
        source_version=8,
        command=_command(status_reason_code="OTHER"),
    )
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)
    result, db, physical = _run(
        ingress=ingress,
        request=request,
        appointment=appointment,
        db=db,
        physical=physical,
        adapter=_ready_adapter(request, locked_request=locked_changed),
    )
    assert result.kind == "blocked"
    assert result.body["blocks"][0]["code"] == "locked_request_digest_changed"
    assert appointment.status == "Booked"
    assert appointment.appointment_state_version == 7
    assert db.audits == []
    assert physical.records == {}


def test_warning_registry_projection_matches_frozen_registry() -> None:
    private_bytes = _private_receipt(warnings=["waiting_area_cleared"])
    envelope = delete_confirm_envelope_projection(private_bytes)
    assert envelope["warnings"] == [DELETE_CONFIRM_WARNING_REGISTRY["waiting_area_cleared"]]
    assert envelope["receipt"]["warning_codes"] == ["waiting_area_cleared"]


def test_hostile_public_envelope_mutations_fail_closed() -> None:
    envelope = delete_confirm_envelope_projection(_private_receipt())
    for mutator in (
        lambda value: {**value, "unexpected": True},
        lambda value: {**value, "safe": False},
        lambda value: {**value, "audit_evidence": []},
        lambda value: {
            **value,
            "receipt": {**value["receipt"], "warning_codes": ["unknown_code"]},
        },
        lambda value: {
            **value,
            "warnings": [dict(DELETE_CONFIRM_WARNING_REGISTRY["waiting_area_cleared"])],
        },
    ):
        with pytest.raises(ValueError):
            canonical_delete_confirm_envelope_bytes(mutator(copy.deepcopy(envelope)))


def test_bad_effect_audit_identity_maps_to_503_and_rolls_back() -> None:
    appointment = _appointment()
    ingress = _ingress()
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)
    result, db, physical = _run(
        ingress=ingress,
        appointment=appointment,
        db=db,
        physical=physical,
        stage=_stage_effect(bad_audit=True),
    )
    assert result.kind == "error"
    assert result.status_code == 503
    assert result.body["detail"]["code"] == "delete_confirm_transaction_unavailable"
    assert appointment.status == "Booked"
    assert appointment.appointment_state_version == 7
    assert db.audits == []
    assert physical.records == {}
    assert physical.rolled_back is True


def test_mismatched_staged_reason_maps_to_503() -> None:
    appointment = _appointment()
    ingress = _ingress()
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)

    def bad_stage(decision: DeleteConfirmPhysicalDecision, request: dict) -> DeleteConfirmEffectResult:
        decision.appointment.status = "Cancelled"
        decision.appointment.waiting_area_id = None
        decision.appointment.status_reason_code = "OTHER"
        decision.appointment.cancellation_reason = None
        decision.appointment.appointment_state_version += 1
        return DeleteConfirmEffectResult(audit_log_id=uuid.uuid4())

    result, db, physical = _run(
        ingress=ingress,
        appointment=appointment,
        db=db,
        physical=physical,
        stage=bad_stage,
    )
    assert result.kind == "error"
    assert result.status_code == 503
    assert appointment.status == "Booked"
    assert db.audits == []
    assert physical.rolled_back is True


def test_admission_stop_authority_revoked_maps_to_403() -> None:
    result, _db, physical = _run(
        ingress=_ingress(),
        appointment=_appointment(),
        stopped="authority_revoked",
    )
    assert result.kind == "error"
    assert result.status_code == 403
    assert result.body["detail"]["code"] == "current_authority_unavailable"
    assert physical.entries == 0


def test_admission_stop_idempotency_missing_maps_to_409() -> None:
    result, _db, physical = _run(
        ingress=_ingress(),
        appointment=_appointment(),
        stopped="idempotency_conflict",
    )
    assert result.kind == "error"
    assert result.status_code == 409
    assert result.body["detail"]["code"] == "idempotency_key_required"
    assert physical.entries == 0


def test_effect_staging_writes_complete_private_receipt() -> None:
    appointment = _appointment()
    ingress = _ingress()
    request = _kernel_request(
        ingress=ingress,
        command=_command(cancellation_reason="Patient requested reschedule"),
        warnings=["waiting_area_cleared"],
    )
    appointment.waiting_area_id = uuid.uuid4()
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)
    result, db, physical = _run(
        ingress=ingress,
        request=request,
        appointment=appointment,
        db=db,
        physical=physical,
    )
    assert result.kind == "committed"
    assert result.body["receipt"]["cancellation_reason"] == "Patient requested reschedule"
    assert result.body["receipt"]["warning_codes"] == ["waiting_area_cleared"]
    record = next(iter(physical.records.values()))
    assert record.state == "completed"
    assert record.response_status_code == 200
    assert record.response_body_hash == hashlib.sha256(
        record.response_body_canonical_bytes
    ).hexdigest()
    assert json.loads(record.response_body_canonical_bytes) == record.response_body_json
    assert record.pre_state_version == 7
    assert record.post_state_version == 8
    assert record.authority_generation == 3
    assert record.audit_log_id is not None
    assert isinstance(record.session_binding_digest, bytes)
    assert len(record.session_binding_digest) == 32
