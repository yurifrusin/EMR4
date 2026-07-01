"""Read-only provider boundary for Bernie booking-instruction interpretation.

This module intentionally performs no DB access, appointment mutations, audit
writes, or raw-instruction logging. The live provider path can call an injected
AI provider only when explicitly configured; disabled/fake paths remain local.
"""

from __future__ import annotations

import os
import re
import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from pydantic import ValidationError

from app.config import settings
from app.schemas.appointments import (
    AppointmentProposalIssue,
    BernieBookingInstructionInterpretIn,
    BernieBookingInstructionInterpretOut,
    BernieBookingInterpreterMetadata,
    BernieConfidenceAxis,
    BernieDecisionPolicy,
    SlotSearchCommandIn,
)
from app.models.tenancy import User
from app.services.ai.access_service import AccessAiRequest, AccessAiService
from app.services.ai.audit_events import AccessAiAuditEvent, AiAuditSourceSurface
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

# Natural language time phrase patterns (no DB, no network).
# Business-hours assumption: bare hour 1–11 without am/pm → pm.
_NAT_TIME_PAT = r"(?:1?[0-9]|2[0-3])(?:[.:][0-5]\d)?(?:\s*(?:am|pm))?"
_BETWEEN_TIME_RE = re.compile(
    r"\bbetween\s+(" + _NAT_TIME_PAT + r")\s+and\s+(" + _NAT_TIME_PAT + r")\b",
    re.IGNORECASE,
)
_AFTER_TIME_RE = re.compile(r"\bafter\s+(" + _NAT_TIME_PAT + r")\b", re.IGNORECASE)
_BEFORE_TIME_RE = re.compile(r"\bbefore\s+(" + _NAT_TIME_PAT + r")\b", re.IGNORECASE)
_TIME_FRAGMENT_RE = re.compile(
    r"^(1?[0-9]|2[0-3])(?:[.:]([0-5]\d))?(?:\s*(am|pm))?$",
    re.IGNORECASE,
)

LiveProviderFactory = Callable[[], AiProvider]
_live_provider_factory: LiveProviderFactory | None = None


def _parse_time_fragment(raw: str) -> str | None:
    """Convert a natural time fragment (e.g. '3', '3:45', '3.45', '3 pm') to HH:MM.

    Business-hours assumption: bare hours 1–11 without am/pm are treated as pm.
    Returns None when the fragment cannot be parsed.
    """
    m = _TIME_FRAGMENT_RE.match(raw.strip())
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    meridiem = (m.group(3) or "").lower()
    if meridiem == "pm" and hour < 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0
    elif not meridiem and 1 <= hour <= 11:
        hour += 12
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def _extract_natural_time_constraints(
    instruction: str,
) -> tuple[str | None, str | None]:
    """Extract earliest/latest times from receptionist phrases.

    Handles: 'after 3', 'after 3 pm', 'before 3:45', 'before 3.45',
    'between 2 pm and 3:45'.  Returns (earliest_time, latest_time) as HH:MM
    strings or None when not found.  Pure function — no DB, no network.
    """
    earliest: str | None = None
    latest: str | None = None

    between_m = _BETWEEN_TIME_RE.search(instruction)
    if between_m:
        earliest = _parse_time_fragment(between_m.group(1))
        latest = _parse_time_fragment(between_m.group(2))
        return earliest, latest

    after_m = _AFTER_TIME_RE.search(instruction)
    if after_m:
        earliest = _parse_time_fragment(after_m.group(1))

    before_m = _BEFORE_TIME_RE.search(instruction)
    if before_m:
        latest = _parse_time_fragment(before_m.group(1))

    return earliest, latest


@dataclass
class InterpreterReadinessStatus:
    """Readiness report for release gating and health monitoring.

    Truthy when requests will be served without hard failure (live or via
    deterministic fallback). live_provider_ok reflects import/construction
    availability only — GCP credential validity is only verifiable at
    runtime so a warning is emitted when no credential source is detected.
    """
    provider: str
    ready: bool
    live_provider_ok: bool
    fallback_active: bool
    mode: str  # "live" | "deterministic_fallback" | "deterministic_only" | "disabled"
    warning: str | None = field(default=None)

    def __bool__(self) -> bool:
        return self.ready


def _check_live_provider_import() -> tuple[bool, str | None]:
    """Try importing and constructing the live Gemini provider without network calls."""
    try:
        from app.services.ai.providers.gemini import GeminiProvider  # noqa: F401
        GeminiProvider()
        return True, None
    except Exception as exc:
        return False, f"provider_import_failed: {str(exc)[:200]}"


def _gcp_credential_warning() -> str | None:
    """Return a warning string when no GCP credential source is detectable."""
    if (
        settings.google_application_credentials
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("CLOUDSDK_CORE_PROJECT")
    ):
        return None
    return (
        "No GCP credential source detected (GOOGLE_APPLICATION_CREDENTIALS not set); "
        "live calls will fail at runtime unless ADC is configured via another mechanism."
    )


def interpreter_is_ready(
    provider_name: str,
    *,
    fallback_override: bool | None = None,
) -> InterpreterReadinessStatus:
    """Return a readiness status suitable for release gating and health checks.

    Does not make network calls. live_provider_ok is True when the provider
    SDK can be imported and constructed locally; GCP credential validity is
    only verifiable at runtime (a warning is emitted when no credential source
    is detected). ready is True when requests will be served without hard
    failure — either via live provider or deterministic fallback.
    """
    normalized = (provider_name or "disabled").strip().lower()
    fallback = (
        fallback_override
        if fallback_override is not None
        else settings.bernie_booking_interpreter_fallback_to_deterministic
    )

    if normalized in ("disabled", ""):
        return InterpreterReadinessStatus(
            provider="disabled",
            ready=False,
            live_provider_ok=False,
            fallback_active=False,
            mode="disabled",
        )

    if normalized == "fake":
        return InterpreterReadinessStatus(
            provider="fake",
            ready=True,
            live_provider_ok=True,
            fallback_active=False,
            mode="deterministic_only",
        )

    if normalized in {"gemini_vertex", "vertex_gemini", "gemini", "vertex"}:
        live_ok, import_warning = _check_live_provider_import()
        if live_ok:
            mode = "live"
            warning = _gcp_credential_warning()
        else:
            mode = "deterministic_fallback" if fallback else "disabled"
            warning = import_warning
        return InterpreterReadinessStatus(
            provider="gemini_vertex",
            ready=live_ok or fallback,
            live_provider_ok=live_ok,
            fallback_active=fallback,
            mode=mode,
            warning=warning,
        )

    # Unknown provider name — report misconfiguration.
    return InterpreterReadinessStatus(
        provider=normalized,
        ready=fallback,
        live_provider_ok=False,
        fallback_active=fallback,
        mode="deterministic_fallback" if fallback else "disabled",
        warning=(
            f"Unknown interpreter provider {normalized!r}; "
            f"{'deterministic fallback is active' if fallback else 'no fallback configured'}."
        ),
    )


class BookingInstructionInterpreter(Protocol):
    metadata: BernieBookingInterpreterMetadata

    def interpret(
        self,
        body: BernieBookingInstructionInterpretIn,
        actor_context: AiActorContext | None = None,
        audit_events: list[AccessAiAuditEvent] | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        pass


def _issue(code: str, severity: str, message: str) -> AppointmentProposalIssue:
    return AppointmentProposalIssue(code=code, severity=severity, message=message)


def _speech_transcription_placeholder_axis() -> BernieConfidenceAxis:
    """Reserved axis — non-gating placeholder until voice/transcription input is wired."""
    return BernieConfidenceAxis(
        axis="speech_transcription",
        band="assume",
        basis="No transcription input — axis reserved for future voice integration.",
    )


def _all_block_axes(reason: str) -> list[BernieConfidenceAxis]:
    """All axes set to block — used by the disabled path."""
    return [
        BernieConfidenceAxis(axis=a, band="block", basis=reason)
        for a in (
            "intent", "temporal", "practitioner",
            "patient_identity", "slot_validity", "speech_transcription",
        )
    ]


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
    block_reason = "Booking-instruction interpreter is disabled."
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
        confidence_axes=_all_block_axes(block_reason),
        decision=BernieDecisionPolicy(
            overall_band="block",
            rationale=block_reason,
            requires_staff_confirmation=True,
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
        audit_events: list[AccessAiAuditEvent] | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        _ = body, actor_context, audit_events
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
        audit_events: list[AccessAiAuditEvent] | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        _ = actor_context, audit_events
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

        speech_axis = _speech_transcription_placeholder_axis()
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
                confidence_axes=[speech_axis],
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
            confidence_axes=[speech_axis],
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

    # Natural time phrases take precedence over positional HH:MM scanning so
    # that 'after 3' and 'before 3:45' produce correct earlier/later semantics.
    if "earliest_time" not in values or "latest_time" not in values:
        nat_earliest, nat_latest = _extract_natural_time_constraints(instruction)
        if "earliest_time" not in values and nat_earliest:
            values["earliest_time"] = nat_earliest
        if "latest_time" not in values and nat_latest:
            values["latest_time"] = nat_latest

    # HH:MM positional fallback for any still-missing time fields.
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
        audit_events: list[AccessAiAuditEvent] | None = None,
    ) -> BernieBookingInstructionInterpretOut:
        try:
            raw = self._generate(body, actor_context, audit_events)
        except Exception:
            if settings.bernie_booking_interpreter_fallback_to_deterministic:
                result = FakeBookingInstructionInterpreter().interpret(
                    body, actor_context, audit_events
                )
                return result.model_copy(update={
                    "provider_metadata": BernieBookingInterpreterMetadata(
                        provider="gemini_vertex",
                        mode="deterministic_fallback",
                        live_provider=False,
                    )
                })
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

        speech_axis = _speech_transcription_placeholder_axis()
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
                confidence_axes=[speech_axis],
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
            confidence_axes=[speech_axis],
        )

    def _generate(
        self,
        body: BernieBookingInstructionInterpretIn,
        actor_context: AiActorContext | None,
        audit_events: list[AccessAiAuditEvent] | None,
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
        if audit_events is not None:
            audit_events.extend(result.audit_events)
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
        "autonomous_booking_language in safety_flags. That language is a warning "
        "for staff confirmation, not a reason to block a supervised proposal. "
        "Do not include raw patient notes or repeat the full instruction in summary. "
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
