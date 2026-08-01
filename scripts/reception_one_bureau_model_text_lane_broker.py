#!/usr/bin/env python3
"""Purpose-built one-use Vertex broker for the Reception One model text lane."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import hmac
import json
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5 as preprinted
from scripts import reception_one_proofreader_dialogue_v4 as dialogue
from scripts import reception_one_receptionist_first_v6 as receptionist_v6
from scripts import reception_one_receptionist_first_v61 as receptionist_v61
from scripts import reception_one_receptionist_first_v62 as receptionist_v62
from scripts import reception_one_receptionist_first_v63 as receptionist_v63
from scripts import reception_one_receptionist_first_v64 as receptionist_v64
from scripts import reception_one_receptionist_first_v65 as receptionist_v65
from scripts import reception_one_receptionist_first_v66 as receptionist_v66
from scripts import reception_one_receptionist_first_v67 as receptionist_v67
from scripts import reception_one_receptionist_first_v68 as receptionist_v68
from scripts import (
    reception_one_receptionist_first_v68_runtime as receptionist_v68_runtime,
)
from scripts import reception_one_shared_typed_plan_language as shared
from scripts import reception_one_structured_source_plan_language as structured


ZERO_HASH = "sha256:" + "0" * 64
PROJECT = "bernie-emr4-dev"
SERVICE_ACCOUNT = (
    "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
)
SCOPE = "https://www.googleapis.com/auth/cloud-platform"
MODEL = "gemini-2.5-flash"
LOCATION = "australia-southeast1"
HOSTNAME = "australia-southeast1-aiplatform.googleapis.com"
PATH = (
    "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
    "publishers/google/models/gemini-2.5-flash:generateContent"
)
POLICY_ID = "reception-one-bureau-model-text-vertex-sydney-v1"
SHARED_POLICY_ID = "reception-one-shared-typed-plan-vertex-sydney-v1"
STRUCTURED_POLICY_ID = (
    "reception-one-structured-source-plan-vertex-sydney-v1"
)
DIALOGUE_POLICY_ID = dialogue.POLICY_ID
PREPRINTED_POLICY_ID = preprinted.POLICY_ID
RECEPTIONIST_V6_POLICY_ID = receptionist_v6.POLICY_ID
RECEPTIONIST_V61_POLICY_ID = receptionist_v61.POLICY_ID
RECEPTIONIST_V62_POLICY_ID = receptionist_v62.POLICY_ID
RECEPTIONIST_V63_POLICY_ID = receptionist_v63.POLICY_ID
RECEPTIONIST_V64_POLICY_ID = receptionist_v64.POLICY_ID
RECEPTIONIST_V65_POLICY_ID = receptionist_v65.POLICY_ID
RECEPTIONIST_V66_POLICY_ID = receptionist_v66.POLICY_ID
RECEPTIONIST_V67_POLICY_ID = receptionist_v67.POLICY_ID
RECEPTIONIST_V68_POLICY_ID = receptionist_v68.POLICY_ID
RECEPTIONIST_V68_RUNTIME_POLICY_ID = receptionist_v68_runtime.POLICY_ID
MAX_CELL_REQUEST_BYTES = 32768
MAX_PROVIDER_REQUEST_BYTES = 65536
MAX_PROVIDER_RESPONSE_BYTES = 65536
MAX_PROVIDER_ERROR_BYTES = 65536
ALLOWLISTED_FINISH_REASONS = frozenset(
    {
        "STOP",
        "MAX_TOKENS",
        "SAFETY",
        "RECITATION",
        "OTHER",
        "BLOCKLIST",
        "PROHIBITED_CONTENT",
        "SPII",
        "MALFORMED_FUNCTION_CALL",
        "MODEL_ARMOR",
    }
)
HISTORICAL_ATTEMPT_ID = "reception-one-model-text-occupied-001"
HISTORICAL_LEDGER_ID = "reception-one-model-text-ledger-001"
RETRY_ATTEMPT_PATTERN = re.compile(
    r"reception-one-model-text-occupied-retry-(?P<sequence>[0-9]{3})"
)
RETRY_LEDGER_PATTERN = re.compile(
    r"reception-one-model-text-ledger-retry-(?P<sequence>[0-9]{3})"
)
PRODUCT_CONTEXT_ATTEMPT_PATTERN = re.compile(
    r"reception-one-product-context-occupied-(?P<sequence>[0-9]{3})"
)
PRODUCT_CONTEXT_LEDGER_PATTERN = re.compile(
    r"reception-one-product-context-ledger-(?P<sequence>[0-9]{3})"
)
EXTENDED_RUNTIME_ATTEMPT_PATTERN = re.compile(
    r"reception-one-extended-runtime-occupied-(?P<sequence>[0-9]{3})"
)
EXTENDED_RUNTIME_LEDGER_PATTERN = re.compile(
    r"reception-one-extended-runtime-ledger-(?P<sequence>[0-9]{3})"
)
SHARED_TYPED_ATTEMPT_PATTERN = re.compile(
    r"reception-one-shared-typed-occupied-(?P<sequence>[0-9]{3})"
)
SHARED_TYPED_LEDGER_PATTERN = re.compile(
    r"reception-one-shared-typed-ledger-(?P<sequence>[0-9]{3})"
)
STRUCTURED_SOURCE_ATTEMPT_PATTERN = re.compile(
    r"reception-one-structured-source-occupied-(?P<sequence>[0-9]{3})"
)
STRUCTURED_SOURCE_LEDGER_PATTERN = re.compile(
    r"reception-one-structured-source-ledger-(?P<sequence>[0-9]{3})"
)
DIALOGUE_ATTEMPT_PATTERN = re.compile(
    r"reception-one-proofreader-dialogue-v4-"
    r"(?P<kind>turn|request-repair)-(?P<sequence>00[12])"
)
DIALOGUE_LEDGER_PATTERN = re.compile(
    r"reception-one-proofreader-dialogue-v4-"
    r"(?P<kind>ledger|request-repair-ledger)-(?P<sequence>00[12])"
)
PREPRINTED_ATTEMPT_PATTERN = re.compile(
    r"reception-one-preprinted-form-v5-"
    r"(?P<kind>turn|request-repair)-(?P<sequence>00[12])"
)
PREPRINTED_LEDGER_PATTERN = re.compile(
    r"reception-one-preprinted-form-v5-"
    r"(?P<kind>ledger|request-repair-ledger)-(?P<sequence>00[12])"
)
PREPRINTED_MULTICASE_ATTEMPT_PATTERN = re.compile(
    r"reception-one-preprinted-form-v5-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
PREPRINTED_MULTICASE_LEDGER_PATTERN = re.compile(
    r"reception-one-preprinted-form-v5-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V6_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v6-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V6_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v6-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V61_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v61-repair-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V61_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v61-repair-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V62_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v62-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V62_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v62-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V63_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v63-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V63_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v63-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V64_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v64-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V64_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v64-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V65_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v65-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V65_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v65-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V66_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v66-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V66_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v66-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V67_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v67-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V67_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v67-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)
RECEPTIONIST_V68_ATTEMPT_PATTERN = re.compile(
    r"reception-one-receptionist-first-v68-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-turn-(?P<sequence>00[12])"
)
RECEPTIONIST_V68_LEDGER_PATTERN = re.compile(
    r"reception-one-receptionist-first-v68-eval-"
    r"(?P<case>[a-z][a-z0-9-]{1,31})-ledger-(?P<sequence>00[12])"
)


class BrokerError(RuntimeError):
    """A bounded one-use broker rejection."""


def validate_attempt_ledger_pair(attempt_id: Any, ledger_id: Any) -> None:
    """Accept the sealed first attempt or an exactly paired retry identifier."""

    if (
        attempt_id == HISTORICAL_ATTEMPT_ID
        and ledger_id == HISTORICAL_LEDGER_ID
    ):
        return
    if not isinstance(attempt_id, str) or not isinstance(ledger_id, str):
        raise BrokerError("cell_request_binding_invalid")
    pattern_pairs = (
        (RETRY_ATTEMPT_PATTERN, RETRY_LEDGER_PATTERN),
        (PRODUCT_CONTEXT_ATTEMPT_PATTERN, PRODUCT_CONTEXT_LEDGER_PATTERN),
        (EXTENDED_RUNTIME_ATTEMPT_PATTERN, EXTENDED_RUNTIME_LEDGER_PATTERN),
        (SHARED_TYPED_ATTEMPT_PATTERN, SHARED_TYPED_LEDGER_PATTERN),
        (
            STRUCTURED_SOURCE_ATTEMPT_PATTERN,
            STRUCTURED_SOURCE_LEDGER_PATTERN,
        ),
        (DIALOGUE_ATTEMPT_PATTERN, DIALOGUE_LEDGER_PATTERN),
        (PREPRINTED_ATTEMPT_PATTERN, PREPRINTED_LEDGER_PATTERN),
        (
            PREPRINTED_MULTICASE_ATTEMPT_PATTERN,
            PREPRINTED_MULTICASE_LEDGER_PATTERN,
        ),
        (RECEPTIONIST_V6_ATTEMPT_PATTERN, RECEPTIONIST_V6_LEDGER_PATTERN),
        (RECEPTIONIST_V61_ATTEMPT_PATTERN, RECEPTIONIST_V61_LEDGER_PATTERN),
        (RECEPTIONIST_V62_ATTEMPT_PATTERN, RECEPTIONIST_V62_LEDGER_PATTERN),
        (RECEPTIONIST_V63_ATTEMPT_PATTERN, RECEPTIONIST_V63_LEDGER_PATTERN),
        (RECEPTIONIST_V64_ATTEMPT_PATTERN, RECEPTIONIST_V64_LEDGER_PATTERN),
        (RECEPTIONIST_V65_ATTEMPT_PATTERN, RECEPTIONIST_V65_LEDGER_PATTERN),
        (RECEPTIONIST_V66_ATTEMPT_PATTERN, RECEPTIONIST_V66_LEDGER_PATTERN),
        (RECEPTIONIST_V67_ATTEMPT_PATTERN, RECEPTIONIST_V67_LEDGER_PATTERN),
        (RECEPTIONIST_V68_ATTEMPT_PATTERN, RECEPTIONIST_V68_LEDGER_PATTERN),
    )
    for attempt_pattern, ledger_pattern in pattern_pairs:
        attempt_match = attempt_pattern.fullmatch(attempt_id)
        ledger_match = ledger_pattern.fullmatch(ledger_id)
        if (
            attempt_match is not None
            and ledger_match is not None
            and attempt_match.group("sequence")
            == ledger_match.group("sequence")
            and attempt_match.group("sequence") != "000"
            and (
                attempt_pattern
                not in {
                    PREPRINTED_MULTICASE_ATTEMPT_PATTERN,
                    RECEPTIONIST_V6_ATTEMPT_PATTERN,
                    RECEPTIONIST_V61_ATTEMPT_PATTERN,
                    RECEPTIONIST_V62_ATTEMPT_PATTERN,
                    RECEPTIONIST_V63_ATTEMPT_PATTERN,
                    RECEPTIONIST_V64_ATTEMPT_PATTERN,
                    RECEPTIONIST_V65_ATTEMPT_PATTERN,
                    RECEPTIONIST_V66_ATTEMPT_PATTERN,
                    RECEPTIONIST_V67_ATTEMPT_PATTERN,
                    RECEPTIONIST_V68_ATTEMPT_PATTERN,
                }
                or attempt_match.group("case") == ledger_match.group("case")
            )
        ):
            if attempt_pattern in {
                DIALOGUE_ATTEMPT_PATTERN,
                PREPRINTED_ATTEMPT_PATTERN,
            }:
                attempt_kind = attempt_match.group("kind")
                ledger_kind = ledger_match.group("kind")
                kinds_match = (
                    attempt_kind == "turn" and ledger_kind == "ledger"
                ) or (
                    attempt_kind == "request-repair"
                    and ledger_kind == "request-repair-ledger"
                )
                if (
                    not kinds_match
                    or (
                        attempt_kind == "request-repair"
                        and attempt_match.group("sequence") != "002"
                    )
                ):
                    continue
            return
    raise BrokerError("cell_request_binding_invalid")


def canonical_bytes(value: Any) -> bytes:
    return lane.canonical_json(value).encode("utf-8")


def bounded_provider_response_metadata(
    packet: dict[str, Any],
) -> dict[str, Any]:
    """Retain allowlisted counts and enums without retaining response text."""

    raw_candidates = packet.get("candidates")
    candidates = raw_candidates if isinstance(raw_candidates, list) else []
    finish_reasons: list[str] = []
    part_counts: list[int] = []
    for candidate in candidates[:4]:
        if not isinstance(candidate, dict):
            finish_reasons.append("UNRECOGNIZED")
            part_counts.append(0)
            continue
        raw_reason = candidate.get("finishReason")
        finish_reasons.append(
            raw_reason
            if raw_reason in ALLOWLISTED_FINISH_REASONS
            else "UNRECOGNIZED"
        )
        content = candidate.get("content")
        parts = content.get("parts") if isinstance(content, dict) else None
        part_counts.append(len(parts) if isinstance(parts, list) else 0)
    usage: dict[str, int] = {}
    raw_usage = packet.get("usageMetadata")
    if isinstance(raw_usage, dict):
        for name in (
            "promptTokenCount",
            "candidatesTokenCount",
            "thoughtsTokenCount",
            "totalTokenCount",
        ):
            value = raw_usage.get(name)
            if type(value) is int and value >= 0:
                usage[name] = value
    return {
        "candidate_count": min(len(candidates), 4),
        "candidate_count_truncated": len(candidates) > 4,
        "finish_reasons": finish_reasons,
        "part_counts": part_counts,
        "usage": usage,
        "provider_text_retained": False,
        "provider_text_inspected_for_diagnosis": False,
    }


def event_hash(event_without_hash: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_bytes(event_without_hash)
    ).hexdigest()


def audit_event(
    sequence: int,
    previous_hash: str,
    event_type: str,
    fields: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "schema_version": "reception.one.bureau.model_text_audit_event.v1",
        "sequence": sequence,
        "previous_hash": previous_hash,
        "event_type": event_type,
        "fields": fields,
    }
    return {**event, "event_hash": event_hash(event)}


def load_object(path: Path) -> dict[str, Any]:
    return lane.load_object(path)


def _safe_error(raw: bytes, status: int) -> dict[str, Any]:
    raw_hash = "sha256:" + hashlib.sha256(raw).hexdigest()
    code = None
    normalized = None
    message = "provider_error_message_withheld"
    field_paths: list[str] = []
    try:
        value = json.loads(raw[:MAX_PROVIDER_ERROR_BYTES])
    except json.JSONDecodeError:
        value = None
    error = value.get("error") if isinstance(value, dict) else None
    if isinstance(error, dict):
        code_value = error.get("code")
        status_value = error.get("status")
        if type(code_value) is int:
            code = code_value
        if isinstance(status_value, str) and re.fullmatch(r"[A-Z_]{1,64}", status_value):
            normalized = status_value
        details = error.get("details")
        if isinstance(details, list):
            for detail in details[:10]:
                violations = (
                    detail.get("fieldViolations")
                    if isinstance(detail, dict)
                    else None
                )
                if not isinstance(violations, list):
                    continue
                for violation in violations[:10]:
                    field = violation.get("field") if isinstance(violation, dict) else None
                    if isinstance(field, str) and re.fullmatch(
                        r"[A-Za-z0-9_.\[\]-]{1,160}", field
                    ):
                        field_paths.append(field)
        candidate_message = error.get("message")
        if isinstance(candidate_message, str):
            encoded = candidate_message.encode("utf-8")
            lowered = candidate_message.casefold()
            forbidden = (
                "bearer ",
                "access_token",
                "authorization",
                "margaret thompson",
                "dr shera",
                "squeeze",
            )
            if (
                len(encoded) <= 2048
                and not any(fragment in lowered for fragment in forbidden)
            ):
                message = candidate_message
    return {
        "http_status": status,
        "provider_error_code": code,
        "normalized_status": normalized,
        "field_violation_paths": sorted(set(field_paths)),
        "sanitized_message": message,
        "discarded_raw_error_hash": raw_hash,
    }


class BrokerState:
    def __init__(self, args: argparse.Namespace) -> None:
        self.token = Path(args.token_file).read_text(encoding="utf-8").strip()
        self.ledger_path = Path(args.ledger)
        self.audit_path = Path(args.audit)
        self.expected_request = load_object(Path(args.request))
        self.frame = load_object(Path(args.frame))
        self.profile = load_object(Path(args.profile))
        self.events: list[dict[str, Any]] = []
        self.served = False
        self.shared_mode = False
        self.structured_mode = False
        self.dialogue_mode = False
        self.preprinted_mode = False
        self.receptionist_v6_mode = False
        self.receptionist_v61_mode = False
        self.receptionist_v62_mode = False
        self.receptionist_v63_mode = False
        self.receptionist_v64_mode = False
        self.receptionist_v65_mode = False
        self.receptionist_v66_mode = False
        self.receptionist_v67_mode = False
        self.receptionist_v68_mode = False
        self.receptionist_v68_runtime_mode = False
        if len(self.token) < 32:
            raise BrokerError("broker_token_invalid")
        self._validate_exact_boundary()

    def _validate_exact_boundary(self) -> None:
        expected_profile = {
            "provider": "google_cloud_vertex_ai",
            "model": MODEL,
            "project": PROJECT,
            "service_account": SERVICE_ACCOUNT,
            "authentication": "keyless_impersonated_service_account_adc",
            "location": LOCATION,
            "endpoint_hostname": HOSTNAME,
            "automatic_fallback": False,
            "global_endpoint": False,
            "api_key_authentication": False,
            "provider_tools": False,
            "grounding": False,
            "retrieval": False,
            "explicit_cache": False,
            "cost_ceiling_usd": 1,
            "occupied_call_ceiling": 1,
        }
        for key, expected in expected_profile.items():
            if self.profile.get(key) != expected:
                raise BrokerError("profile_mismatch:" + key)
        expected_keys = {
            "protocol_version",
            "policy_id",
            "attempt_id",
            "ledger_id",
            "model_input",
        }
        if set(self.expected_request) != expected_keys:
            raise BrokerError("cell_request_shape_invalid")
        protocol = self.expected_request["protocol_version"]
        policy = self.expected_request["policy_id"]
        if (
            protocol == "reception.one.bureau.model-text-cell.v1"
            and policy == POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
        elif (
            protocol == "reception.one.bureau.shared-typed-cell.v2"
            and policy == SHARED_POLICY_ID
        ):
            self.shared_mode = True
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
        elif (
            protocol == structured.PROTOCOL_VERSION
            and policy == STRUCTURED_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = True
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
        elif (
            protocol == dialogue.PROTOCOL_VERSION
            and policy == DIALOGUE_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = True
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
        elif (
            protocol == preprinted.PROTOCOL_VERSION
            and policy == PREPRINTED_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = True
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
        elif (
            protocol == receptionist_v6.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V6_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = True
            self.receptionist_v61_mode = False
        elif (
            protocol == receptionist_v61.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V61_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = True
        elif (
            protocol == receptionist_v62.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V62_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = True
        elif (
            protocol == receptionist_v63.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V63_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = False
            self.receptionist_v63_mode = True
        elif (
            protocol == receptionist_v64.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V64_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = False
            self.receptionist_v63_mode = False
            self.receptionist_v64_mode = True
            self.receptionist_v65_mode = False
            self.receptionist_v66_mode = False
            self.receptionist_v67_mode = False
            self.receptionist_v68_mode = False
        elif (
            protocol == receptionist_v65.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V65_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = False
            self.receptionist_v63_mode = False
            self.receptionist_v64_mode = False
            self.receptionist_v65_mode = True
            self.receptionist_v66_mode = False
            self.receptionist_v67_mode = False
            self.receptionist_v68_mode = False
        elif (
            protocol == receptionist_v66.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V66_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = False
            self.receptionist_v63_mode = False
            self.receptionist_v64_mode = False
            self.receptionist_v65_mode = False
            self.receptionist_v66_mode = True
            self.receptionist_v67_mode = False
            self.receptionist_v68_mode = False
        elif (
            protocol == receptionist_v67.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V67_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = False
            self.receptionist_v63_mode = False
            self.receptionist_v64_mode = False
            self.receptionist_v65_mode = False
            self.receptionist_v66_mode = False
            self.receptionist_v67_mode = True
            self.receptionist_v68_mode = False
        elif (
            protocol == receptionist_v68_runtime.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V68_RUNTIME_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = False
            self.receptionist_v63_mode = False
            self.receptionist_v64_mode = False
            self.receptionist_v65_mode = False
            self.receptionist_v66_mode = False
            self.receptionist_v67_mode = False
            self.receptionist_v68_mode = True
            self.receptionist_v68_runtime_mode = True
        elif (
            protocol == receptionist_v68.PROTOCOL_VERSION
            and policy == RECEPTIONIST_V68_POLICY_ID
        ):
            self.shared_mode = False
            self.structured_mode = False
            self.dialogue_mode = False
            self.preprinted_mode = False
            self.receptionist_v6_mode = False
            self.receptionist_v61_mode = False
            self.receptionist_v62_mode = False
            self.receptionist_v63_mode = False
            self.receptionist_v64_mode = False
            self.receptionist_v65_mode = False
            self.receptionist_v66_mode = False
            self.receptionist_v67_mode = False
            self.receptionist_v68_mode = True
            self.receptionist_v68_runtime_mode = False
        else:
            raise BrokerError("cell_request_binding_invalid")
        validate_attempt_ledger_pair(
            self.expected_request["attempt_id"],
            self.expected_request["ledger_id"],
        )
        typed_plan.validate_schema(self.frame, "input")
        receptionist_contract = (
            receptionist_v68_runtime
            if self.receptionist_v68_runtime_mode
            else receptionist_v68
            if self.receptionist_v68_mode
            else receptionist_v67
            if self.receptionist_v67_mode
            else receptionist_v66
            if self.receptionist_v66_mode
            else receptionist_v65
            if self.receptionist_v65_mode
            else receptionist_v64
            if self.receptionist_v64_mode
            else receptionist_v63
            if self.receptionist_v63_mode
            else receptionist_v62
            if self.receptionist_v62_mode
            else
            receptionist_v61
            if self.receptionist_v61_mode
            else receptionist_v6
            if self.receptionist_v6_mode
            else None
        )
        if receptionist_contract is not None:
            receptionist_contract.validate_turn_input(
                self.frame,
                self.expected_request["model_input"],
            )
            correction_ticket = self.expected_request["model_input"][
                "correction_ticket"
            ]
            expected_model_input = receptionist_contract.build_turn_input(
                self.frame,
                correction_ticket=correction_ticket,
            )
            match = (
                RECEPTIONIST_V68_ATTEMPT_PATTERN
                if self.receptionist_v68_mode
                else RECEPTIONIST_V67_ATTEMPT_PATTERN
                if self.receptionist_v67_mode
                else RECEPTIONIST_V66_ATTEMPT_PATTERN
                if self.receptionist_v66_mode
                else RECEPTIONIST_V65_ATTEMPT_PATTERN
                if self.receptionist_v65_mode
                else RECEPTIONIST_V64_ATTEMPT_PATTERN
                if self.receptionist_v64_mode
                else RECEPTIONIST_V63_ATTEMPT_PATTERN
                if self.receptionist_v63_mode
                else RECEPTIONIST_V62_ATTEMPT_PATTERN
                if self.receptionist_v62_mode
                else RECEPTIONIST_V61_ATTEMPT_PATTERN
                if self.receptionist_v61_mode
                else RECEPTIONIST_V6_ATTEMPT_PATTERN
            ).fullmatch(
                self.expected_request["attempt_id"],
            )
            if (
                match is None
                or (
                    int(match.group("sequence"))
                    != self.expected_request["model_input"]["turn_code"]
                    and not (
                        (
                            self.receptionist_v62_mode
                            or self.receptionist_v63_mode
                            or self.receptionist_v64_mode
                            or self.receptionist_v65_mode
                            or self.receptionist_v66_mode
                            or self.receptionist_v67_mode
                            or self.receptionist_v68_mode
                        )
                        and match.group("sequence") == "002"
                        and self.expected_request["model_input"]["turn_code"]
                        == 1
                        and correction_ticket is None
                    )
                )
            ):
                raise BrokerError("receptionist_v6_turn_attempt_mismatch")
        elif self.preprinted_mode:
            preprinted.validate_turn_input(
                self.frame,
                self.expected_request["model_input"],
            )
            correction_ticket = self.expected_request["model_input"][
                "correction_ticket"
            ]
            expected_model_input = preprinted.build_turn_input(
                self.frame,
                correction_ticket=correction_ticket,
            )
            match = PREPRINTED_ATTEMPT_PATTERN.fullmatch(
                self.expected_request["attempt_id"]
            )
            multicase_match = PREPRINTED_MULTICASE_ATTEMPT_PATTERN.fullmatch(
                self.expected_request["attempt_id"]
            )
            if (
                match is None
                and multicase_match is None
            ):
                raise BrokerError("preprinted_turn_attempt_mismatch")
            active_match = match or multicase_match
            if active_match is None:
                raise BrokerError("preprinted_turn_attempt_mismatch")
            if (
                (
                    active_match.groupdict().get("kind") in {None, "turn"}
                    and int(active_match.group("sequence"))
                    != self.expected_request["model_input"]["turn_code"]
                )
                or (
                    active_match.groupdict().get("kind") == "request-repair"
                    and (
                        active_match.group("sequence") != "002"
                        or self.expected_request["model_input"]["turn_code"] != 1
                        or correction_ticket is not None
                    )
                )
            ):
                raise BrokerError("preprinted_turn_attempt_mismatch")
        elif self.dialogue_mode:
            dialogue.validate_turn_input(
                self.frame,
                self.expected_request["model_input"],
            )
            correction_ticket = self.expected_request["model_input"][
                "correction_ticket"
            ]
            expected_model_input = dialogue.build_turn_input(
                self.frame,
                correction_ticket=correction_ticket,
            )
            match = DIALOGUE_ATTEMPT_PATTERN.fullmatch(
                self.expected_request["attempt_id"]
            )
            if (
                match is None
                or (
                    match.group("kind") == "turn"
                    and int(match.group("sequence"))
                    != self.expected_request["model_input"]["turn_code"]
                )
                or (
                    match.group("kind") == "request-repair"
                    and (
                        match.group("sequence") != "002"
                        or self.expected_request["model_input"]["turn_code"]
                        != 1
                        or correction_ticket is not None
                    )
                )
            ):
                raise BrokerError("dialogue_turn_attempt_mismatch")
        elif self.structured_mode:
            structured.validate_exact(
                self.expected_request["model_input"],
                structured.MODEL_INPUT_SCHEMA_PATH,
            )
            expected_model_input = structured.build_model_input(self.frame)
        elif self.shared_mode:
            shared.validate_exact(
                self.expected_request["model_input"],
                shared.MODEL_INPUT_SCHEMA_PATH,
            )
            expected_model_input = shared.build_model_input(
                self.frame,
                proofreader_feedback=self.expected_request[
                    "model_input"
                ].get("proofreader_feedback"),
            )
        else:
            lane.validate_exact(
                self.expected_request["model_input"], lane.INPUT_SCHEMA_PATH
            )
            expected_model_input = lane.build_model_input(self.frame)
        if expected_model_input != self.expected_request["model_input"]:
            raise BrokerError("model_input_frame_mismatch")

    def append_event(self, event_type: str, fields: dict[str, Any]) -> None:
        previous = self.events[-1]["event_hash"] if self.events else ZERO_HASH
        event = audit_event(len(self.events) + 1, previous, event_type, fields)
        self.events.append(event)
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def consume_ledger(self) -> None:
        ledger = load_object(self.ledger_path)
        expected = {
            "schema_version": (
                "reception.one.bureau.model_text_single_use_ledger.v1"
            ),
            "ledger_id": self.expected_request["ledger_id"],
            "attempt_id": self.expected_request["attempt_id"],
            "policy_id": self.expected_request["policy_id"],
            "status": "open",
            "maximum_provider_calls": 1,
            "provider_calls_consumed": 0,
            "fallback_permitted": False,
        }
        if ledger != expected:
            raise BrokerError("ledger_not_exactly_open")
        consumed = dict(ledger)
        consumed["status"] = "consumed"
        consumed["provider_calls_consumed"] = 1
        temporary = self.ledger_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(consumed, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(self.ledger_path)
        self.append_event(
            "ledger_consumed",
            {
                "attempt_id": consumed["attempt_id"],
                "ledger_id": consumed["ledger_id"],
                "provider_calls_reserved": 1,
            },
        )

    def _credentials(self):
        import google.auth
        from google.auth.transport.requests import Request as GoogleRequest

        try:
            credentials, project = google.auth.default(scopes=[SCOPE])
        except Exception:
            raise BrokerError("impersonated_adc_discovery_failed") from None
        target = getattr(credentials, "service_account_email", None)
        module = type(credentials).__module__
        target_scopes = set(getattr(credentials, "_target_scopes", []) or [])
        if (
            not module.endswith("impersonated_credentials")
            or project != PROJECT
            or target != SERVICE_ACCOUNT
            or target_scopes != {SCOPE}
        ):
            raise BrokerError("impersonated_adc_binding_invalid")
        try:
            credentials.refresh(GoogleRequest())
        except Exception:
            raise BrokerError("impersonated_adc_refresh_failed") from None
        if not getattr(credentials, "token", None):
            raise BrokerError("impersonated_adc_refresh_failed")
        return credentials

    def provider_call(
        self, vertex_request: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        credentials = self._credentials()
        url = "https://" + HOSTNAME + PATH
        if not url.startswith(
            "https://australia-southeast1-aiplatform.googleapis.com/v1/"
        ):
            raise BrokerError("provider_url_not_allowlisted")
        body = canonical_bytes(vertex_request)
        if len(body) > MAX_PROVIDER_REQUEST_BYTES:
            raise BrokerError("provider_request_oversized")
        request = Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        started = time.monotonic()
        try:
            with urlopen(request, timeout=45) as response:  # nosec B310
                raw = response.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
                status = int(response.status)
        except HTTPError as error:
            raw_error = error.read(MAX_PROVIDER_ERROR_BYTES + 1)
            bounded = _safe_error(raw_error, error.code)
            self.append_event("provider_call_failed", bounded)
            raise BrokerError("provider_call_failed") from error
        except OSError as error:
            raise BrokerError("provider_transport_failed") from error
        latency_ms = round((time.monotonic() - started) * 1000)
        if len(raw) > MAX_PROVIDER_RESPONSE_BYTES:
            raise BrokerError("provider_response_oversized")
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError as error:
            raise BrokerError("provider_response_not_json") from error
        if not isinstance(packet, dict):
            raise BrokerError("provider_response_not_object")
        return packet, {"http_status": status, "latency_ms": latency_ms}

    def execute(self, packet: dict[str, Any]) -> dict[str, Any]:
        if self.served:
            raise BrokerError("broker_already_used")
        self.served = True
        if packet != self.expected_request:
            raise BrokerError("cell_request_not_exact")
        self.append_event(
            "request_admitted",
            {
                "attempt_id": packet["attempt_id"],
                "ledger_id": packet["ledger_id"],
                "policy_id": packet["policy_id"],
                "cell_request_hash": lane.canonical_hash(packet),
                "model_input_hash": lane.canonical_hash(packet["model_input"]),
            },
        )
        self.consume_ledger()
        receptionist_contract = (
            receptionist_v68_runtime
            if self.receptionist_v68_runtime_mode
            else receptionist_v68
            if self.receptionist_v68_mode
            else receptionist_v67
            if self.receptionist_v67_mode
            else receptionist_v66
            if self.receptionist_v66_mode
            else receptionist_v65
            if self.receptionist_v65_mode
            else receptionist_v64
            if self.receptionist_v64_mode
            else receptionist_v63
            if self.receptionist_v63_mode
            else receptionist_v62
            if self.receptionist_v62_mode
            else
            receptionist_v61
            if self.receptionist_v61_mode
            else receptionist_v6
            if self.receptionist_v6_mode
            else None
        )
        if receptionist_contract is not None:
            vertex_request = receptionist_contract.build_vertex_request(
                packet["model_input"]
            )
            response_schema = receptionist_contract.vertex_response_schema()
        elif self.preprinted_mode:
            vertex_request = preprinted.build_vertex_request(
                packet["model_input"]
            )
            response_schema = preprinted.vertex_response_schema()
        elif self.dialogue_mode:
            vertex_request = dialogue.build_vertex_request(
                packet["model_input"]
            )
            response_schema = dialogue.vertex_response_schema()
        elif self.structured_mode:
            vertex_request = structured.build_vertex_request(
                packet["model_input"]
            )
            response_schema = structured.vertex_response_schema()
        elif self.shared_mode:
            vertex_request = shared.build_vertex_request(
                packet["model_input"]
            )
            response_schema = shared.vertex_response_schema()
        else:
            vertex_request = lane.build_vertex_request(
                packet["model_input"]
            )
            response_schema = lane.vertex_response_schema()
        self.append_event(
            "provider_request_constructed",
            {
                "provider": "google_vertex_ai",
                "model_id": MODEL,
                "project": PROJECT,
                "service_account": SERVICE_ACCOUNT,
                "authentication": "keyless_impersonated_service_account_adc",
                "api_key_authentication_used": False,
                "location": LOCATION,
                "endpoint_hostname": HOSTNAME,
                "request_hash": lane.canonical_hash(vertex_request),
                "schema_hash": lane.canonical_hash(response_schema),
                "provider_tools": False,
                "fallback": False,
            },
        )
        self.append_event(
            "provider_call_started",
            {"endpoint_hostname": HOSTNAME, "maximum_calls": 1},
        )
        provider_packet, call_meta = self.provider_call(vertex_request)
        bounded_response_metadata = bounded_provider_response_metadata(
            provider_packet
        )
        self.append_event(
            "provider_call_received",
            {
                **call_meta,
                "model_version": (
                    provider_packet.get("modelVersion")
                    if isinstance(provider_packet.get("modelVersion"), str)
                    else None
                ),
                **bounded_response_metadata,
            },
        )
        wire_safe_repairs: list[dict[str, str]] = []
        operator_note_review: dict[str, Any] | None = None
        receptionist_output_review: dict[str, Any] | None = None
        correction_ticket: dict[str, Any] | None = None
        if receptionist_contract is not None:
            program, body, usage = receptionist_contract.parse_vertex_output(
                provider_packet
            )
            turn_code = packet["model_input"]["turn_code"]
            evaluation = receptionist_contract.evaluate_output(
                self.frame,
                program,
                body,
                turn_code=turn_code,
                **(
                    {"turn_input": packet["model_input"]}
                    if (
                        self.receptionist_v62_mode
                        or self.receptionist_v63_mode
                        or self.receptionist_v64_mode
                        or self.receptionist_v65_mode
                        or self.receptionist_v66_mode
                        or self.receptionist_v67_mode
                        or self.receptionist_v68_mode
                    )
                    else {}
                ),
                **(
                    {"now": datetime.now(timezone.utc)}
                    if self.receptionist_v68_runtime_mode
                    else {}
                ),
            )
            review = evaluation["semantic_review"] or {
                "disposition": evaluation["disposition"],
                "safe_repairs": evaluation["safe_repairs"],
                "violations": evaluation["violations"],
                "admitted_operator_ids": evaluation[
                    "admitted_operator_ids"
                ],
                "reviewed_context_revision": evaluation[
                    "reviewed_context_revision"
                ],
            }
            normalized = evaluation["normalized_plan"]
            candidate = evaluation["candidate"]
            operator_note_review = evaluation["operator_note"]
            receptionist_output_review = evaluation[
                "receptionist_output"
            ]
            if evaluation["correction_eligible"]:
                correction_ticket = (
                    receptionist_contract.build_correction_ticket(
                        body,
                        program,
                        evaluation,
                    )
                )
            completed_fields = {
                **call_meta,
                "usage": usage,
                "model_version": (
                    provider_packet.get("modelVersion")
                    if isinstance(provider_packet.get("modelVersion"), str)
                    else None
                ),
                "turn_code": turn_code,
                "model_form_body_hash": receptionist_contract.canonical_hash(
                    body
                ),
                "model_authored_field_manifest": list(
                    receptionist_contract.MODEL_AUTHORED_FIELDS
                ),
                "preprinted_field_manifest_hash": (
                    receptionist_contract.canonical_hash(
                        receptionist_contract.PREPRINTED_FIELDS
                    )
                ),
                "broker_owned_field_manifest": ["version_code"],
                "broker_judgement_repair": False,
                "natural_response_parsed_into_form": False,
                "program_hash": receptionist_contract.canonical_hash(
                    program
                ),
                "typed_program": structured.audit_typed_program(program),
                "receptionist_output": {
                    "disposition": receptionist_output_review[
                        "disposition"
                    ],
                    "violations": receptionist_output_review[
                        "violations"
                    ],
                    "receptionist_response": receptionist_output_review[
                        "receptionist_response"
                    ],
                    "decision_note": receptionist_output_review[
                        "decision_note"
                    ],
                    "evidence_utterance_indices": (
                        receptionist_output_review[
                            "evidence_utterance_indices"
                        ]
                    ),
                },
                "candidate_hash": (
                    lane.canonical_hash(candidate)
                    if candidate is not None
                    else None
                ),
                "wire_safe_repairs": [],
                "context_frame_review": evaluation.get(
                    "context_frame_review"
                ),
            }
        elif self.preprinted_mode:
            program, usage = preprinted.parse_vertex_program(provider_packet)
            turn_code = packet["model_input"]["turn_code"]
            evaluation = preprinted.evaluate_program(
                self.frame,
                program,
                turn_code=turn_code,
            )
            review = evaluation["semantic_review"] or {
                "disposition": evaluation["disposition"],
                "safe_repairs": evaluation["safe_repairs"],
                "violations": evaluation["violations"],
                "admitted_operator_ids": evaluation[
                    "admitted_operator_ids"
                ],
                "reviewed_context_revision": evaluation[
                    "reviewed_context_revision"
                ],
            }
            normalized = evaluation["normalized_plan"]
            candidate = evaluation["candidate"]
            operator_note_review = evaluation["operator_note"]
            if evaluation["correction_eligible"]:
                correction_ticket = preprinted.build_correction_ticket(
                    program,
                    evaluation,
                )
            body = preprinted.model_form_body(program)
            completed_fields = {
                **call_meta,
                "usage": usage,
                "model_version": (
                    provider_packet.get("modelVersion")
                    if isinstance(provider_packet.get("modelVersion"), str)
                    else None
                ),
                "turn_code": turn_code,
                "model_form_body_hash": preprinted.canonical_hash(body),
                "model_authored_field_manifest": list(
                    preprinted.MODEL_AUTHORED_FIELDS
                ),
                "preprinted_field_manifest_hash": preprinted.canonical_hash(
                    preprinted.PREPRINTED_FIELDS
                ),
                "broker_owned_field_manifest": ["version_code"],
                "broker_judgement_repair": False,
                "program_hash": preprinted.canonical_hash(program),
                "typed_program": structured.audit_typed_program(program),
                "candidate_hash": (
                    lane.canonical_hash(candidate)
                    if candidate is not None
                    else None
                ),
                "wire_safe_repairs": [],
            }
        elif self.dialogue_mode:
            program, usage = dialogue.parse_vertex_program(provider_packet)
            turn_code = packet["model_input"]["turn_code"]
            evaluation = dialogue.evaluate_program(
                self.frame,
                program,
                turn_code=turn_code,
            )
            review = evaluation["semantic_review"] or {
                "disposition": evaluation["disposition"],
                "safe_repairs": evaluation["safe_repairs"],
                "violations": evaluation["violations"],
                "admitted_operator_ids": evaluation[
                    "admitted_operator_ids"
                ],
                "reviewed_context_revision": evaluation[
                    "reviewed_context_revision"
                ],
            }
            normalized = evaluation["normalized_plan"]
            candidate = evaluation["candidate"]
            operator_note_review = evaluation["operator_note"]
            if evaluation["correction_eligible"]:
                correction_ticket = dialogue.build_correction_ticket(
                    program,
                    evaluation,
                )
            completed_fields = {
                **call_meta,
                "usage": usage,
                "model_version": (
                    provider_packet.get("modelVersion")
                    if isinstance(provider_packet.get("modelVersion"), str)
                    else None
                ),
                "turn_code": turn_code,
                "program_hash": dialogue.canonical_hash(program),
                "typed_program": structured.audit_typed_program(program),
                "candidate_hash": (
                    lane.canonical_hash(candidate)
                    if candidate is not None
                    else None
                ),
                "wire_safe_repairs": [],
            }
        elif self.structured_mode:
            program, usage = structured.parse_vertex_program(
                provider_packet
            )
            review, normalized, candidate, operator_note_review = (
                structured.proofread_program(self.frame, program)
            )
            completed_fields = {
                **call_meta,
                "usage": usage,
                "model_version": (
                    provider_packet.get("modelVersion")
                    if isinstance(provider_packet.get("modelVersion"), str)
                    else None
                ),
                "program_hash": structured.canonical_hash(program),
                "typed_program": structured.audit_typed_program(program),
                "candidate_hash": (
                    lane.canonical_hash(candidate)
                    if candidate is not None
                    else None
                ),
                "wire_safe_repairs": [],
            }
        elif self.shared_mode:
            program, usage = shared.parse_vertex_program(provider_packet)
            review, normalized, candidate, operator_note_review = (
                shared.proofread_program(self.frame, program)
            )
            completed_fields = {
                **call_meta,
                "usage": usage,
                "model_version": (
                    provider_packet.get("modelVersion")
                    if isinstance(provider_packet.get("modelVersion"), str)
                    else None
                ),
                "program_hash": shared.canonical_hash(program),
                "typed_program": shared.audit_typed_program(program),
                "candidate_hash": (
                    lane.canonical_hash(candidate)
                    if candidate is not None
                    else None
                ),
                "wire_safe_repairs": [],
            }
        else:
            candidate, usage, wire_safe_repairs = (
                lane.parse_vertex_candidate_with_repairs(provider_packet)
            )
            review, normalized, _ = lane.proofread_candidate(
                self.frame, candidate
            )
            completed_fields = {
                **call_meta,
                "usage": usage,
                "model_version": (
                    provider_packet.get("modelVersion")
                    if isinstance(provider_packet.get("modelVersion"), str)
                    else None
                ),
                "candidate_hash": lane.canonical_hash(candidate),
                "wire_safe_repairs": wire_safe_repairs,
            }
        self.append_event("provider_call_completed", completed_fields)
        if receptionist_output_review is not None:
            response_fields: dict[str, Any] = {
                "disposition": receptionist_output_review["disposition"],
                "violations": receptionist_output_review["violations"],
                "receptionist_response_sha256": (
                    receptionist_contract.canonical_hash(
                        {
                            "text": completed_fields[
                                "receptionist_output"
                            ].get("receptionist_response")
                        }
                    )
                ),
                "decision_note_sha256": (
                    receptionist_contract.canonical_hash(
                        {
                            "text": completed_fields[
                                "receptionist_output"
                            ].get("decision_note")
                        }
                    )
                ),
                "evidence_utterance_indices": receptionist_output_review[
                    "evidence_utterance_indices"
                ],
                "natural_response_parsed_into_form": False,
                "product_delivered": False,
            }
            if receptionist_output_review["disposition"] == "admit":
                response_fields["receptionist_response"] = (
                    receptionist_output_review["receptionist_response"]
                )
                response_fields["decision_note"] = (
                    receptionist_output_review["decision_note"]
                )
            self.append_event(
                "receptionist_response_evaluated",
                response_fields,
            )
        if operator_note_review is not None:
            note_fields = {
                "disposition": operator_note_review["disposition"],
                "reason_codes": operator_note_review["reason_codes"],
                "note_sha256": operator_note_review["note_sha256"],
                "retained_utf8_bytes": operator_note_review[
                    "retained_utf8_bytes"
                ],
                "audit_only": True,
                "parsed_into_plan": False,
                "product_delivered": False,
            }
            if operator_note_review["disposition"] == "admit":
                note_fields["operator_note"] = operator_note_review[
                    "retained_text"
                ]
            self.append_event("operator_note_evaluated", note_fields)
        if correction_ticket is not None:
            self.append_event(
                "correction_ticket_issued",
                {
                    "turn_code": 1,
                    "target_turn_code": 2,
                    "ticket_hash": (
                        receptionist_contract.canonical_hash(
                            correction_ticket
                        )
                        if receptionist_contract is not None
                        else preprinted.canonical_hash(correction_ticket)
                        if self.preprinted_mode
                        else dialogue.canonical_hash(correction_ticket)
                    ),
                    "ticket": correction_ticket,
                    "complete_replacement_required": True,
                    "attempts_remaining": 1,
                    "proofreader_selected_replacement": False,
                },
            )
        proofreader_fields = {
                "disposition": review["disposition"],
                "safe_repairs": review["safe_repairs"],
                "wire_safe_repairs": wire_safe_repairs,
                "violations": review["violations"],
                "admitted_operator_ids": review["admitted_operator_ids"],
                "context_revision": review["reviewed_context_revision"],
                "freshness": "fresh",
                "supersession": "current",
                "retry_count": (
                    packet["model_input"]["turn_code"] - 1
                    if (
                        self.dialogue_mode
                        or self.preprinted_mode
                        or receptionist_contract is not None
                    )
                    else 0
                ),
                "model_id": MODEL,
                "project": PROJECT,
                "location": LOCATION,
                "edge_aborted": review["disposition"] != "admit",
                "correction_eligible": correction_ticket is not None,
                "turn_terminal": (
                    review["disposition"] == "admit"
                    or packet["model_input"]["turn_code"] == 2
                    if (
                        self.dialogue_mode
                        or self.preprinted_mode
                        or receptionist_contract is not None
                    )
                    else review["disposition"] != "admit"
                ),
            }
        if (
            self.receptionist_v62_mode
            or self.receptionist_v63_mode
            or self.receptionist_v64_mode
            or self.receptionist_v65_mode
            or self.receptionist_v66_mode
            or self.receptionist_v67_mode
            or self.receptionist_v68_mode
        ):
            proofreader_fields["context_frame_review"] = evaluation[
                "context_frame_review"
            ]
        self.append_event(
            "proofreader_completed",
            proofreader_fields,
        )
        if review["disposition"] != "admit" or normalized is None:
            raise BrokerError("proofreader_rejected")
        execution = typed_plan.execute_plan(self.frame, normalized, review)
        release = execution["final_output"]
        self.append_event(
            "release_committed",
            {
                "released_field_manifest": execution["released_field_paths"],
                "released_values": release,
                "atomic_release": True,
                "write_performed": False,
                "human_gate": True,
            },
        )
        return {
            "status": "completed",
            "release": release,
            "receptionist_output": (
                {
                    "receptionist_response": receptionist_output_review[
                        "receptionist_response"
                    ],
                    "decision_note": receptionist_output_review[
                        "decision_note"
                    ],
                    "evidence_utterance_indices": (
                        receptionist_output_review[
                            "evidence_utterance_indices"
                        ]
                    ),
                }
                if receptionist_output_review is not None
                and receptionist_output_review["disposition"] == "admit"
                else None
            ),
            "proofreader": {
                "disposition": review["disposition"],
                "safe_repairs": review["safe_repairs"],
                "wire_safe_repairs": wire_safe_repairs,
                "violations": review["violations"],
                "admitted_operator_ids": review["admitted_operator_ids"],
                "normalized_plan_sha256": review["normalized_plan_sha256"],
                "operator_note_disposition": (
                    operator_note_review["disposition"]
                    if operator_note_review is not None
                    else "not_applicable"
                ),
                **(
                    {
                        "context_frame_review": evaluation[
                            "context_frame_review"
                        ]
                    }
                    if (
                        self.receptionist_v62_mode
                        or self.receptionist_v63_mode
                        or self.receptionist_v64_mode
                        or self.receptionist_v65_mode
                        or self.receptionist_v66_mode
                        or self.receptionist_v67_mode
                        or self.receptionist_v68_mode
                    )
                    else {}
                ),
            },
        }


def build_handler(state: BrokerState):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ReceptionOneVertexBroker/1"

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def respond(self, status: int, packet: dict[str, Any]) -> None:
            body = canonical_bytes(packet)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/v1/execute":
                self.respond(404, {"status": "rejected", "reason_code": "path_invalid"})
                return
            if not hmac.compare_digest(
                self.headers.get("Authorization", ""),
                f"Bearer {state.token}",
            ):
                self.respond(
                    401,
                    {"status": "rejected", "reason_code": "broker_auth_invalid"},
                )
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                size = 0
            if size < 1 or size > MAX_CELL_REQUEST_BYTES:
                self.respond(
                    413,
                    {"status": "rejected", "reason_code": "request_size_invalid"},
                )
                return
            try:
                packet = json.loads(self.rfile.read(size))
                if not isinstance(packet, dict):
                    raise BrokerError("request_not_object")
                result = state.execute(packet)
            except (
                BrokerError,
                json.JSONDecodeError,
                lane.ModelLaneError,
                shared.SharedLanguageError,
                structured.StructuredSourceError,
                dialogue.DialogueError,
                preprinted.PreprintedFormError,
                receptionist_v6.ReceptionistFirstError,
                ValueError,
            ) as error:
                error_text = str(error)
                reason, _, detail = error_text.partition(":")
                fields: dict[str, Any] = {
                    "reason_code": reason,
                    "provider_retry": False,
                }
                if reason == "schema_invalid" and detail:
                    safe_paths = [
                        path
                        for path in detail.split(",")[:20]
                        if re.fullmatch(r"\$(?:\.[A-Za-z0-9_]+|\[[0-9]+\])*", path)
                    ]
                    fields["field_paths"] = safe_paths
                state.append_event(
                    "broker_rejected",
                    fields,
                )
                self.respond(409, {"status": "rejected", "reason_code": reason})
                self.server.shutdown_requested = True  # type: ignore[attr-defined]
                return
            self.respond(200, result)
            self.server.shutdown_requested = True  # type: ignore[attr-defined]

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen-port", type=int, required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--frame", required=True)
    args = parser.parse_args()
    state = BrokerState(args)
    state.append_event(
        "broker_ready",
        {
            "mode": "live",
            "policy_id": state.expected_request["policy_id"],
            "provider": "google_vertex_ai",
            "model_id": MODEL,
            "project": PROJECT,
            "service_account": SERVICE_ACCOUNT,
            "authentication": "keyless_impersonated_service_account_adc",
            "api_key_authentication_used": False,
            "location": LOCATION,
            "endpoint_hostname": HOSTNAME,
        },
    )
    # nosec B104 -- transient Docker-host relay requires host-interface reachability;
    # an ephemeral bearer, exact packet contract, size bound and 90s lifetime gate it.
    server = ThreadingHTTPServer(("0.0.0.0", args.listen_port), build_handler(state))  # nosec B104
    server.timeout = 1
    server.shutdown_requested = False  # type: ignore[attr-defined]
    deadline = time.monotonic() + 90
    while (
        not server.shutdown_requested  # type: ignore[attr-defined]
        and time.monotonic() < deadline
    ):
        server.handle_request()
    server.server_close()
    if not state.served:
        state.append_event("broker_timeout", {"provider_call": False})
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
