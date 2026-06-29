"""Read-only provider boundary for Bernie booking-instruction interpretation.

This module intentionally performs no DB access, appointment mutations, audit
writes, or raw-instruction logging. The live provider path can call an injected
AI provider only when explicitly configured; disabled/fake paths remain local.
"""

from __future__ import annotations

import re
import asyncio
from typing import Any, Callable, Protocol

from pydantic import ValidationError

from app.config import settings
from app.schemas.appointments import (
    AppointmentProposalIssue,
    BernieBookingInstructionInterpretIn,
    BernieBookingInstructionInterpretOut,
    BernieBookingInterpreterMetadata,
    SlotSearchCommandIn,
)
from app.models.tenancy import User
from app.services.ai.access_service import AccessAiRequest, AccessAiService
from app.services.ai.audit_events import AiAuditSourceSurface
from app.services.ai.contracts import AiCapability, AiMethod, AiProvider
from app.services.ai.entitlements import AiAccessRole, AiActorContext, actor_context_from_user
from app.services.ai.service import _get_default_provider
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

LiveProviderFactory = Callable[[], AiProvider]
_live_provider_factory: LiveProviderFactory | None = None


class BookingInstructionInterpreter(Protocol):
    metadata: BernieBookingInterpreterMetadata

    def interpret(
        self,
        body: BernieBookingInstructionInterpretIn,
        actor_context: AiActorContext | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        pass


def _issue(code: str, severity: str, message: str) -> AppointmentProposalIssue:
    return AppointmentProposalIssue(code=code, severity=severity, message=message)


def set_live_provider_factory(factory: LiveProviderFactory | None) -> None:
    """Inject a live-provider factory for tests without touching cloud clients."""
    global _live_provider_factory
    _live_provider_factory = factory


def actor_context_for_interpreter_user(user: User) -> AiActorContext:
    return actor_context_from_user(
        user,
        extra_roles=(AiAccessRole.RECEPTION_USER,),
        environment=settings.environment.lower(),
    )


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
        actor_context: AiActorContext | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        _ = body, actor_context
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
        actor_context: AiActorContext | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        _ = actor_context
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


class GeminiVertexBookingInstructionInterpreter:
    metadata = BernieBookingInterpreterMetadata(
        provider="gemini_vertex",
        mode="live",
        live_provider=True,
    )

    def __init__(self, provider_factory: LiveProviderFactory | None = None) -> None:
        self._provider_factory = provider_factory

    def interpret(
        self,
        body: BernieBookingInstructionInterpretIn,
        actor_context: AiActorContext | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        try:
            raw = self._generate(body, actor_context)
        except Exception:
            return _live_blocked_response(
                "booking_interpreter_provider_unavailable",
                "Live booking-instruction interpreter provider is unavailable.",
            )

        if not isinstance(raw, dict):
            return _live_blocked_response(
                "booking_interpreter_invalid_response",
                "Live booking-instruction interpreter returned an invalid response.",
            )

        command, command_error = _command_from_live_response(raw)
        if command_error:
            return _live_blocked_response(
                "booking_interpreter_invalid_command",
                "Live booking-instruction interpreter returned an invalid command candidate.",
            )

        safety_flags = _dedupe_strings([
            *_coerce_string_list(raw.get("safety_flags")),
            *_safety_flags(body.instruction),
        ])
        missing_fields = _dedupe_strings([
            *_coerce_string_list(raw.get("missing_fields")),
            *_missing_fields(command),
        ])
        confidence = _coerce_confidence(raw.get("confidence"))
        summary = _safe_summary(raw.get("summary"), body.instruction)
        clarifying_question = _safe_optional_string(raw.get("clarifying_question"))
        normalization = normalize_slot_search_command(
            command,
            reference_date=body.reference_date,
        )
        warnings = [
            _issue(
                "autonomous_booking_language",
                "warning",
                "Instruction contains booking/confirmation language; staff confirmation is still required.",
            )
            for flag in safety_flags
            if flag == "autonomous_booking_language"
        ]
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
                summary=summary or "Booking instruction needs staff clarification before slot search.",
                confidence=min(confidence, 0.65),
                command_candidate=command,
                missing_fields=missing_fields,
                safety_flags=safety_flags,
                clarifying_question=(
                    clarifying_question
                    or _clarifying_question(missing_fields, safety_flags)
                ),
                normalization=normalization,
                warnings=[*normalization.warnings, *warnings],
                blocks=blocks,
                provider_metadata=self.metadata,
            )

        return BernieBookingInstructionInterpretOut(
            safe=True,
            result="interpreted",
            autonomy_tier="execute_with_report",
            summary=summary or "Booking instruction interpreted into a validated slot-search command candidate.",
            confidence=confidence,
            command_candidate=command,
            missing_fields=[],
            safety_flags=[],
            clarifying_question=None,
            normalization=normalization,
            warnings=normalization.warnings,
            blocks=[],
            provider_metadata=self.metadata,
        )

    def _generate(
        self,
        body: BernieBookingInstructionInterpretIn,
        actor_context: AiActorContext | None,
    ) -> dict:
        provider_factory = self._provider_factory or _live_provider_factory
        provider = provider_factory() if provider_factory is not None else None
        if provider is None:
            provider = _get_default_provider()
        access_ai = AccessAiService(provider)
        result = _run_access_ai_invocation(
            access_ai.invoke(
                AccessAiRequest(
                    actor=actor_context or _fallback_interpreter_actor_context(),
                    capability=AiCapability.BERNIE_BOOKING_INTERPRET,
                    method=AiMethod.INVOKE,
                    contents=_build_live_provider_prompt(body),
                    source_surface=AiAuditSourceSurface.DIARY,
                    temperature=settings.bernie_booking_interpreter_live_temperature,
                    metadata={"interpreter": "bernie_booking_instruction"},
                )
            )
        )
        if not result.allowed or result.raw is None:
            raise RuntimeError(result.denial_reason or "access_ai_interpreter_blocked")
        return result.raw


def _live_blocked_response(code: str, message: str) -> BernieBookingInstructionInterpretOut:
    return BernieBookingInstructionInterpretOut(
        safe=False,
        result="blocked",
        autonomy_tier="blocked",
        summary="Live booking-instruction interpretation failed closed.",
        confidence=0,
        missing_fields=[],
        safety_flags=["provider_response_unusable"],
        clarifying_question="Please use structured booking fields or the deterministic interpreter path.",
        blocks=[_issue(code, "blocked", message)],
        provider_metadata=GeminiVertexBookingInstructionInterpreter.metadata,
    )


def _fallback_interpreter_actor_context() -> AiActorContext:
    return AiActorContext(
        user_id=None,
        practice_id=None,
        roles=("ai.reception_user",),
        environment=settings.environment.lower(),
    )


def _run_access_ai_invocation(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError("bernie_interpreter_requires_sync_context")


def _build_live_provider_prompt(
    body: BernieBookingInstructionInterpretIn,
) -> str:
    reference_date = body.reference_date.isoformat() if body.reference_date else "not provided"
    return (
        "You are Bernie, EMR4's read-only booking-instruction interpreter. "
        "Return only JSON. Do not book, confirm, create appointments, search slots, "
        "write audit rows, or claim that an appointment has been made. "
        "Extract only structured slot-search command fields from the staff instruction. "
        "If the instruction asks you to book/confirm/create/write, include "
        "autonomous_booking_language in safety_flags. Do not include raw patient notes "
        "or repeat the full instruction in summary. "
        "JSON shape: {"
        "\"command_candidate\":{\"practitioner_id\":null,\"patient_id\":null,"
        "\"appointment_type_id\":null,\"location_id\":null,\"date_from\":null,"
        "\"date_to\":null,\"duration_minutes\":null,\"earliest_time\":null,"
        "\"latest_time\":null,\"limit\":null},"
        "\"confidence\":0.0,"
        "\"summary\":\"brief non-PHI structured interpretation summary\","
        "\"missing_fields\":[],"
        "\"safety_flags\":[],"
        "\"clarifying_question\":null"
        "}. "
        f"Reference date: {reference_date}. "
        f"Instruction: {body.instruction}"
    )


def _command_from_live_response(
    raw: dict[str, Any],
) -> tuple[SlotSearchCommandIn, bool]:
    candidate = raw.get("command_candidate", raw.get("command", {}))
    if not isinstance(candidate, dict):
        return SlotSearchCommandIn(), True
    try:
        return SlotSearchCommandIn.model_validate(candidate), False
    except ValidationError:
        return SlotSearchCommandIn(), True


def _coerce_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _dedupe_strings(values: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _coerce_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.5
    return max(0, min(confidence, 1))


def _safe_summary(value: Any, raw_instruction: str | None = None) -> str:
    if not isinstance(value, str):
        return ""
    cleaned = value.strip()
    if not cleaned:
        return ""
    instruction = (raw_instruction or "").strip()
    if instruction and instruction.lower() in cleaned.lower():
        return ""
    cleaned = re.sub(
        r"\b(patient_id|practitioner_id|appointment_type_id|location_id):"
        + UUID_RE.pattern,
        r"\1:[redacted]",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = UUID_RE.sub("[redacted-id]", cleaned)
    return cleaned[:200]


def _safe_optional_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned[:200] if cleaned else None


def get_booking_instruction_interpreter(
    provider_name: str,
) -> BookingInstructionInterpreter:
    normalized = (provider_name or "disabled").strip().lower()
    if normalized == "fake":
        return FakeBookingInstructionInterpreter()
    if normalized in {"gemini_vertex", "vertex_gemini", "gemini", "vertex"}:
        return GeminiVertexBookingInstructionInterpreter()
    return DisabledBookingInstructionInterpreter()
