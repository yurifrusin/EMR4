"""Read-only provider boundary for Bernie booking-instruction interpretation.

This module intentionally performs no DB access, network calls, LLM calls,
appointment mutations, audit writes, or raw-instruction logging.
"""

from __future__ import annotations

import re
from typing import Protocol

from app.schemas.appointments import (
    AppointmentProposalIssue,
    BernieBookingInstructionInterpretIn,
    BernieBookingInstructionInterpretOut,
    BernieBookingInterpreterMetadata,
    SlotSearchCommandIn,
)
from app.services.bernie_slot_normalizer import normalize_slot_search_command


UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
KEY_VALUE_RE = re.compile(
    r"\b(?P<key>practitioner_id|patient_id|appointment_type_id|location_id|"
    r"date_from|date_to|duration_minutes|duration|earliest_time|latest_time|"
    r"limit)\s*[:=]\s*(?P<value>[^\s,;]+)",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"\b(?:today|tomorrow|\d{4}-\d{2}-\d{2})\b", re.IGNORECASE)
TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b")
UNSAFE_TERMS = ("book it", "create it", "confirm it", "make the booking", "write it")


class BookingInstructionInterpreter(Protocol):
    metadata: BernieBookingInterpreterMetadata

    def interpret(
        self,
        body: BernieBookingInstructionInterpretIn,
    ) -> BernieBookingInstructionInterpretOut:
        ...


def _issue(code: str, severity: str, message: str) -> AppointmentProposalIssue:
    return AppointmentProposalIssue(code=code, severity=severity, message=message)


def _disabled_response() -> BernieBookingInstructionInterpretOut:
    return BernieBookingInstructionInterpretOut(
        safe=False,
        result="blocked",
        autonomy_tier="blocked",
        summary="Booking-instruction interpreter is disabled by default.",
        confidence=0,
        missing_fields=["interpreter_provider"],
        safety_flags=["provider_disabled"],
        clarifying_question=(
            "Enable a reviewed booking-instruction interpreter provider before "
            "using free-text booking interpretation."
        ),
        blocks=[
            _issue(
                "booking_interpreter_disabled",
                "blocked",
                "Booking-instruction interpretation is disabled by default.",
            )
        ],
        provider_metadata=BernieBookingInterpreterMetadata(
            provider="disabled",
            mode="disabled",
            live_provider=False,
        ),
    )


class DisabledBookingInstructionInterpreter:
    metadata = BernieBookingInterpreterMetadata(
        provider="disabled",
        mode="disabled",
        live_provider=False,
    )

    def interpret(
        self,
        body: BernieBookingInstructionInterpretIn,
    ) -> BernieBookingInstructionInterpretOut:
        _ = body
        return _disabled_response()


class FakeBookingInstructionInterpreter:
    metadata = BernieBookingInterpreterMetadata(
        provider="fake",
        mode="mocked",
        live_provider=False,
    )

    def interpret(
        self,
        body: BernieBookingInstructionInterpretIn,
    ) -> BernieBookingInstructionInterpretOut:
        command = _extract_fake_command(body.instruction)
        safety_flags = _safety_flags(body.instruction)
        missing_fields = _missing_fields(command)
        warnings = [
            _issue(
                "autonomous_booking_language",
                "warning",
                "Instruction contains booking/confirmation language; staff confirmation is still required.",
            )
            for flag in safety_flags
            if flag == "autonomous_booking_language"
        ]

        normalization = normalize_slot_search_command(
            command,
            reference_date=body.reference_date,
        )
        blocks = list(normalization.blocks)
        if safety_flags:
            blocks.append(_issue(
                "staff_confirmation_required",
                "blocked",
                "Free-text interpretation is read-only and cannot book or confirm appointments.",
            ))

        if blocks:
            result = "clarification_required" if missing_fields else "blocked"
            return BernieBookingInstructionInterpretOut(
                safe=False,
                result=result,
                autonomy_tier="blocked",
                summary="Booking instruction needs staff clarification before slot search.",
                confidence=0.45 if missing_fields else 0.55,
                command_candidate=command,
                missing_fields=missing_fields,
                safety_flags=safety_flags,
                clarifying_question=_clarifying_question(missing_fields, safety_flags),
                normalization=normalization,
                warnings=[*normalization.warnings, *warnings],
                blocks=blocks,
                provider_metadata=self.metadata,
            )

        return BernieBookingInstructionInterpretOut(
            safe=True,
            result="interpreted",
            autonomy_tier="execute_with_report",
            summary="Booking instruction interpreted into a validated slot-search command candidate.",
            confidence=0.9,
            command_candidate=command,
            missing_fields=[],
            safety_flags=[],
            clarifying_question=None,
            normalization=normalization,
            warnings=normalization.warnings,
            blocks=[],
            provider_metadata=self.metadata,
        )


def _extract_fake_command(instruction: str) -> SlotSearchCommandIn:
    values: dict[str, object] = {}
    for match in KEY_VALUE_RE.finditer(instruction):
        key = match.group("key").lower()
        if key == "duration":
            key = "duration_minutes"
        values[key] = match.group("value").strip()

    if "practitioner_id" not in values:
        practitioner_match = re.search(
            r"\bpractitioner(?:_id)?\s+(?P<uuid>" + UUID_RE.pattern + ")",
            instruction,
            re.IGNORECASE,
        )
        if practitioner_match:
            values["practitioner_id"] = practitioner_match.group("uuid")

    if "date_from" not in values:
        date_match = DATE_RE.search(instruction)
        if date_match:
            values["date_from"] = date_match.group(0).lower()

    times = TIME_RE.findall(instruction)
    if "earliest_time" not in values and times:
        values["earliest_time"] = times[0]
    if "latest_time" not in values and len(times) > 1:
        values["latest_time"] = times[1]

    if "duration_minutes" not in values:
        duration_match = re.search(
            r"\b(?P<minutes>\d{1,3})\s*(?:min|mins|minute|minutes)\b",
            instruction,
            re.IGNORECASE,
        )
        if duration_match:
            values["duration_minutes"] = duration_match.group("minutes")

    return SlotSearchCommandIn(**values)


def _missing_fields(command: SlotSearchCommandIn) -> list[str]:
    missing = []
    if command.practitioner_id is None:
        missing.append("practitioner_id")
    if command.date_from is None:
        missing.append("date_from")
    return missing


def _safety_flags(instruction: str) -> list[str]:
    lowered = instruction.lower()
    if any(term in lowered for term in UNSAFE_TERMS):
        return ["autonomous_booking_language"]
    return []


def _clarifying_question(
    missing_fields: list[str],
    safety_flags: list[str],
) -> str | None:
    if missing_fields:
        readable = ", ".join(missing_fields)
        return f"Please provide {readable} before Bernie searches for slots."
    if safety_flags:
        return "Please confirm this is only a read-only interpretation request."
    return None


def get_booking_instruction_interpreter(
    provider_name: str,
) -> BookingInstructionInterpreter:
    normalized = (provider_name or "disabled").strip().lower()
    if normalized == "fake":
        return FakeBookingInstructionInterpreter()
    return DisabledBookingInstructionInterpreter()
