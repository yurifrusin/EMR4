#!/usr/bin/env python3
"""Host-only one-use broker for the bounded A3/B3 Sydney rehearsal.

The cell supplies one exact request packet.  This broker alone may discover the
existing impersonated ADC and contact the exact regional Vertex endpoint in
``live`` mode.  ``dry-run`` exercises the identical selector wrapping and
deterministic proofreader path without credentials or provider transport.

Raw prompts and provider responses are transient process memory only.  Audit
and response packets contain hashes, allowlisted provider metadata, proofreader
decisions, and (only after admission) the deterministic release.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib
import hmac
import json
import os
from pathlib import Path
import threading
import time
from typing import Any, BinaryIO, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from scripts import model_required_bureau_a3_b3_contracts as contracts


ZERO_HASH = "sha256:" + "0" * 64
REQUEST_SCHEMA_PATH = contracts.ARTIFACT_ROOT / "cell-request.schema.json"
LEDGER_SCHEMA_PATH = contracts.ARTIFACT_ROOT / "single-use-ledger.schema.json"
MAX_PROVIDER_ERROR_BYTES = 65536
MAX_SANITIZED_ERROR_PREFIX_BYTES = 8192
BROKER_LIFETIME_SECONDS = 90


class BrokerError(RuntimeError):
    """A fail-closed broker result with optional sanitized metadata."""

    def __init__(
        self,
        reason_code: str,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code.split(":", 1)[0]
        self.metadata = dict(metadata or {})


class _DuplicateKeyError(ValueError):
    """Raised only inside the strict JSON decoder."""


class _NoRedirectHandler(HTTPRedirectHandler):
    """Turn every redirect into an HTTPError handled as a terminal denial."""

    def redirect_request(  # type: ignore[override]
        self,
        _request: Request,
        _file_pointer: BinaryIO,
        _code: int,
        _message: str,
        _headers: Any,
        _new_url: str,
    ) -> None:
        return None


def _canonical_event_hash(value: Mapping[str, Any]) -> str:
    return contracts.prefixed_sha256(dict(value))


def _strict_json_object(raw: bytes, *, reason_code: str) -> dict[str, Any]:
    """Decode one UTF-8 JSON object while rejecting duplicate object keys."""

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise _DuplicateKeyError
            value[key] = item
        return value

    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, _DuplicateKeyError) as error:
        raise BrokerError(reason_code) from error
    if not isinstance(value, dict):
        raise BrokerError(reason_code)
    return value


def _read_error_stream(
    stream: BinaryIO,
) -> tuple[bytes, str, int, bool]:
    """Retain one bounded parse prefix and hash only bounded observed bytes."""

    digest = hashlib.sha256()
    prefix = bytearray()
    observed = 0
    oversized = False
    while observed <= MAX_PROVIDER_ERROR_BYTES:
        chunk = stream.read(min(16384, MAX_PROVIDER_ERROR_BYTES + 1 - observed))
        if not chunk:
            break
        if not isinstance(chunk, bytes):
            raise BrokerError("provider_error_stream_invalid")
        observed += len(chunk)
        digest.update(chunk)
        remaining = MAX_SANITIZED_ERROR_PREFIX_BYTES - len(prefix)
        if remaining > 0:
            prefix.extend(chunk[:remaining])
        if observed > MAX_PROVIDER_ERROR_BYTES:
            oversized = True
            break
    return (
        bytes(prefix),
        "sha256:" + digest.hexdigest(),
        observed,
        oversized,
    )


def _sanitized_provider_error(
    *,
    http_status: int,
    prefix: bytes,
    observed_hash: str,
    observed_bytes: int,
    oversized: bool,
) -> dict[str, Any]:
    """Extract enums and field paths only; never retain provider prose."""

    provider_error_code: int | None = None
    normalized_status: str | None = None
    field_paths: set[str] = set()
    try:
        packet = _strict_json_object(prefix, reason_code="provider_error_not_json")
    except BrokerError:
        packet = {}
    error = packet.get("error") if isinstance(packet, dict) else None
    if isinstance(error, dict):
        code = error.get("code")
        status = error.get("status")
        if type(code) is int:
            provider_error_code = code
        if (
            isinstance(status, str)
            and 1 <= len(status) <= 64
            and all(character == "_" or character.isupper() for character in status)
        ):
            normalized_status = status
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
                    field = (
                        violation.get("field")
                        if isinstance(violation, dict)
                        else None
                    )
                    if (
                        isinstance(field, str)
                        and 1 <= len(field) <= 160
                        and all(
                            character.isalnum()
                            or character in "_.[]-"
                            for character in field
                        )
                    ):
                        field_paths.add(field)
    packet.clear()
    return {
        "http_status": http_status,
        "provider_error_code": provider_error_code,
        "normalized_status": normalized_status,
        "field_violation_paths": sorted(field_paths),
        "discarded_error_sha256": observed_hash,
        "observed_error_bytes": observed_bytes,
        "error_stream_oversized": oversized,
        "provider_error_text_retained": False,
    }


def _safe_model_version(value: Any) -> str | None:
    if not isinstance(value, str) or not 1 <= len(value) <= 160:
        return None
    if not all(character.isalnum() or character in "._:/-" for character in value):
        return None
    return value


def _provider_binding() -> dict[str, Any]:
    return {
        "provider": "google_cloud_vertex_ai",
        "model": contracts.MODEL,
        "project": contracts.PROJECT,
        "service_account": contracts.SERVICE_ACCOUNT,
        "authentication": "existing_keyless_impersonated_service_account_adc",
        "oauth_scope": contracts.SCOPE,
        "location": contracts.LOCATION,
        "endpoint_hostname": contracts.HOSTNAME,
        "api_path": contracts.PATH,
        "api_key_authentication_used": False,
        "service_account_key_authentication_used": False,
        "fallback_used": False,
        "provider_tools_used": False,
        "grounding_used": False,
        "retrieval_used": False,
        "cached_content_used": False,
    }


def _base_metadata(state: "BrokerState") -> dict[str, Any]:
    request = state.expected_request
    return {
        "schema_version": "emr4.model_required_bureau_a3_b3.broker_result.v1",
        "mode": state.mode,
        "lane": request["lane"],
        "attempt_id": request["attempt_id"],
        "ledger_id": request["ledger_id"],
        "attempt_number": request["attempt_number"],
        "correction_of": request["correction_of"],
        "correction_reason_code": request["correction_reason_code"],
        "policy_id": request["policy_id"],
        "context_hash": request["context_hash"],
        "provider_request_hash": request["provider_request_hash"],
        "provider_binding": _provider_binding(),
        "raw_prompt_retained": False,
        "raw_provider_response_retained": False,
        "credential_or_token_retained": False,
        "product_or_database_access": False,
        "command_or_write_performed": False,
        "fallback_used": False,
    }


class BrokerState:
    """Own one exact request and one terminal execution claim."""

    def __init__(
        self,
        args: argparse.Namespace,
        *,
        opener_factory: Callable[[], Any] | None = None,
    ) -> None:
        self.mode = args.mode
        self.lane = args.lane
        self.token = Path(args.token_file).read_text(encoding="utf-8").strip()
        self.ledger_path = Path(args.ledger)
        self.audit_path = Path(args.audit)
        self.request_path = Path(args.request)
        self.context_path = Path(args.context)
        self.expected_request = contracts.load_object(self.request_path)
        self.context = contracts.load_object(self.context_path)
        self.events: list[dict[str, Any]] = []
        self._claim_lock = threading.Lock()
        self._claimed = False
        self._opener_factory = opener_factory or self._exact_opener
        if self.mode not in {"dry-run", "live"}:
            raise BrokerError("mode_invalid")
        if not 32 <= len(self.token) <= 512:
            raise BrokerError("broker_token_invalid")
        if self.audit_path.exists():
            raise BrokerError("audit_path_preexisted")
        if not self.audit_path.parent.is_dir():
            raise BrokerError("audit_parent_missing")
        self._validate_request_and_context()
        self._validate_open_ledger()

    @staticmethod
    def _exact_opener() -> Any:
        # Empty proxy configuration prevents environment-controlled proxy
        # routing.  The redirect handler converts every 3xx into HTTPError.
        return build_opener(ProxyHandler({}), HTTPSHandler(), _NoRedirectHandler())

    def _provider_request(self) -> dict[str, Any]:
        return contracts.provider_request_for_attempt(
            self.expected_request["lane"],
            self.context,
            attempt_number=self.expected_request["attempt_number"],
            correction_reason_code=self.expected_request[
                "correction_reason_code"
            ],
        )

    def _validate_request_and_context(self) -> None:
        try:
            contracts.validate_instance(REQUEST_SCHEMA_PATH, self.expected_request)
        except contracts.ContractError as error:
            raise BrokerError("cell_request_schema_invalid") from error
        lane = self.expected_request["lane"]
        if lane != self.lane:
            raise BrokerError("lane_argument_mismatch")
        try:
            if lane == contracts.LANE_RAYLEEN:
                contracts.validate_rayleen_context(self.context)
            elif lane == contracts.LANE_DAVIDA:
                contracts.validate_davida_context(self.context)
            else:
                raise contracts.ContractError("lane_invalid")
        except contracts.ContractError as error:
            raise BrokerError("context_invalid") from error
        context_hash = contracts.prefixed_sha256(self.context)
        if not hmac.compare_digest(
            self.expected_request["context_hash"], context_hash
        ):
            raise BrokerError("context_hash_mismatch")
        provider_request = self._provider_request()
        provider_request_hash = contracts.prefixed_sha256(provider_request)
        provider_request.clear()
        if not hmac.compare_digest(
            self.expected_request["provider_request_hash"],
            provider_request_hash,
        ):
            raise BrokerError("provider_request_hash_mismatch")

    def _expected_open_ledger(self) -> dict[str, Any]:
        request = self.expected_request
        live = self.mode == "live"
        return {
            "schema_version": (
                "emr4.model_required_bureau_a3_b3.single_use_ledger.v1"
            ),
            "ledger_id": request["ledger_id"],
            "attempt_id": request["attempt_id"],
            "lane": request["lane"],
            "policy_id": contracts.POLICY_ID,
            "status": "open",
            "maximum_provider_calls": 1 if live else 0,
            "provider_calls_consumed": 0,
            "reserved_cost_usd": (
                contracts.RESERVED_COST_PER_CALL_USD if live else 0
            ),
            "fallback_permitted": False,
        }

    def _validate_open_ledger(self) -> dict[str, Any]:
        try:
            ledger = contracts.load_object(self.ledger_path)
            contracts.validate_instance(LEDGER_SCHEMA_PATH, ledger)
        except (OSError, json.JSONDecodeError, contracts.ContractError) as error:
            raise BrokerError("single_use_ledger_invalid") from error
        if ledger != self._expected_open_ledger():
            raise BrokerError("single_use_ledger_not_exactly_open")
        return ledger

    def append_event(self, event_type: str, fields: Mapping[str, Any]) -> None:
        previous_hash = self.events[-1]["event_hash"] if self.events else ZERO_HASH
        event_without_hash = {
            "schema_version": (
                "emr4.model_required_bureau_a3_b3.broker_audit_event.v1"
            ),
            "sequence": len(self.events) + 1,
            "previous_hash": previous_hash,
            "event_type": event_type,
            "fields": dict(fields),
        }
        event = {
            **event_without_hash,
            "event_hash": _canonical_event_hash(event_without_hash),
        }
        self.events.append(event)
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def claim_once(self) -> None:
        with self._claim_lock:
            if self._claimed:
                raise BrokerError("broker_already_used")
            # Invalid or failing admitted traffic consumes this broker.  A
            # caller cannot probe and then reuse the same one-use process.
            self._claimed = True

    def consume_ledger(self) -> dict[str, Any]:
        ledger = self._validate_open_ledger()
        consumed = dict(ledger)
        consumed["status"] = "consumed"
        consumed["provider_calls_consumed"] = 1 if self.mode == "live" else 0
        temporary = self.ledger_path.with_name(self.ledger_path.name + ".tmp")
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
                "lane": consumed["lane"],
                "provider_call_slot_consumed": self.mode == "live",
                "provider_calls_reserved": consumed["maximum_provider_calls"],
                "reserved_cost_usd": consumed["reserved_cost_usd"],
                "fallback_permitted": False,
            },
        )
        return consumed

    def _credentials(self) -> Any:
        # Caller-supplied credential files are outside the frozen keyless ADC
        # boundary even if they happen to target the same service account.
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            raise BrokerError("google_application_credentials_override_present")
        import google.auth
        from google.auth.transport.requests import Request as GoogleRequest

        try:
            credentials, project = google.auth.default(scopes=[contracts.SCOPE])
        except Exception:
            raise BrokerError("impersonated_adc_discovery_failed") from None
        module = type(credentials).__module__
        target = getattr(credentials, "service_account_email", None)
        target_scopes = set(getattr(credentials, "_target_scopes", []) or [])
        if (
            not module.endswith("impersonated_credentials")
            or project != contracts.PROJECT
            or target != contracts.SERVICE_ACCOUNT
            or target_scopes != {contracts.SCOPE}
        ):
            raise BrokerError("impersonated_adc_binding_invalid")
        try:
            credentials.refresh(GoogleRequest())
        except Exception:
            raise BrokerError("impersonated_adc_refresh_failed") from None
        if not getattr(credentials, "token", None):
            raise BrokerError("impersonated_adc_refresh_failed")
        return credentials

    def _provider_call(
        self,
        provider_request: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        credentials = self._credentials()
        expected_url = "https://" + contracts.HOSTNAME + contracts.PATH
        if expected_url != (
            "https://australia-southeast1-aiplatform.googleapis.com"
            "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
            "publishers/google/models/gemini-2.5-flash:generateContent"
        ):
            raise BrokerError("provider_url_not_exact")
        body = contracts.canonical_bytes(provider_request)
        if len(body) > contracts.MAX_PROVIDER_REQUEST_BYTES:
            raise BrokerError("provider_request_oversized")
        request = Request(
            expected_url,
            data=body,
            headers={
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        self.append_event(
            "provider_call_started",
            {
                "endpoint_hostname": contracts.HOSTNAME,
                "api_path": contracts.PATH,
                "provider_request_hash": contracts.prefixed_sha256(
                    provider_request
                ),
                "maximum_calls": 1,
                "fallback": False,
            },
        )
        started = time.monotonic()
        try:
            with self._opener_factory().open(request, timeout=45) as response:
                final_url = response.geturl()
                status = int(response.status)
                raw = response.read(contracts.MAX_PROVIDER_RESPONSE_BYTES + 1)
        except HTTPError as error:
            prefix, error_hash, observed, oversized = _read_error_stream(error)
            safe_error = _sanitized_provider_error(
                http_status=int(error.code),
                prefix=prefix,
                observed_hash=error_hash,
                observed_bytes=observed,
                oversized=oversized,
            )
            prefix = b""
            reason = (
                "provider_redirect_denied"
                if 300 <= int(error.code) < 400
                else "provider_call_failed"
            )
            self.append_event("provider_call_failed", {**safe_error, "reason_code": reason})
            raise BrokerError(
                reason,
                metadata={"provider_contacted": True, **safe_error},
            ) from None
        except (OSError, URLError):
            raise BrokerError(
                "provider_transport_failed",
                metadata={"provider_contacted": True},
            ) from None
        latency_ms = round((time.monotonic() - started) * 1000)
        if final_url != expected_url:
            raw = b""
            raise BrokerError(
                "provider_redirect_denied",
                metadata={"provider_contacted": True, "http_status": status},
            )
        if status != 200:
            raw = b""
            raise BrokerError(
                "provider_http_status_invalid",
                metadata={"provider_contacted": True, "http_status": status},
            )
        if len(raw) > contracts.MAX_PROVIDER_RESPONSE_BYTES:
            raw = b""
            raise BrokerError(
                "provider_response_oversized",
                metadata={"provider_contacted": True, "http_status": status},
            )
        response_hash = "sha256:" + hashlib.sha256(raw).hexdigest()
        response_bytes = len(raw)
        packet = _strict_json_object(raw, reason_code="provider_response_not_json")
        raw = b""
        return packet, {
            "provider_contacted": True,
            "http_status": status,
            "latency_ms": latency_ms,
            "discarded_provider_response_sha256": response_hash,
            "provider_response_bytes": response_bytes,
            "raw_provider_response_retained": False,
        }

    @staticmethod
    def _dry_run_packet(lane: str) -> dict[str, Any]:
        selector = contracts.canonical_model_body_fixture(lane)
        return {
            "candidates": [
                {
                    "finishReason": "STOP",
                    "content": {
                        "parts": [
                            {
                                "text": contracts.canonical_bytes(selector).decode(
                                    "utf-8"
                                )
                            }
                        ]
                    },
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 0,
                "candidatesTokenCount": 0,
                "thoughtsTokenCount": 0,
                "totalTokenCount": 0,
            },
            "modelVersion": "provider-free-selector-fixture",
        }

    def execute(self, request_packet: dict[str, Any]) -> dict[str, Any]:
        self.claim_once()
        if request_packet != self.expected_request:
            raise BrokerError("cell_request_not_exact")
        self.append_event(
            "request_admitted",
            {
                "lane": request_packet["lane"],
                "attempt_id": request_packet["attempt_id"],
                "ledger_id": request_packet["ledger_id"],
                "attempt_number": request_packet["attempt_number"],
                "correction_of": request_packet["correction_of"],
                "correction_reason_code": request_packet[
                    "correction_reason_code"
                ],
                "policy_id": request_packet["policy_id"],
                "cell_request_hash": contracts.prefixed_sha256(request_packet),
                "context_hash": request_packet["context_hash"],
                "provider_request_hash": request_packet[
                    "provider_request_hash"
                ],
            },
        )
        self.consume_ledger()
        provider_request = self._provider_request()
        actual_request_hash = contracts.prefixed_sha256(provider_request)
        if not hmac.compare_digest(
            actual_request_hash,
            request_packet["provider_request_hash"],
        ):
            provider_request.clear()
            raise BrokerError("provider_request_hash_mismatch")
        self.append_event(
            "provider_request_constructed",
            {
                **_provider_binding(),
                "provider_request_hash": actual_request_hash,
                "response_schema_hash": contracts.prefixed_sha256(
                    contracts.provider_response_schema(request_packet["lane"])
                ),
                "raw_prompt_retained": False,
            },
        )

        if self.mode == "dry-run":
            provider_packet = self._dry_run_packet(request_packet["lane"])
            call_metadata: dict[str, Any] = {
                "provider_contacted": False,
                "http_status": None,
                "latency_ms": 0,
                "discarded_provider_response_sha256": None,
                "provider_response_bytes": 0,
                "raw_provider_response_retained": False,
                "fixture_used": True,
            }
            self.append_event(
                "provider_call_simulated",
                {
                    "provider_contacted": False,
                    "fixture": "committed_selector_only_candidate",
                },
            )
        else:
            provider_packet, call_metadata = self._provider_call(provider_request)
            call_metadata["fixture_used"] = False
        provider_request.clear()

        bounded_metadata = contracts.bounded_provider_metadata(provider_packet)
        model_version = _safe_model_version(provider_packet.get("modelVersion"))
        try:
            selector_body = contracts.extract_provider_candidate(provider_packet)
        except contracts.ContractError as error:
            provider_packet.clear()
            raise BrokerError(
                str(error).split(":", 1)[0],
                metadata={
                    **call_metadata,
                    "provider_metadata": bounded_metadata,
                    "model_version": model_version,
                },
            ) from None
        provider_packet.clear()
        model_authored_field_labels = {
            key: "untrusted_model" for key in sorted(selector_body)
        }

        try:
            candidate = contracts.wrap_provider_body(
                request_packet["lane"],
                selector_body,
                self.context,
            )
        except contracts.ContractError as error:
            reason = str(error).split(":", 1)[0]
            proof = {
                "verdict": "rejected",
                "lane": request_packet["lane"],
                "reason_code": reason,
                "candidate_hash": contracts.prefixed_sha256(selector_body),
                "correction_eligible": reason == "schema_invalid",
                "released": None,
            }
        else:
            proof = contracts.proofread(
                request_packet["lane"], candidate, self.context
            )
            candidate.clear()
        selector_body.clear()

        sanitized_provider = {
            **call_metadata,
            **bounded_metadata,
            "model_version": model_version,
            "provider_text_retained": False,
            "raw_prompt_retained": False,
            "raw_response_retained": False,
        }
        proof_metadata = {
            "verdict": proof["verdict"],
            "reason_code": proof["reason_code"],
            "candidate_hash": proof["candidate_hash"],
            "correction_eligible": proof["correction_eligible"],
            "model_authored_field_labels": model_authored_field_labels,
        }
        self.append_event(
            (
                "provider_call_completed"
                if self.mode == "live"
                else "provider_fixture_completed"
            ),
            sanitized_provider,
        )
        self.append_event("proofreader_completed", proof_metadata)

        release = proof["released"] if proof["verdict"] == "admitted" else None
        if release is not None:
            self.append_event(
                "release_committed",
                {
                    "release_hash": contracts.prefixed_sha256(release),
                    "released_field_manifest": sorted(release),
                    "atomic_release": True,
                    "advisory_only": True,
                    "product_read": False,
                    "command": False,
                    "write": False,
                    "success": False,
                },
            )
        return {
            # The generic credential-free cell admits only this transport-level
            # terminal value.  Proofreader admission remains explicit below.
            "status": "completed",
            "release": release,
            "proofreader": proof_metadata,
            "provider_metadata": sanitized_provider,
            "metadata": {
                **_base_metadata(self),
                "provider": sanitized_provider,
                "proofreader": proof_metadata,
            },
        }


def build_handler(state: BrokerState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "EMR4A3B3Broker/1"

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def _json(self, status: int, packet: Mapping[str, Any]) -> None:
            body = contracts.canonical_bytes(dict(packet))
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/v1/execute":
                self._json(
                    404,
                    {"status": "rejected", "reason_code": "path_invalid"},
                )
                return
            supplied = self.headers.get("Authorization", "")
            if not hmac.compare_digest(supplied, f"Bearer {state.token}"):
                self._json(
                    401,
                    {
                        "status": "rejected",
                        "reason_code": "broker_auth_invalid",
                    },
                )
                return
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0]
            if content_type.strip().lower() != "application/json":
                self._json(
                    415,
                    {
                        "status": "rejected",
                        "reason_code": "content_type_invalid",
                    },
                )
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                size = 0
            if size < 1 or size > contracts.MAX_CELL_REQUEST_BYTES:
                self._json(
                    413,
                    {
                        "status": "rejected",
                        "reason_code": "cell_request_size_invalid",
                    },
                )
                return
            try:
                packet = _strict_json_object(
                    self.rfile.read(size),
                    reason_code="cell_request_not_json",
                )
                result = state.execute(packet)
            except BrokerError as error:
                provider_metadata = error.metadata.get("provider_metadata")
                if not isinstance(provider_metadata, dict):
                    provider_metadata = {
                        key: value
                        for key, value in error.metadata.items()
                        if key != "proofreader"
                    }
                proofreader = error.metadata.get("proofreader")
                if not isinstance(proofreader, dict):
                    proofreader = {
                        "verdict": "not_reached",
                        "reason_code": error.reason_code,
                        "correction_eligible": False,
                    }
                safe_metadata = {
                    **_base_metadata(state),
                    **error.metadata,
                    "reason_code": error.reason_code,
                }
                state.append_event(
                    "broker_rejected",
                    {
                        "reason_code": error.reason_code,
                        "provider_retry": False,
                        "provider_contacted": error.metadata.get(
                            "provider_contacted", False
                        ),
                    },
                )
                self._json(
                    409,
                    {
                        "status": "rejected",
                        "release": None,
                        "proofreader": proofreader,
                        "provider_metadata": provider_metadata,
                        "metadata": safe_metadata,
                    },
                )
                self.server.shutdown_requested = True  # type: ignore[attr-defined]
                return
            self._json(200, result)
            self.server.shutdown_requested = True  # type: ignore[attr-defined]

    return Handler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dry-run", "live"), required=True)
    parser.add_argument("--listen-port", type=int, required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--lane", choices=sorted(contracts.LANES), required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.listen_port <= 65535:
        print(
            json.dumps(
                {"status": "rejected", "reason_code": "listen_port_invalid"},
                sort_keys=True,
            )
        )
        return 2
    try:
        state = BrokerState(args)
    except (
        BrokerError,
        OSError,
        json.JSONDecodeError,
        contracts.ContractError,
    ) as error:
        reason = error.reason_code if isinstance(error, BrokerError) else "broker_setup_failed"
        print(
            json.dumps(
                {"status": "rejected", "reason_code": reason},
                sort_keys=True,
            )
        )
        return 2
    state.append_event(
        "broker_ready",
        {
            "mode": state.mode,
            "policy_id": contracts.POLICY_ID,
            "lane": state.expected_request["lane"],
            **_provider_binding(),
        },
    )
    # nosec B104 -- the exact-path Docker relay reaches the host through
    # host.docker.internal.  The port is ephemeral, bearer-authenticated,
    # size-bounded and lives for at most 90 seconds.
    server = HTTPServer(("0.0.0.0", args.listen_port), build_handler(state))  # nosec B104
    server.timeout = 1
    server.shutdown_requested = False  # type: ignore[attr-defined]
    deadline = time.monotonic() + BROKER_LIFETIME_SECONDS
    while (
        not server.shutdown_requested  # type: ignore[attr-defined]
        and time.monotonic() < deadline
    ):
        server.handle_request()
    server.server_close()
    if not state._claimed:
        state.append_event(
            "broker_timeout",
            {"provider_contacted": False, "provider_calls": 0},
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
