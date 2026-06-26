"""Deterministic, non-mutating normalizer for Bernie slot-search commands.

Pure function contract:
  - No DB session, no network, no LLM, no asyncio.
  - No appointment or audit mutation.
  - Idempotent: same input always produces same output.

Pipeline position:
  LLM parses NL → SlotSearchCommandIn (loose) → normalize_slot_search_command()
  → SlotSearchCommandResult (safe=True + constraint) → POST /proposals/slot-search
  → confirm → create appointment.

This module owns ONLY the normalization step.
"""

from __future__ import annotations

import uuid
from datetime import date, time, timedelta
from typing import Optional

from app.schemas.appointments import (
    AppointmentProposalIssue,
    SlotSearchCommandIn,
    SlotSearchCommandResult,
    SlotSearchProposalIn,
)


def _issue(code: str, severity: str, message: str) -> AppointmentProposalIssue:
    return AppointmentProposalIssue(code=code, severity=severity, message=message)


def _parse_uuid(
    raw: object,
    field: str,
    blocks: list[AppointmentProposalIssue],
) -> Optional[uuid.UUID]:
    if raw is None:
        return None
    if isinstance(raw, uuid.UUID):
        return raw
    try:
        return uuid.UUID(str(raw).strip())
    except (ValueError, AttributeError):
        blocks.append(_issue(
            f"invalid_{field}", "blocked",
            f"{field} is not a valid UUID: {raw!r}",
        ))
        return None


def _parse_date(
    raw: object,
    field: str,
    blocks: list[AppointmentProposalIssue],
    reference_date: Optional[date] = None,
) -> Optional[date]:
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    s = str(raw).strip().lower()
    if s in ("today", "tomorrow"):
        if reference_date is None:
            blocks.append(_issue(
                "relative_date_no_reference", "blocked",
                f"{field} uses relative token '{s}' but no reference_date was supplied.",
            ))
            return None
        return reference_date if s == "today" else reference_date + timedelta(days=1)
    try:
        return date.fromisoformat(s)
    except (ValueError, AttributeError):
        blocks.append(_issue(
            f"invalid_{field}", "blocked",
            f"{field} is not a valid ISO date (YYYY-MM-DD): {raw!r}",
        ))
        return None


def _parse_time(
    raw: object,
    field: str,
    blocks: list[AppointmentProposalIssue],
) -> Optional[time]:
    if raw is None:
        return None
    if isinstance(raw, time):
        return raw
    try:
        return time.fromisoformat(str(raw).strip())
    except (ValueError, AttributeError):
        blocks.append(_issue(
            f"invalid_{field}", "blocked",
            f"{field} is not a valid time (HH:MM or HH:MM:SS): {raw!r}",
        ))
        return None


def _coerce_int(
    raw: object,
    field: str,
    blocks: list[AppointmentProposalIssue],
) -> Optional[int]:
    """Parse raw to int without range validation. Rejects booleans."""
    if raw is None:
        return None
    if isinstance(raw, bool):
        blocks.append(_issue(
            f"invalid_{field}", "blocked",
            f"{field} must be an integer, not a boolean.",
        ))
        return None
    if isinstance(raw, int):
        return raw
    try:
        return int(str(raw).strip())
    except (ValueError, AttributeError):
        blocks.append(_issue(
            f"invalid_{field}", "blocked",
            f"{field} is not a valid integer: {raw!r}",
        ))
        return None


def normalize_slot_search_command(
    payload: SlotSearchCommandIn,
    *,
    reference_date: Optional[date] = None,
) -> SlotSearchCommandResult:
    """Normalize a permissive Bernie slot-search command into a typed SlotSearchProposalIn.

    Args:
        payload: Permissive command dict (strings, UUIDs, dates, times, ints — any mix).
        reference_date: Required only when payload contains relative date tokens
            ('today', 'tomorrow'). Injected by the caller so the function stays pure.

    Returns:
        SlotSearchCommandResult with safe=True and a populated constraint on success,
        or safe=False with typed block issues on failure. No side effects.
    """
    warnings: list[AppointmentProposalIssue] = []
    blocks: list[AppointmentProposalIssue] = []

    # ── Identifier fields (UUID/format parsing only; no DB resolution) ────────
    practitioner_id = _parse_uuid(payload.practitioner_id, "practitioner_id", blocks)
    appointment_type_id = _parse_uuid(payload.appointment_type_id, "appointment_type_id", blocks)
    location_id = _parse_uuid(payload.location_id, "location_id", blocks)
    patient_id = _parse_uuid(payload.patient_id, "patient_id", blocks)

    # ── Date fields ───────────────────────────────────────────────────────────
    date_from = _parse_date(payload.date_from, "date_from", blocks, reference_date)
    date_to = _parse_date(payload.date_to, "date_to", blocks, reference_date)

    # Default date_to to date_from when not explicitly supplied by the caller
    if date_to is None and payload.date_to is None and date_from is not None:
        date_to = date_from

    # ── Time fields ───────────────────────────────────────────────────────────
    earliest_time = _parse_time(payload.earliest_time, "earliest_time", blocks)
    latest_time = _parse_time(payload.latest_time, "latest_time", blocks)

    # ── duration_minutes ──────────────────────────────────────────────────────
    duration_minutes: Optional[int] = None
    dur_raw = _coerce_int(payload.duration_minutes, "duration_minutes", blocks)
    if dur_raw is not None:
        if dur_raw <= 0:
            blocks.append(_issue(
                "invalid_duration_minutes", "blocked",
                f"duration_minutes must be positive, got {dur_raw}.",
            ))
        else:
            duration_minutes = dur_raw

    # ── limit ─────────────────────────────────────────────────────────────────
    limit = 20  # default matches SlotSearchProposalIn default
    lim_raw = _coerce_int(payload.limit, "limit", blocks)
    if lim_raw is not None:
        if lim_raw <= 0:
            blocks.append(_issue(
                "invalid_limit", "blocked",
                f"limit must be positive, got {lim_raw}.",
            ))
        elif lim_raw > 100:
            warnings.append(_issue(
                "limit_clamped", "warning",
                f"limit {lim_raw} exceeds maximum 100; clamped to 100.",
            ))
            limit = 100
        else:
            limit = lim_raw

    # ── Require mandatory fields ──────────────────────────────────────────────
    if practitioner_id is None and not any(
        b.code == "invalid_practitioner_id" for b in blocks
    ):
        blocks.append(_issue(
            "missing_practitioner_id", "blocked",
            "practitioner_id is required for slot search.",
        ))

    if date_from is None and not any(
        b.code in ("invalid_date_from", "relative_date_no_reference") for b in blocks
    ):
        blocks.append(_issue(
            "missing_date_from", "blocked",
            "date_from is required for slot search.",
        ))

    if blocks:
        return SlotSearchCommandResult(
            safe=False,
            constraint=None,
            warnings=warnings,
            blocks=blocks,
            summary="Slot-search command blocked: " + "; ".join(b.message for b in blocks),
        )

    # ── Construct the validated constraint ────────────────────────────────────
    # SlotSearchProposalIn.validate_date_range enforces date_to >= date_from
    # and the 14-day ceiling; ValueError there becomes a typed block.
    try:
        constraint = SlotSearchProposalIn(
            practitioner_id=practitioner_id,
            date_from=date_from,
            date_to=date_to,
            duration_minutes=duration_minutes,
            appointment_type_id=appointment_type_id,
            location_id=location_id,
            earliest_time=earliest_time,
            latest_time=latest_time,
            patient_id=patient_id,
            limit=limit,
        )
    except ValueError as exc:
        blocks.append(_issue("constraint_validation_error", "blocked", str(exc)))
        return SlotSearchCommandResult(
            safe=False,
            constraint=None,
            warnings=warnings,
            blocks=blocks,
            summary="Slot-search command blocked: " + str(exc),
        )

    # ── Build human-readable summary ──────────────────────────────────────────
    parts = [
        f"practitioner {constraint.practitioner_id}",
        f"from {constraint.date_from}",
    ]
    if constraint.date_to and constraint.date_to != constraint.date_from:
        parts.append(f"to {constraint.date_to}")
    if constraint.duration_minutes:
        parts.append(f"{constraint.duration_minutes} min")
    summary = "Slot search normalized: " + ", ".join(parts) + "."
    if warnings:
        summary += f" ({len(warnings)} warning(s))"

    return SlotSearchCommandResult(
        safe=True,
        constraint=constraint,
        warnings=warnings,
        blocks=[],
        summary=summary,
    )
