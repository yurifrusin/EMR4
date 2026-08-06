"""Pure unmounted Rayleen A4 to Practice Context Fabric source adapter.

The adapter consumes an already-authorised serialized waiting-room frame.  It
does not import the product read service, access a database, mount a route, or
perform network/provider work.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    ContractViolation,
    canonical_json,
    canonical_sha256,
    seal,
    verify_seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    DATA_CLASS as CURRENT_DATA_CLASS,
    EVIDENCE_LABEL as CURRENT_EVIDENCE_LABEL,
    SCHEMA_VERSION as CURRENT_WEAVE_SCHEMA_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]
A4_FRAME_SCHEMA_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "model-required-bureau-provider-free-successor-lanes"
    / "waiting-room-context-frame.schema.json"
)
RESULT_SCHEMA_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter"
    / "adapter-result.schema.json"
)

SCHEMA_VERSION = (
    "emr4.practice_context_fabric_rayleen_waiting_room_source_adapter.v1"
)
ALIAS_SCHEMA_VERSION = (
    "emr4.practice_context_fabric_waiting_room_reference_alias_manifest.v1"
)
EVIDENCE_LABEL = (
    "provider_free_authored_synthetic_unmounted_rayleen_waiting_room_source_adapter"
)
SOURCE_CONTRACT_ID = "emr4.waiting_room_context_frame.v1"
FRAME_TYPE = "current_waiting_room_projection"
SOURCE_CLASS = "current_waiting_room"
MAX_SOURCE_TTL_SECONDS = 120
MAX_ENTRIES = 6
MAX_OUTPUT_BYTES = 12000

EXCLUDED_FIELD_CLASSES = [
    "contact_details",
    "national_identifiers",
    "clinical_text",
    "appointment_notes",
    "unrestricted_history",
    "credentials",
    "raw_provider_data",
]

STATUS_CODES = {
    "booked": "BOOKED",
    "confirmed": "CONFIRMED",
    "arrived": "ARRIVED",
    "in_consult": "IN_CONSULT",
}
THRESHOLD_CODES = {
    "under_15_minutes": "UNDER_15_MINUTES",
    "15_to_29_minutes": "15_TO_29_MINUTES",
    "30_minutes_or_more": "30_MINUTES_OR_MORE",
}
FLOW_EXCEPTION_CODES = {
    "missing_arrival_timestamp": "MISSING_ARRIVAL_TIMESTAMP",
    "expected_arrival_overdue": "EXPECTED_ARRIVAL_OVERDUE",
}


class WaitingRoomSourceAdapterViolation(ContractViolation):
    """Raised when the bounded source adapter must release nothing."""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


A4_FRAME_SCHEMA = _load_json(A4_FRAME_SCHEMA_PATH)
ADAPTER_RESULT_SCHEMA = _load_json(RESULT_SCHEMA_PATH)


ALIAS_MANIFEST_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "manifest_id",
        "source_contract_id",
        "source_frame_digest",
        "binding_digest",
        "grant_digest",
        "session_binding_digest",
        "source_practice_id",
        "source_location_id",
        "fabric_practice_ref",
        "fabric_location_ref",
        "appointment_aliases",
        "practitioner_aliases",
        "issued_at",
        "expires_at",
        "maximum_entries",
        "maximum_output_bytes",
        "read_only",
        "command_authority",
        "provider_authority",
        "alias_manifest_digest",
    ],
    "properties": {
        "schema_version": {"const": ALIAS_SCHEMA_VERSION},
        "manifest_id": {
            "type": "string",
            "pattern": r"^synthetic:alias-manifest:[a-z0-9-]+$",
        },
        "source_contract_id": {"const": SOURCE_CONTRACT_ID},
        "source_frame_digest": {
            "type": "string",
            "pattern": r"^sha256:[0-9a-f]{64}$",
        },
        "binding_digest": {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"},
        "grant_digest": {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"},
        "session_binding_digest": {
            "type": "string",
            "pattern": r"^sha256:[0-9a-f]{64}$",
        },
        "source_practice_id": {"type": "string", "format": "uuid"},
        "source_location_id": {"type": "string", "format": "uuid"},
        "fabric_practice_ref": {
            "type": "string",
            "pattern": r"^synthetic:practice:[a-z0-9-]+$",
        },
        "fabric_location_ref": {
            "type": "string",
            "pattern": r"^synthetic:location:[a-z0-9-]+$",
        },
        "appointment_aliases": {
            "type": "array",
            "maxItems": MAX_ENTRIES,
            "items": {"$ref": "#/$defs/appointment_alias"},
        },
        "practitioner_aliases": {
            "type": "array",
            "maxItems": MAX_ENTRIES,
            "items": {"$ref": "#/$defs/practitioner_alias"},
        },
        "issued_at": {"type": "string", "format": "date-time"},
        "expires_at": {"type": "string", "format": "date-time"},
        "maximum_entries": {"type": "integer", "minimum": 0, "maximum": MAX_ENTRIES},
        "maximum_output_bytes": {
            "type": "integer",
            "minimum": 1024,
            "maximum": MAX_OUTPUT_BYTES,
        },
        "read_only": {"const": True},
        "command_authority": {"const": False},
        "provider_authority": {"const": False},
        "alias_manifest_digest": {
            "type": "string",
            "pattern": r"^sha256:[0-9a-f]{64}$",
        },
    },
    "$defs": {
        "appointment_alias": {
            "type": "object",
            "additionalProperties": False,
            "required": ["source_id", "fabric_ref"],
            "properties": {
                "source_id": {"type": "string", "format": "uuid"},
                "fabric_ref": {
                    "type": "string",
                    "pattern": r"^synthetic:appointment:[a-z0-9-]+$",
                },
            },
        },
        "practitioner_alias": {
            "type": "object",
            "additionalProperties": False,
            "required": ["source_id", "fabric_ref"],
            "properties": {
                "source_id": {"type": "string", "format": "uuid"},
                "fabric_ref": {
                    "type": "string",
                    "pattern": r"^synthetic:practitioner:[a-z0-9-]+$",
                },
            },
        },
    },
}


def _instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise WaitingRoomSourceAdapterViolation("invalid_timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise WaitingRoomSourceAdapterViolation("timestamp_requires_timezone")
    return parsed.astimezone(timezone.utc)


def _z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_json_schema(value: dict[str, Any], schema: dict[str, Any], code: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise WaitingRoomSourceAdapterViolation(code)


def _verify(value: dict[str, Any], field: str, code: str) -> None:
    try:
        verify_seal(value, field)
    except ContractViolation as error:
        raise WaitingRoomSourceAdapterViolation(code) from error


def _threshold_band(wait_minutes: int) -> str:
    if wait_minutes < 15:
        return "under_15_minutes"
    if wait_minutes < 30:
        return "15_to_29_minutes"
    return "30_minutes_or_more"


def _threshold_code(wait_minutes: int) -> str:
    return THRESHOLD_CODES[_threshold_band(wait_minutes)]


def validate_waiting_room_source_adapter_result(result: dict[str, Any]) -> None:
    """Validate the complete sealed adapter result at the assembler handoff."""

    _validate_json_schema(
        result,
        ADAPTER_RESULT_SCHEMA,
        "adapter_result_schema_invalid",
    )
    envelope = result["source_envelope"]
    trace = result["adapter_trace"]
    _verify(envelope, "source_digest", "source_envelope_digest_invalid")
    _verify(trace, "adapter_trace_digest", "adapter_trace_digest_invalid")
    _verify(result, "adapter_result_digest", "adapter_result_digest_invalid")

    expected_pairs = (
        (result["source_frame_digest"], trace["source_frame_digest"]),
        (result["alias_manifest_digest"], trace["alias_manifest_digest"]),
        (envelope["source_envelope_id"], trace["source_envelope_id"]),
        (envelope["source_digest"], trace["source_digest"]),
        (envelope["session_binding_digest"], trace["session_binding_digest"]),
        (envelope["expires_at"], trace["expires_at"]),
        (envelope["location_refs"][0], envelope["payload"]["location_ref"]),
    )
    if any(left != right for left, right in expected_pairs):
        raise WaitingRoomSourceAdapterViolation("adapter_result_linkage_invalid")
    if trace["source_entry_count"] != trace["released_entry_count"]:
        raise WaitingRoomSourceAdapterViolation("adapter_result_count_mismatch")
    entries = envelope["payload"]["entries"]
    if trace["released_entry_count"] != len(entries):
        raise WaitingRoomSourceAdapterViolation("adapter_result_count_mismatch")
    if len({entry["appointment_ref"] for entry in entries}) != len(entries):
        raise WaitingRoomSourceAdapterViolation("adapter_result_duplicate_entry")

    observed = _instant(envelope["observed_at"])
    assembled = _instant(trace["assembled_at"])
    expires = _instant(envelope["expires_at"])
    if not observed <= assembled < expires:
        raise WaitingRoomSourceAdapterViolation("adapter_result_time_invalid")
    if (expires - observed).total_seconds() > MAX_SOURCE_TTL_SECONDS:
        raise WaitingRoomSourceAdapterViolation("adapter_result_ttl_invalid")

    for entry in entries:
        elapsed = entry.get("elapsed_wait_minutes")
        threshold = entry.get("threshold_code")
        rank = entry.get("longest_wait_rank")
        exception = entry.get("flow_exception_code")
        if (elapsed is None) != (threshold is None):
            raise WaitingRoomSourceAdapterViolation("adapter_result_wait_pair_invalid")
        if elapsed is not None and threshold != _threshold_code(elapsed):
            raise WaitingRoomSourceAdapterViolation("adapter_result_threshold_invalid")
        if rank is not None and elapsed is None:
            raise WaitingRoomSourceAdapterViolation("adapter_result_rank_invalid")
        if exception is not None and any(
            value is not None for value in (elapsed, threshold, rank)
        ):
            raise WaitingRoomSourceAdapterViolation("adapter_result_exception_invalid")


def extract_waiting_room_source_envelope(result: dict[str, Any]) -> dict[str, Any]:
    """Return only a revalidated immutable-copy handoff to the parent assembler."""

    validate_waiting_room_source_adapter_result(result)
    return deepcopy(result["source_envelope"])


def _expected_signal_values(frame: dict[str, Any]) -> list[dict[str, Any]]:
    observed = _instant(frame["generated_at"])
    elapsed: list[tuple[int, str]] = []
    expected: list[dict[str, Any]] = []
    for fact in frame["backend_facts"]:
        appointment_id = fact["appointment_id"]
        status = fact["status"]
        scheduled = _instant(fact["scheduled_at"])
        arrived_raw = fact["arrived_at"]
        if status in {"arrived", "in_consult"}:
            if arrived_raw is None:
                expected.append(
                    {
                        "kind": "flow_exception",
                        "appointment_id": appointment_id,
                        "value": "missing_arrival_timestamp",
                    }
                )
                continue
            arrived = _instant(arrived_raw)
            if arrived > observed:
                raise WaitingRoomSourceAdapterViolation("arrival_observed_in_future")
            wait_minutes = max(0, int((observed - arrived).total_seconds() // 60))
            elapsed.append((wait_minutes, appointment_id))
            expected.extend(
                [
                    {
                        "kind": "elapsed_wait_minutes",
                        "appointment_id": appointment_id,
                        "value": wait_minutes,
                    },
                    {
                        "kind": "threshold_band",
                        "appointment_id": appointment_id,
                        "value": _threshold_band(wait_minutes),
                    },
                ]
            )
        elif scheduled < observed:
            expected.append(
                {
                    "kind": "flow_exception",
                    "appointment_id": appointment_id,
                    "value": "expected_arrival_overdue",
                }
            )
    for rank, (_, appointment_id) in enumerate(
        sorted(elapsed, key=lambda item: (-item[0], item[1])), start=1
    ):
        expected.append(
            {
                "kind": "longest_wait_rank",
                "appointment_id": appointment_id,
                "value": rank,
            }
        )
    return expected


def _signal_key(value: dict[str, Any]) -> tuple[str, str]:
    return value["appointment_id"], value["kind"]


def _validate_source_frame(frame: dict[str, Any], *, assembled_at: str) -> str:
    _validate_json_schema(frame, A4_FRAME_SCHEMA, "source_schema_invalid")
    if frame["excluded_field_classes"] != EXCLUDED_FIELD_CLASSES:
        raise WaitingRoomSourceAdapterViolation("source_excluded_fields_invalid")
    observed = _instant(frame["generated_at"])
    expires = _instant(frame["expires_at"])
    now = _instant(assembled_at)
    lifetime = (expires - observed).total_seconds()
    if lifetime <= 0 or lifetime > MAX_SOURCE_TTL_SECONDS:
        raise WaitingRoomSourceAdapterViolation("source_ttl_invalid")
    if observed > now or now >= expires:
        raise WaitingRoomSourceAdapterViolation("source_not_current")
    if len(frame["backend_facts"]) > MAX_ENTRIES:
        raise WaitingRoomSourceAdapterViolation("source_entry_limit_exceeded")

    facts_by_id: dict[str, dict[str, Any]] = {}
    for fact in frame["backend_facts"]:
        appointment_id = fact["appointment_id"]
        if appointment_id in facts_by_id:
            raise WaitingRoomSourceAdapterViolation("duplicate_source_fact")
        facts_by_id[appointment_id] = fact
        label = fact["label"]
        if (
            label["observed_at"] != frame["generated_at"]
            or label["expires_at"] != frame["expires_at"]
            or label["freshness_state"] != "fresh"
            or label["authority_ceiling"] != "data_only"
        ):
            raise WaitingRoomSourceAdapterViolation("source_fact_label_mismatch")

    normalized_actual: list[dict[str, Any]] = []
    seen_signal_keys: set[tuple[str, str]] = set()
    for signal in frame["derived_signals"]:
        appointment_id = signal["appointment_id"]
        if appointment_id not in facts_by_id:
            raise WaitingRoomSourceAdapterViolation("orphan_source_signal")
        key = _signal_key(signal)
        if key in seen_signal_keys:
            raise WaitingRoomSourceAdapterViolation("duplicate_source_signal")
        seen_signal_keys.add(key)
        label = signal["label"]
        if (
            label != facts_by_id[appointment_id]["label"]
            or label["observed_at"] != frame["generated_at"]
            or label["expires_at"] != frame["expires_at"]
        ):
            raise WaitingRoomSourceAdapterViolation("source_signal_label_mismatch")
        normalized_actual.append(
            {
                "kind": signal["kind"],
                "appointment_id": appointment_id,
                "value": signal["value"],
            }
        )
    expected = _expected_signal_values(frame)
    actual_rows = sorted(canonical_json(item) for item in normalized_actual)
    expected_rows = sorted(canonical_json(item) for item in expected)
    if actual_rows != expected_rows:
        raise WaitingRoomSourceAdapterViolation("source_signal_not_grounded")
    return canonical_sha256(frame)


def _validate_authority(
    authority_binding: dict[str, Any],
    scope_grant: dict[str, Any],
    *,
    assembled_at: str,
) -> None:
    _verify(authority_binding, "binding_digest", "binding_digest_invalid")
    _verify(scope_grant, "grant_digest", "grant_digest_invalid")
    if scope_grant["binding_digest"] != authority_binding["binding_digest"]:
        raise WaitingRoomSourceAdapterViolation("grant_binding_mismatch")
    if (
        scope_grant["session_binding_digest"]
        != authority_binding["session_binding_digest"]
    ):
        raise WaitingRoomSourceAdapterViolation("grant_session_mismatch")
    if "RECEPTIONIST" not in authority_binding["roles"]:
        raise WaitingRoomSourceAdapterViolation("reader_role_not_admitted")
    if "RAYLEEN" not in authority_binding["allowed_bureaus"]:
        raise WaitingRoomSourceAdapterViolation("rayleen_not_admitted")
    if "CURRENT_OPERATIONAL_AWARENESS" not in authority_binding["allowed_purposes"]:
        raise WaitingRoomSourceAdapterViolation("purpose_not_admitted")
    if (
        scope_grant["decision"] != "ADMIT"
        or scope_grant["requesting_bureau"] != "RAYLEEN"
        or scope_grant["purpose_code"] != "CURRENT_OPERATIONAL_AWARENESS"
    ):
        raise WaitingRoomSourceAdapterViolation("source_scope_not_admitted")
    if (
        FRAME_TYPE not in scope_grant["allowed_frame_types"]
        or SOURCE_CLASS not in scope_grant["allowed_source_classes"]
    ):
        raise WaitingRoomSourceAdapterViolation("source_triple_not_admitted")
    if (
        scope_grant["read_only"] is not True
        or scope_grant["command_authority"] is not False
        or scope_grant["provider_authority"] is not False
    ):
        raise WaitingRoomSourceAdapterViolation("adapter_authority_invalid")
    now = _instant(assembled_at)
    if not (
        _instant(authority_binding["issued_at"])
        <= now
        < _instant(authority_binding["expires_at"])
        and _instant(scope_grant["issued_at"])
        <= now
        < _instant(scope_grant["expires_at"])
    ):
        raise WaitingRoomSourceAdapterViolation("adapter_authority_not_current")


def _alias_map(rows: list[dict[str, str]], kind: str) -> dict[str, str]:
    sources = [row["source_id"] for row in rows]
    aliases = [row["fabric_ref"] for row in rows]
    if len(sources) != len(set(sources)) or len(aliases) != len(set(aliases)):
        raise WaitingRoomSourceAdapterViolation("duplicate_reference")
    if sources != sorted(sources):
        raise WaitingRoomSourceAdapterViolation(f"{kind}_aliases_not_canonical")
    for row in rows:
        if row["source_id"].casefold() in row["fabric_ref"].casefold():
            raise WaitingRoomSourceAdapterViolation("raw_identifier_alias")
    return {row["source_id"]: row["fabric_ref"] for row in rows}


def _validate_alias_manifest(
    alias_manifest: dict[str, Any],
    frame: dict[str, Any],
    authority_binding: dict[str, Any],
    scope_grant: dict[str, Any],
    *,
    source_frame_digest: str,
    assembled_at: str,
) -> tuple[dict[str, str], dict[str, str]]:
    _validate_json_schema(
        alias_manifest, ALIAS_MANIFEST_SCHEMA, "alias_manifest_schema_invalid"
    )
    _verify(
        alias_manifest,
        "alias_manifest_digest",
        "alias_manifest_digest_invalid",
    )
    expected = {
        "source_frame_digest": source_frame_digest,
        "binding_digest": authority_binding["binding_digest"],
        "grant_digest": scope_grant["grant_digest"],
        "session_binding_digest": scope_grant["session_binding_digest"],
        "source_practice_id": frame["practice_id"],
        "source_location_id": frame["location_id"],
        "fabric_practice_ref": authority_binding["practice_id"],
    }
    for key, value in expected.items():
        if alias_manifest[key] != value:
            raise WaitingRoomSourceAdapterViolation("alias_scope_mismatch")
    allowed_locations = scope_grant["allowed_location_refs"]
    if allowed_locations != [alias_manifest["fabric_location_ref"]]:
        raise WaitingRoomSourceAdapterViolation("alias_location_not_admitted")
    now = _instant(assembled_at)
    if not _instant(alias_manifest["issued_at"]) <= now < _instant(
        alias_manifest["expires_at"]
    ):
        raise WaitingRoomSourceAdapterViolation("alias_manifest_not_current")
    if alias_manifest["maximum_entries"] > scope_grant["maximum_items_per_frame"]:
        raise WaitingRoomSourceAdapterViolation("alias_entry_limit_exceeded")
    if alias_manifest["maximum_output_bytes"] > scope_grant["maximum_total_bytes"]:
        raise WaitingRoomSourceAdapterViolation("alias_byte_limit_exceeded")

    appointment_map = _alias_map(alias_manifest["appointment_aliases"], "appointment")
    practitioner_map = _alias_map(
        alias_manifest["practitioner_aliases"], "practitioner"
    )
    expected_appointments = {item["appointment_id"] for item in frame["backend_facts"]}
    expected_practitioners = {item["practitioner_id"] for item in frame["backend_facts"]}
    if set(appointment_map) != expected_appointments or set(practitioner_map) != expected_practitioners:
        raise WaitingRoomSourceAdapterViolation("alias_manifest_not_complete")
    if len(expected_appointments) > alias_manifest["maximum_entries"]:
        raise WaitingRoomSourceAdapterViolation("source_entry_limit_exceeded")
    return appointment_map, practitioner_map


def _build_entries(
    frame: dict[str, Any],
    appointment_map: dict[str, str],
    practitioner_map: dict[str, str],
    allowed_fields: set[str],
) -> list[dict[str, Any]]:
    signals: dict[str, dict[str, Any]] = {}
    for signal in frame["derived_signals"]:
        signals.setdefault(signal["appointment_id"], {})[signal["kind"]] = signal[
            "value"
        ]
    entries: list[dict[str, Any]] = []
    for fact in frame["backend_facts"]:
        entry: dict[str, Any] = {
            "appointment_ref": appointment_map[fact["appointment_id"]],
        }
        if "waiting_practitioner_ref" in allowed_fields:
            entry["practitioner_ref"] = practitioner_map[fact["practitioner_id"]]
        if "waiting_status" in allowed_fields:
            entry["status"] = STATUS_CODES[fact["status"]]
        values = signals.get(fact["appointment_id"], {})
        if (
            "waiting_elapsed_minutes" in allowed_fields
            and "elapsed_wait_minutes" in values
        ):
            entry["elapsed_wait_minutes"] = values["elapsed_wait_minutes"]
        if "waiting_threshold_code" in allowed_fields and "threshold_band" in values:
            entry["threshold_code"] = THRESHOLD_CODES[values["threshold_band"]]
        if "flow_exception" in values:
            entry["flow_exception_code"] = FLOW_EXCEPTION_CODES[
                values["flow_exception"]
            ]
        if (
            "waiting_elapsed_minutes" in allowed_fields
            and "longest_wait_rank" in values
        ):
            entry["longest_wait_rank"] = values["longest_wait_rank"]
        entries.append(entry)
    return entries


def adapt_waiting_room_source(
    frame: dict[str, Any],
    authority_binding: dict[str, Any],
    scope_grant: dict[str, Any],
    alias_manifest: dict[str, Any],
    *,
    assembled_at: str,
) -> dict[str, Any]:
    """Return one sealed Current source or raise without partial release."""

    _validate_authority(authority_binding, scope_grant, assembled_at=assembled_at)
    source_frame_digest = _validate_source_frame(frame, assembled_at=assembled_at)
    appointment_map, practitioner_map = _validate_alias_manifest(
        alias_manifest,
        frame,
        authority_binding,
        scope_grant,
        source_frame_digest=source_frame_digest,
        assembled_at=assembled_at,
    )
    expires_at = _z(
        min(
            _instant(frame["expires_at"]),
            _instant(authority_binding["expires_at"]),
            _instant(scope_grant["expires_at"]),
            _instant(alias_manifest["expires_at"]),
        )
    )
    entries = _build_entries(
        frame,
        appointment_map,
        practitioner_map,
        set(scope_grant["allowed_fields"]),
    )
    envelope_base = {
        "schema_version": CURRENT_WEAVE_SCHEMA_VERSION,
        "source_envelope_id": (
            "synthetic:source:waiting-adapter-" + source_frame_digest[-12:]
        ),
        "frame_type": FRAME_TYPE,
        "source_class": SOURCE_CLASS,
        "source_contract_id": SOURCE_CONTRACT_ID,
        "source_revision": (
            f"synthetic:waiting-revision:{frame['context_revision']}:"
            f"{source_frame_digest[-12:]}"
        ),
        "practice_id": authority_binding["practice_id"],
        "session_binding_digest": scope_grant["session_binding_digest"],
        "location_refs": [alias_manifest["fabric_location_ref"]],
        "observed_at": frame["generated_at"],
        "expires_at": expires_at,
        "evidence_label": CURRENT_EVIDENCE_LABEL,
        "data_class": CURRENT_DATA_CLASS,
        "read_only": True,
        "command_authority": False,
        "provider_authority": False,
        "supersession_state": "CURRENT",
        "payload": {
            "location_ref": alias_manifest["fabric_location_ref"],
            "context_revision": frame["context_revision"],
            "entries": entries,
        },
    }
    source_envelope = seal(envelope_base, "source_digest")
    trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "source_frame_digest": source_frame_digest,
            "alias_manifest_digest": alias_manifest["alias_manifest_digest"],
            "binding_digest": authority_binding["binding_digest"],
            "grant_digest": scope_grant["grant_digest"],
            "session_binding_digest": scope_grant["session_binding_digest"],
            "source_envelope_id": source_envelope["source_envelope_id"],
            "source_digest": source_envelope["source_digest"],
            "source_entry_count": len(frame["backend_facts"]),
            "released_entry_count": len(entries),
            "omitted_field_codes": [
                "PATIENT_DISPLAY_TOKEN_OMITTED",
                "RAW_SOURCE_IDENTIFIERS_OMITTED",
                "SOURCE_TIMESTAMPS_MINIMIZED",
                "EXCLUDED_FIELD_CLASSES_OMITTED",
            ],
            "assembled_at": assembled_at,
            "expires_at": expires_at,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
            "release_decision": "RELEASE",
        },
        "adapter_trace_digest",
    )
    result = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "evidence_label": EVIDENCE_LABEL,
            "data_class": CURRENT_DATA_CLASS,
            "source_frame_digest": source_frame_digest,
            "alias_manifest_digest": alias_manifest["alias_manifest_digest"],
            "source_envelope": source_envelope,
            "adapter_trace": trace,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
            "release_decision": "RELEASE",
        },
        "adapter_result_digest",
    )
    validate_waiting_room_source_adapter_result(result)
    forbidden_values = {
        frame["practice_id"],
        frame["location_id"],
        frame["frame_id"],
        *(item["appointment_id"] for item in frame["backend_facts"]),
        *(item["practitioner_id"] for item in frame["backend_facts"]),
        *(item["patient_display_token"] for item in frame["backend_facts"]),
        *(
            item["waiting_area_id"]
            for item in frame["backend_facts"]
            if item["waiting_area_id"] is not None
        ),
        *(item["scheduled_at"] for item in frame["backend_facts"]),
        *(
            item["arrived_at"]
            for item in frame["backend_facts"]
            if item["arrived_at"] is not None
        ),
        *(source_id for item in frame["backend_facts"] for source_id in item["label"]["source_ids"]),
    }
    released_text = canonical_json(result).casefold()
    if any(str(value).casefold() in released_text for value in forbidden_values):
        raise WaitingRoomSourceAdapterViolation("raw_identifier_leak")
    if len(canonical_json(result).encode("utf-8")) > alias_manifest[
        "maximum_output_bytes"
    ]:
        raise WaitingRoomSourceAdapterViolation("adapter_output_byte_limit_exceeded")
    return result


def build_authored_synthetic_waiting_room_frame() -> dict[str, Any]:
    label = {
        "source_ids": ["authored_synthetic_fixture:waiting-room-adapter-001"],
        "integrity_principals": ["backend_truth"],
        "confidentiality_readers": ["authorized_reception_surface"],
        "observed_at": "2026-08-06T02:59:30Z",
        "expires_at": "2026-08-06T03:01:30Z",
        "freshness_state": "fresh",
        "authority_ceiling": "data_only",
    }
    appointment_id = "11000000-0000-4000-8000-000000000004"
    practitioner_id = "11000000-0000-4000-8000-000000000005"
    return {
        "schema_version": SOURCE_CONTRACT_ID,
        "frame_id": "11000000-0000-4000-8000-000000000001",
        "practice_id": "11000000-0000-4000-8000-000000000002",
        "location_id": "11000000-0000-4000-8000-000000000003",
        "context_revision": 7,
        "generated_at": "2026-08-06T02:59:30Z",
        "expires_at": "2026-08-06T03:01:30Z",
        "reader": "authorized_reception_surface",
        "backend_facts": [
            {
                "appointment_id": appointment_id,
                "patient_display_token": "synthetic:patient-a08e75075c67",
                "practitioner_id": practitioner_id,
                "status": "arrived",
                "scheduled_at": "2026-08-06T02:45:00Z",
                "waiting_area_id": "11000000-0000-4000-8000-000000000006",
                "arrived_at": "2026-08-06T02:49:30Z",
                "label": deepcopy(label),
            }
        ],
        "derived_signals": [
            {
                "kind": "elapsed_wait_minutes",
                "appointment_id": appointment_id,
                "value": 10,
                "derived_by": "deterministic_projection_engine",
                "label": deepcopy(label),
            },
            {
                "kind": "threshold_band",
                "appointment_id": appointment_id,
                "value": "under_15_minutes",
                "derived_by": "deterministic_projection_engine",
                "label": deepcopy(label),
            },
            {
                "kind": "longest_wait_rank",
                "appointment_id": appointment_id,
                "value": 1,
                "derived_by": "deterministic_projection_engine",
                "label": deepcopy(label),
            },
        ],
        "excluded_field_classes": list(EXCLUDED_FIELD_CLASSES),
    }


def build_authored_synthetic_alias_manifest(
    frame: dict[str, Any],
    authority_binding: dict[str, Any],
    scope_grant: dict[str, Any],
) -> dict[str, Any]:
    appointments = sorted(
        {
            item["appointment_id"]: "synthetic:appointment:one"
            for item in frame["backend_facts"]
        }.items()
    )
    practitioners = sorted(
        {
            item["practitioner_id"]: "synthetic:practitioner:one"
            for item in frame["backend_facts"]
        }.items()
    )
    return seal(
        {
            "schema_version": ALIAS_SCHEMA_VERSION,
            "manifest_id": "synthetic:alias-manifest:rayleen-waiting-001",
            "source_contract_id": SOURCE_CONTRACT_ID,
            "source_frame_digest": canonical_sha256(frame),
            "binding_digest": authority_binding["binding_digest"],
            "grant_digest": scope_grant["grant_digest"],
            "session_binding_digest": scope_grant["session_binding_digest"],
            "source_practice_id": frame["practice_id"],
            "source_location_id": frame["location_id"],
            "fabric_practice_ref": authority_binding["practice_id"],
            "fabric_location_ref": scope_grant["allowed_location_refs"][0],
            "appointment_aliases": [
                {"source_id": source_id, "fabric_ref": fabric_ref}
                for source_id, fabric_ref in appointments
            ],
            "practitioner_aliases": [
                {"source_id": source_id, "fabric_ref": fabric_ref}
                for source_id, fabric_ref in practitioners
            ],
            "issued_at": "2026-08-06T02:59:45Z",
            "expires_at": "2026-08-06T03:01:30Z",
            "maximum_entries": 6,
            "maximum_output_bytes": MAX_OUTPUT_BYTES,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "alias_manifest_digest",
    )


__all__ = [
    "ADAPTER_RESULT_SCHEMA",
    "ALIAS_MANIFEST_SCHEMA",
    "ALIAS_SCHEMA_VERSION",
    "EVIDENCE_LABEL",
    "MAX_ENTRIES",
    "MAX_OUTPUT_BYTES",
    "SCHEMA_VERSION",
    "SOURCE_CONTRACT_ID",
    "WaitingRoomSourceAdapterViolation",
    "adapt_waiting_room_source",
    "build_authored_synthetic_alias_manifest",
    "build_authored_synthetic_waiting_room_frame",
    "extract_waiting_room_source_envelope",
    "validate_waiting_room_source_adapter_result",
]
