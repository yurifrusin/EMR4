"""Default-off Reception One product-context proposal runtime.

The planner receives a minimal authored-synthetic frame with opaque,
request-scoped handles. Database reads happen only in the trusted context desk;
the accepted typed-plan proofreader and executor remain proposal-only.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from dataclasses import dataclass
import hashlib
import hmac
import re
import secrets
from typing import Any
import uuid

from sqlalchemy.orm import Session

from app.models.appointments import Appointment, AppointmentStatus
from app.models.patients import Patient
from app.models.tenancy import Practitioner
from app.schemas.appointments import (
    ReceptionOneProductContextAdapterReviewOut,
    ReceptionOneProductContextAppointmentOut,
    ReceptionOneProductContextProposalOut,
    ReceptionOneProductContextReviewOut,
    ReceptionOneProductContextSlotOut,
    SlotSearchProposalIn,
    SlotSearchProposalOut,
)
from app.services.bernie.semantic_extraction import extract_semantics
from app.services.appointment_lifecycle import LifecycleRejected, bureau_status


CONTRACT_VERSION = "reception.one.bureau.plan-input.v1"
DEFAULT_DURATION_MINUTES = 15
MAX_ENTITY_SCAN = 200
MAX_APPOINTMENTS = 24
MAX_CANDIDATE_SLOTS = 8


class ReceptionOneRuntimeError(ValueError):
    """A bounded runtime-context or proofreader failure."""


def practice_is_allowlisted(practice_id: uuid.UUID, raw_allowlist: str) -> bool:
    allowed = {
        item.strip().lower()
        for item in (raw_allowlist or "").split(",")
        if item.strip()
    }
    return str(practice_id).lower() in allowed


def _normalized_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).casefold()).strip()


def _term_present(instruction: str, term: str) -> bool:
    normalized_instruction = f" {_normalized_text(instruction)} "
    normalized_term = _normalized_text(term)
    return bool(normalized_term) and f" {normalized_term} " in normalized_instruction


def _opaque_handle(
    kind: str,
    source_id: object,
    *,
    handle_key: bytes,
) -> str:
    digest = hmac.new(
        handle_key,
        f"{kind}:{source_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:20]
    return f"synthetic-{kind}-{digest}"


def _safe_status(value: AppointmentStatus | str | None) -> str:
    raw = value.value if isinstance(value, AppointmentStatus) else value
    try:
        return bureau_status(raw)
    except LifecycleRejected:
        raise ReceptionOneRuntimeError("unsupported_appointment_status") from None


def _read_entities(
    db: Session,
    *,
    practice_id: uuid.UUID,
    instruction: str,
    handle_key: bytes,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, uuid.UUID]]:
    patient_rows = (
        db.query(Patient.id, Patient.first_name, Patient.last_name)
        .filter(Patient.practice_id == practice_id)
        .order_by(Patient.last_name, Patient.first_name)
        .limit(MAX_ENTITY_SCAN)
        .all()
    )
    practitioner_rows = (
        db.query(
            Practitioner.id,
            Practitioner.first_name,
            Practitioner.last_name,
        )
        .filter(
            Practitioner.practice_id == practice_id,
            Practitioner.is_active.is_(True),
        )
        .order_by(Practitioner.last_name, Practitioner.first_name)
        .limit(MAX_ENTITY_SCAN)
        .all()
    )

    handle_map: dict[str, uuid.UUID] = {}
    patients: list[dict[str, Any]] = []
    for row in patient_rows:
        display = f"{row.first_name} {row.last_name}".strip()
        if not _term_present(instruction, display):
            continue
        handle = _opaque_handle("patient", row.id, handle_key=handle_key)
        handle_map[handle] = row.id
        patients.append(
            {
                "id": handle,
                "display": display,
                "aliases": [row.first_name],
            }
        )
        if len(patients) >= 8:
            break

    practitioners: list[dict[str, Any]] = []
    for row in practitioner_rows:
        short_display = f"Dr {row.last_name}".strip()
        full_display = f"Dr {row.first_name} {row.last_name}".strip()
        if not (
            _term_present(instruction, short_display)
            or _term_present(instruction, full_display)
            or _term_present(instruction, row.last_name)
        ):
            continue
        handle = _opaque_handle("practitioner", row.id, handle_key=handle_key)
        handle_map[handle] = row.id
        practitioners.append(
            {
                "id": handle,
                "display": (
                    short_display
                    if _term_present(instruction, short_display)
                    else full_display
                ),
                "aliases": [full_display, row.last_name],
            }
        )
        if len(practitioners) >= 8:
            break

    return patients, practitioners, handle_map


def _read_appointments(
    db: Session,
    *,
    practice_id: uuid.UUID,
    target_date: date,
    patient_ids: set[uuid.UUID],
    practitioner_ids: set[uuid.UUID],
    handle_key: bytes,
    handle_map: dict[str, uuid.UUID],
) -> list[dict[str, Any]]:
    query = db.query(
        Appointment.id,
        Appointment.patient_id,
        Appointment.practitioner_id,
        Appointment.appointment_date,
        Appointment.start_time_local,
        Appointment.duration_minutes,
        Appointment.status,
    ).filter(
        Appointment.practice_id == practice_id,
        Appointment.appointment_date == target_date,
    )
    if patient_ids and practitioner_ids:
        query = query.filter(
            (Appointment.patient_id.in_(patient_ids))
            | (Appointment.practitioner_id.in_(practitioner_ids))
        )
    elif patient_ids:
        query = query.filter(Appointment.patient_id.in_(patient_ids))
    elif practitioner_ids:
        query = query.filter(Appointment.practitioner_id.in_(practitioner_ids))
    else:
        return []

    reverse_handles = {value: key for key, value in handle_map.items()}
    result: list[dict[str, Any]] = []
    for row in (
        query.order_by(Appointment.start_time_local)
        .limit(MAX_APPOINTMENTS)
        .all()
    ):
        patient_ref = reverse_handles.get(row.patient_id)
        practitioner_ref = reverse_handles.get(row.practitioner_id)
        if patient_ref is None or practitioner_ref is None:
            continue
        result.append(
            {
                "id": _opaque_handle(
                    "appointment",
                    row.id,
                    handle_key=handle_key,
                ),
                "patient_ref": patient_ref,
                "practitioner_ref": practitioner_ref,
                "date": row.appointment_date.isoformat(),
                "start_time": row.start_time_local.strftime("%H:%M"),
                "duration_minutes": row.duration_minutes
                or DEFAULT_DURATION_MINUTES,
                "status": _safe_status(row.status),
            }
        )
    return result


def _slot_context(
    proposal: SlotSearchProposalOut | None,
    *,
    practitioner_handle: str,
    handle_key: bytes,
    classification: str = "available",
) -> list[dict[str, Any]]:
    if proposal is None or not proposal.safe:
        return []
    result: list[dict[str, Any]] = []
    for index, candidate in enumerate(
        proposal.candidates[:MAX_CANDIDATE_SLOTS]
    ):
        source = (
            candidate.candidate_freshness_id
            or (
                f"{candidate.appointment_date.isoformat()}:"
                f"{candidate.start_time_local.isoformat()}:"
                f"{candidate.duration_minutes}:{index}"
            )
        )
        result.append(
            {
                "id": _opaque_handle(
                    "slot",
                    source,
                    handle_key=handle_key,
                ),
                "practitioner_ref": practitioner_handle,
                "date": candidate.appointment_date.isoformat(),
                "start_time": candidate.start_time_local.strftime("%H:%M"),
                "duration_minutes": candidate.duration_minutes,
                "classification": classification,
                "warning_codes": (
                    ["manual_squeeze_in_review", "no_reservation"]
                    if classification == "squeeze_in_review"
                    else ["no_reservation"]
                ),
            }
        )
    return result


def _read_selected_appointment(
    db: Session,
    *,
    practice_id: uuid.UUID,
    appointment_id: uuid.UUID,
    handle_key: bytes,
    handle_map: dict[str, uuid.UUID],
    patients: list[dict[str, Any]],
    practitioners: list[dict[str, Any]],
    allow_unmentioned_parties: bool,
    source_capture: list | None = None,
) -> dict[str, Any]:
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.practice_id == practice_id,
        )
        .first()
    )
    if appointment is None:
        raise ReceptionOneRuntimeError("selected_appointment_not_found")
    patient = (
        db.query(Patient)
        .filter(Patient.id == appointment.patient_id, Patient.practice_id == practice_id)
        .first()
    )
    practitioner = (
        db.query(Practitioner)
        .filter(
            Practitioner.id == appointment.practitioner_id,
            Practitioner.practice_id == practice_id,
            Practitioner.is_active.is_(True),
        )
        .first()
    )
    if patient is None or getattr(patient, "is_active", True) is not True:
        raise ReceptionOneRuntimeError("selected_patient_unavailable")
    if practitioner is None:
        raise ReceptionOneRuntimeError("selected_practitioner_unavailable")
    reverse_handles = {value: key for key, value in handle_map.items()}
    patient_ref = reverse_handles.get(appointment.patient_id)
    practitioner_ref = reverse_handles.get(appointment.practitioner_id)
    if (patient_ref is None or practitioner_ref is None) and not allow_unmentioned_parties:
        raise ReceptionOneRuntimeError(
            "selected_appointment_not_grounded_in_instruction"
        )
    if patient_ref is None:
        if len(patients) >= 8:
            raise ReceptionOneRuntimeError("selected_context_entity_limit")
        patient_ref = _opaque_handle("patient", patient.id, handle_key=handle_key)
        patients.append({
            "id": patient_ref,
            "display": f"{patient.first_name} {patient.last_name}".strip(),
            "aliases": [patient.first_name],
        })
        handle_map[patient_ref] = patient.id
    if practitioner_ref is None:
        if len(practitioners) >= 8:
            raise ReceptionOneRuntimeError("selected_context_entity_limit")
        practitioner_ref = _opaque_handle("practitioner", practitioner.id, handle_key=handle_key)
        practitioners.append({
            "id": practitioner_ref,
            "display": f"Dr {practitioner.last_name}".strip(),
            "aliases": [
                f"Dr {practitioner.first_name} {practitioner.last_name}".strip(),
                practitioner.last_name,
            ],
        })
        handle_map[practitioner_ref] = practitioner.id
    appointment_handle = _opaque_handle(
        "appointment",
        appointment.id,
        handle_key=handle_key,
    )
    handle_map[appointment_handle] = appointment.id
    if source_capture is not None:
        # Actual row facts; never use the public frame duration default or HMAC.
        source_capture.append({
            "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_revision": appointment.appointment_state_version,
            "selected_appointment_id": str(appointment.id),
            "selected_state_version": appointment.appointment_state_version,
            "selected_status": appointment.status.value,
            "selected_date": appointment.appointment_date.isoformat(),
            "selected_start_local": appointment.start_time_local.strftime("%H:%M"),
            "patient_id": str(appointment.patient_id) if appointment.patient_id else None,
            "practitioner_id": str(appointment.practitioner_id),
            "appointment_type_id": str(appointment.appointment_type_id) if appointment.appointment_type_id else None,
            "location_id": str(appointment.location_id) if appointment.location_id else None,
            "duration_minutes": appointment.duration_minutes,
        })
    return {
        "id": appointment_handle,
        "patient_ref": patient_ref,
        "practitioner_ref": practitioner_ref,
        "date": appointment.appointment_date.isoformat(),
        "start_time": appointment.start_time_local.strftime("%H:%M"),
        "duration_minutes": (
            appointment.duration_minutes or DEFAULT_DURATION_MINUTES
        ),
        "status": _safe_status(appointment.status),
    }



@dataclass(frozen=True)
class SelectedMoveSource:
    """Request-local server-only observation; never part of the model frame."""
    frame_sha256: str
    request_id: str
    selected_handle: str
    context_items: tuple


def point_move_envelope(*, frame, normalized_plan, review, execution,
                        provenance, capture, tenant_id, actor_id,
                        selected_appointment_id, now):
    """Revalidate the closed final-frame/plan/output/observed-source join."""
    from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
    from app.services.appointment_lifecycle import validate_move_intent

    if (type(capture) is not SelectedMoveSource or now.tzinfo is None
            or not all(isinstance(value, dict) for value in (normalized_plan, review, execution))):
        raise ReceptionOneRuntimeError("point_source_capture_required")
    frame_hash = typed_plan.canonical_sha256(frame)
    plan_hash = typed_plan.canonical_sha256(normalized_plan)
    if (capture.frame_sha256 != frame_hash or capture.request_id != frame["request_id"]
            or not isinstance(provenance, dict)
            or set(provenance) != {"raw_response_sha256", "packet_sha256", "frame_sha256",
                                   "context_revision", "packet_schema_version",
                                   "constructor_version", "compiled_plan_sha256"}
            or provenance.get("frame_sha256") != frame_hash
            or provenance.get("compiled_plan_sha256") != plan_hash
            or provenance.get("context_revision") != frame["context_revision"]
            or provenance.get("packet_schema_version") != typed_plan.POINT_PACKET_VERSION
            or provenance.get("constructor_version") != typed_plan.POINT_CONSTRUCTOR_VERSION
            or any(not isinstance(provenance.get(key), str)
                   or not re.fullmatch(r"[0-9a-f]{64}", provenance[key])
                   for key in ("raw_response_sha256", "packet_sha256"))
            or normalized_plan.get("contract_version") != typed_plan.POINT_PLAN_VERSION
            or review.get("safe_repairs")):
        raise ReceptionOneRuntimeError("point_execution_join_refused")
    expected = typed_plan.execute_plan(frame, normalized_plan, review, now=now)
    # Full pure executions retain their exact receipt; the existing planner
    # projection carries only final_output. Both require exact deterministic data.
    if (set(execution) not in ({"final_output"}, set(expected))
            or execution["final_output"] != expected["final_output"]
            or (set(execution) == set(expected) and execution != expected)):
        raise ReceptionOneRuntimeError("point_execution_output_refused")
    output = expected["final_output"]
    selected = frame["context"]["selected_appointment"]
    context = dict(capture.context_items)
    if (len(context) != len(capture.context_items)
            or selected is None or selected["id"] != capture.selected_handle
            or output["appointment_ref"] != capture.selected_handle
            or output["patient_ref"] != selected["patient_ref"]
            or output["practitioner_ref"] != selected["practitioner_ref"]
            or context.get("tenant_id") != str(tenant_id)
            or context.get("actor_id") != str(actor_id)
            or context.get("selected_appointment_id") != str(selected_appointment_id)
            or type(context.get("duration_minutes")) is not int
            or type(selected["duration_minutes"]) is not int
            or type(output["duration_minutes"]) is not int
            or not 1 <= context["duration_minutes"] <= 480
            or context["duration_minutes"] != selected["duration_minutes"]
            or context["duration_minutes"] != output["duration_minutes"]
            or context.get("source_revision") != context.get("selected_state_version")
            or selected["date"] != context.get("selected_date")
            or selected["start_time"] != context.get("selected_start_local")):
        raise ReceptionOneRuntimeError("point_source_identity_refused")
    # Preserve original captured_at. Only the dispatch clock advances.
    context["as_of"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    envelope = {
        "schema_version": "appointment.move_time_intent.v1",
        "tenant_id": context["tenant_id"], "actor_id": context["actor_id"],
        "role": context["role"],
        "source_appointment_id": context["selected_appointment_id"],
        "source_state_version": context["selected_state_version"],
        "source_revision": context["source_revision"],
        "target_date": output["target_date"],
        "target_start_local": output["target_start_local"],
        "authority": "proposal_only",
    }
    validate_move_intent(envelope, context)
    return envelope


def build_product_context_frame(
    db: Session,
    *,
    practice_id: uuid.UUID,
    instruction: str,
    reference_date: date,
    correlation_id: str,
    slot_proposal: SlotSearchProposalOut | None,
    selected_appointment_id: uuid.UUID | None = None,
    observed_at: datetime | None = None,
    handle_key: bytes | None = None,
    selected_source_capture: list | None = None,
    trusted_actor_id: uuid.UUID | None = None,
    trusted_role: str | None = None,
    trusted_practice_timezone: str | None = None,
) -> tuple[dict[str, Any], dict[str, str], dict[str, uuid.UUID]]:
    from scripts import reception_one_bureau_typed_plan_protocol as typed_plan

    if not instruction.strip():
        raise ReceptionOneRuntimeError("instruction_required")
    if len(instruction) > 512:
        raise ReceptionOneRuntimeError("instruction_too_large")

    effective_now = observed_at or datetime.now(timezone.utc)
    if effective_now.tzinfo is None:
        raise ReceptionOneRuntimeError("timezone_aware_observed_at_required")
    effective_handle_key = handle_key or secrets.token_bytes(32)
    patients, practitioners, handle_map = _read_entities(
        db,
        practice_id=practice_id,
        instruction=instruction,
        handle_key=effective_handle_key,
    )
    extraction = extract_semantics(
        [instruction],
        reference_date.isoformat(),
    )
    target_date_raw = extraction.normalized_values.get("appointment_date")
    target_date = (
        date.fromisoformat(str(target_date_raw))
        if target_date_raw is not None
        else reference_date
    )
    patient_ids = {
        handle_map[item["id"]]
        for item in patients
        if item["id"] in handle_map
    }
    practitioner_ids = {
        handle_map[item["id"]]
        for item in practitioners
        if item["id"] in handle_map
    }
    appointments = _read_appointments(
        db,
        practice_id=practice_id,
        target_date=target_date,
        patient_ids=patient_ids,
        practitioner_ids=practitioner_ids,
        handle_key=effective_handle_key,
        handle_map=handle_map,
    )
    observed_source: list = []
    selected_appointment = (
        _read_selected_appointment(
            db,
            practice_id=practice_id,
            appointment_id=selected_appointment_id,
            handle_key=effective_handle_key,
            handle_map=handle_map,
            patients=patients,
            practitioners=practitioners,
            allow_unmentioned_parties=extraction.intended_action == "move",
            source_capture=observed_source if selected_source_capture is not None else None,
        )
        if selected_appointment_id is not None
        else None
    )
    practitioner_handle = (
        practitioners[0]["id"]
        if len(practitioners) == 1
        else "synthetic-practitioner-unresolved"
    )
    selected_subject = typed_plan.selected_move_subject(
        {"utterances": [instruction], "context": {
            "patients": patients,
            "practitioners": practitioners,
            "selected_appointment": selected_appointment,
        }},
        extraction,
    ) if extraction.intended_action == "move" else None
    candidate_slots = (
        _slot_context(
            slot_proposal,
            practitioner_handle=practitioner_handle,
            handle_key=effective_handle_key,
            classification=(
                "squeeze_in_review"
                if typed_plan.is_squeeze_in_request(
                    {"utterances": [instruction]}
                )
                else "available"
            ),
        )
        if len(practitioners) == 1
        and (extraction.intended_action != "move" or selected_subject is not None)
        else []
    )
    safe_context = {
        "patients": patients,
        "practitioners": practitioners,
        "selected_appointment": selected_appointment,
        "appointments": appointments,
        "candidate_slots": candidate_slots,
        "squeeze_policy": {
            "id": "synthetic-policy-squeeze-review",
            "assessment_enabled": True,
            "allow_move_existing": False,
            "allow_overbook": False,
            "requires_human_review": True,
        },
        "default_duration_minutes": DEFAULT_DURATION_MINUTES,
        "allowed_statuses": ["arrived", "completed", "dna"],
    }
    context_revision = max(
        1,
        int(
            hmac.new(
                effective_handle_key,
                typed_plan.canonical_json(safe_context).encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()[:8],
            16,
        ),
    )
    request_id = _opaque_handle(
        "request",
        f"{correlation_id}:{effective_now.isoformat()}",
        handle_key=effective_handle_key,
    )
    frame = {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "practice_ref": _opaque_handle(
            "practice",
            practice_id,
            handle_key=effective_handle_key,
        ),
        "correlation_id": _opaque_handle(
            "correlation",
            correlation_id,
            handle_key=effective_handle_key,
        ),
        "context_revision": context_revision,
        "observed_at": effective_now.isoformat().replace("+00:00", "Z"),
        "expires_at": (
            effective_now + timedelta(minutes=2)
        ).isoformat().replace("+00:00", "Z"),
        "data_class": "authored_synthetic",
        "utterances": [instruction],
        "reference_date": reference_date.isoformat(),
        "context": safe_context,
        "authority": {
            "effect_ceiling": "proposal_only",
            "appointment_write_authority": False,
            "confirmation_authority": False,
            "provider_execution": False,
            "network_access": False,
            "database_access": False,
            "product_delivery": False,
        },
    }
    typed_plan.validate_schema(frame, "input")
    if selected_source_capture is not None and selected_appointment is not None:
        if selected_source_capture or len(observed_source) != 1:
            raise ReceptionOneRuntimeError("point_capture_not_empty")
        context = dict(observed_source[0])
        context.update(
            tenant_id=str(practice_id), actor_id=str(trusted_actor_id),
            role=trusted_role, move_capability="appointments.move.propose",
            practice_timezone=trusted_practice_timezone,
            as_of=context["captured_at"],
        )
        selected_source_capture.append(SelectedMoveSource(
            frame_sha256=typed_plan.canonical_sha256(frame),
            request_id=frame["request_id"], selected_handle=selected_appointment["id"],
            context_items=tuple(sorted(context.items())),
        ))
    displays = {
        **{item["id"]: item["display"] for item in patients},
        **{item["id"]: item["display"] for item in practitioners},
    }
    return frame, displays, handle_map


def build_slot_search_input(
    frame: dict[str, Any],
    handle_map: dict[str, uuid.UUID],
) -> SlotSearchProposalIn | None:
    from scripts import reception_one_bureau_typed_plan_protocol as typed_plan

    extraction = typed_plan.extraction_for(frame)
    practitioners = frame["context"]["practitioners"]
    patients = frame["context"]["patients"]
    is_squeeze = typed_plan.is_squeeze_in_request(frame)
    if extraction.intended_action not in {"create", "move"} and not is_squeeze:
        return None
    selected = frame["context"].get("selected_appointment")
    if extraction.intended_action == "move":
        if selected is None or typed_plan.selected_move_subject(frame, extraction) is None:
            return None
        practitioner_handle = selected["practitioner_ref"]
        patient_handle = selected["patient_ref"]
    else:
        if len(practitioners) != 1 or len(patients) != 1:
            return None
        practitioner_handle = practitioners[0]["id"]
        patient_handle = patients[0]["id"]
    duration_default = frame["context"]["default_duration_minutes"]
    if extraction.intended_action == "move":
        duration_default = selected["duration_minutes"]
    practitioner_id = handle_map.get(practitioner_handle)
    patient_id = handle_map.get(patient_handle)
    appointment_date = extraction.normalized_values.get("appointment_date")
    if (
        practitioner_id is None
        or patient_id is None
        or appointment_date is None
    ):
        return None
    earliest = extraction.normalized_values.get("earliest_time")
    latest = extraction.normalized_values.get("latest_time")
    duration = extraction.normalized_values.get(
        "duration_minutes",
        duration_default,
    )
    return SlotSearchProposalIn(
        practitioner_id=practitioner_id,
        patient_id=patient_id,
        date_from=date.fromisoformat(str(appointment_date)),
        date_to=date.fromisoformat(str(appointment_date)),
        earliest_time=time.fromisoformat(str(earliest)) if earliest else None,
        latest_time=time.fromisoformat(str(latest)) if latest else None,
        temporal_relation=extraction.temporal_relation,
        duration_minutes=int(duration),
        limit=20,
    )


def build_reviewed_proposal_result(
    *,
    frame: dict[str, Any],
    displays: dict[str, str],
    normalized_plan: dict[str, Any],
    review: dict[str, Any],
    execution: dict[str, Any] | None,
    adapter_review: ReceptionOneProductContextAdapterReviewOut | None = None,
    planner_mode: str = "deterministic",
    provider_calls: int = 0,
    runtime_audit_ref: str | None = None,
) -> ReceptionOneProductContextProposalOut:
    disposition = review["disposition"]
    final_output = execution["final_output"] if execution is not None else {}
    patient_handle = final_output.get("patient_ref")
    practitioner_handle = final_output.get("practitioner_ref")
    slots_by_id = {
        item["id"]: item for item in frame["context"]["candidate_slots"]
    }
    candidate_slots = [
        ReceptionOneProductContextSlotOut(
            slot_handle=slot_id,
            appointment_date=date.fromisoformat(slots_by_id[slot_id]["date"]),
            start_time_local=time.fromisoformat(
                slots_by_id[slot_id]["start_time"]
            ),
            duration_minutes=slots_by_id[slot_id]["duration_minutes"],
            warning_codes=slots_by_id[slot_id]["warning_codes"],
        )
        for slot_id in final_output.get("candidate_slot_ids", [])
        if slot_id in slots_by_id
    ]
    result_by_disposition = {
        "admit": (
            "clarification_required"
            if final_output.get("proposal_family") == "clarification"
            else "proposal_ready"
        ),
        "clarification_required": "clarification_required",
        "revision_required": "revision_required",
        "reject": "blocked",
    }
    result = result_by_disposition[disposition]
    if (
        result == "proposal_ready"
        and adapter_review is not None
        and not adapter_review.safe
    ):
        result = "blocked"
    family = final_output.get("proposal_family")
    if result == "proposal_ready":
        if adapter_review is not None:
            summary = adapter_review.summary
        elif family == "squeeze_in_assessment":
            summary = (
                f"Prepared {len(candidate_slots)} bounded squeeze-in review "
                f"option{'' if len(candidate_slots) == 1 else 's'}. "
                "No appointment has changed."
            )
        else:
            summary = (
                f"Prepared {len(candidate_slots)} current option"
                f"{'' if len(candidate_slots) == 1 else 's'} for staff review. "
                "Nothing has been booked."
            )
    elif result == "clarification_required":
        summary = "Reception One needs one more detail and has released no proposal."
    elif result == "revision_required":
        summary = "The typed plan needs a bounded mechanical revision."
    else:
        summary = (
            adapter_review.summary
            if adapter_review is not None and not adapter_review.safe
            else "The typed plan failed closed and released no proposal."
        )

    selected = frame["context"].get("selected_appointment")
    selected_out = (
        ReceptionOneProductContextAppointmentOut(
            appointment_handle=selected["id"],
            appointment_date=date.fromisoformat(selected["date"]),
            start_time_local=time.fromisoformat(selected["start_time"]),
            duration_minutes=selected["duration_minutes"],
            status=selected["status"],
        )
        if selected is not None
        else None
    )
    proposed_date = None
    proposed_time = None
    if family == "move" and "target_start_local" in final_output:
        proposed_date = date.fromisoformat(final_output["target_date"])
        proposed_time = time.fromisoformat(final_output["target_start_local"])
    elif family == "move" and candidate_slots:
        proposed_date = candidate_slots[0].appointment_date
        proposed_time = candidate_slots[0].start_time_local
    proposed_duration = (
        final_output.get("duration_minutes")
        if family in {"move", "resize"}
        else None
    )
    warning_codes = set(final_output.get("warning_codes", []))
    if adapter_review is not None:
        warning_codes.update(adapter_review.warning_codes)

    return ReceptionOneProductContextProposalOut(
        result=result,
        safe=result in {"proposal_ready", "clarification_required"},
        summary=summary,
        request_id=frame["request_id"],
        correlation_id=frame["correlation_id"],
        context_revision=frame["context_revision"],
        patient_handle=patient_handle,
        patient_display=displays.get(patient_handle),
        practitioner_handle=practitioner_handle,
        practitioner_display=displays.get(practitioner_handle),
        goal=normalized_plan.get("goal"),
        operation_id=final_output.get("api_spine_operation_id"),
        candidate_slots=candidate_slots,
        selected_appointment=selected_out,
        proposed_appointment_date=proposed_date,
        proposed_start_time_local=proposed_time,
        proposed_duration_minutes=proposed_duration,
        adapter_review=adapter_review,
        warning_codes=sorted(warning_codes),
        review=ReceptionOneProductContextReviewOut(
            disposition=disposition,
            plan_hash=review.get("normalized_plan_sha256"),
            operator_ids=review.get("admitted_operator_ids", []),
            safe_repairs=review.get("safe_repairs", []),
            violation_paths=[
                item["path"] for item in review.get("violations", [])
            ],
            context_revision=frame["context_revision"],
        ),
        planner_mode=planner_mode,
        provider_calls=provider_calls,
        runtime_audit_ref=runtime_audit_ref,
        database_reads_performed=True,
    )


def proofread_provider_blocked_plan(
    *,
    frame: dict[str, Any],
    now: datetime,
    plan: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    from scripts import reception_one_bureau_typed_plan_protocol as typed_plan

    typed_plan.validate_schema(frame, "input")
    if plan is not None:
        candidate = plan
    else:
        try:
            candidate = typed_plan.deterministic_plan(frame)
        except ValueError:
            extraction = typed_plan.extraction_for(frame)
            bounded_goal = typed_plan.ACTION_GOALS.get(
                extraction.intended_action or "",
                "clarification",
            )
            candidate = typed_plan.base_plan(
                frame,
                planner_class="deterministic_semantic_adapter",
                goal=bounded_goal,
            )
            candidate["steps"] = [
                {
                    "id": "step-clarification",
                    "operator": "request_clarification",
                    "args": {},
                }
            ]
        # The typed slot operator raises on an empty authoritative read.
        # For an exact move with no matching slot, use the existing reviewed
        # clarification step rather than executing a candidate-free move.
        extraction = typed_plan.extraction_for(frame)
        if (
            plan is None
            and extraction.intended_action == "move"
            and extraction.temporal_relation == "exact"
            and not frame["context"]["candidate_slots"]
        ):
            candidate = typed_plan.base_plan(
                frame,
                planner_class="deterministic_semantic_adapter",
                goal="move",
            )
            candidate["steps"] = [
                {
                    "id": "step-clarification",
                    "operator": "request_clarification",
                    "args": {},
                }
            ]
    review, normalized_plan = typed_plan.proofread_plan(
        frame,
        candidate,
        now=now,
    )
    execution = None
    if review["disposition"] == "admit":
        execution = typed_plan.execute_plan(frame, normalized_plan, review)
    return review, normalized_plan, execution


def compose_provider_blocked_proposal(
    *,
    frame: dict[str, Any],
    displays: dict[str, str],
    now: datetime,
    plan: dict[str, Any] | None = None,
    adapter_review: ReceptionOneProductContextAdapterReviewOut | None = None,
) -> ReceptionOneProductContextProposalOut:
    review, normalized_plan, execution = proofread_provider_blocked_plan(
        frame=frame,
        now=now,
        plan=plan,
    )
    return build_reviewed_proposal_result(
        frame=frame,
        displays=displays,
        normalized_plan=normalized_plan,
        review=review,
        execution=execution,
        adapter_review=adapter_review,
    )
