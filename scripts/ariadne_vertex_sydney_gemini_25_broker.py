"""Purpose-built one-use broker for the Gemini 2.5 Flash Sydney rehearsal."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import hmac
import json
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts


ZERO_HASH = "sha256:" + "0" * 64


class BrokerError(RuntimeError):
    """A bounded broker rejection."""


def read_and_hash_provider_error(
    stream: Any, *, parse_limit: int
) -> tuple[bytes, str]:
    """Hash the complete discarded stream while retaining one parse prefix."""

    if parse_limit < 1:
        raise BrokerError("provider_error_limit_invalid")
    digest = hashlib.sha256()
    prefix = bytearray()
    while True:
        chunk = stream.read(16384)
        if not chunk:
            break
        if not isinstance(chunk, bytes):
            raise BrokerError("provider_error_stream_invalid")
        digest.update(chunk)
        remaining = parse_limit - len(prefix)
        if remaining > 0:
            prefix.extend(chunk[:remaining])
    return bytes(prefix), "sha256:" + digest.hexdigest()


class BrokerState:
    def __init__(self, args: argparse.Namespace) -> None:
        self.mode = args.mode
        self.token = Path(args.token_file).read_text(encoding="utf-8").strip()
        self.ledger_path = Path(args.ledger)
        self.audit_path = Path(args.audit)
        self.policy = contracts.load_object(Path(args.policy))
        self.expected_request = contracts.load_object(Path(args.request))
        self.events: list[dict[str, Any]] = []
        self.served = False
        if len(self.token) < 32:
            raise BrokerError("broker_token_invalid")
        self._validate_policy()
        if contracts.validate_cell_request(self.expected_request):
            raise BrokerError("expected_request_invalid")

    def _validate_policy(self) -> None:
        expected = {
            "policy_id": contracts.POLICY_ID,
            "provider": "google_vertex_ai",
            "model_id": "gemini-2.5-flash",
            "project": "bernie-emr4-dev",
            "service_account": (
                "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
            ),
            "authentication": "keyless_impersonated_service_account_adc",
            "oauth_scope": "https://www.googleapis.com/auth/cloud-platform",
            "location": "australia-southeast1",
            "endpoint_hostname": (
                "australia-southeast1-aiplatform.googleapis.com"
            ),
            "automatic_fallback": False,
            "api_key_authentication": False,
            "service_account_key_authentication": False,
            "provider_tools": False,
            "function_calling": False,
            "grounding": False,
            "retrieval": False,
            "explicit_context_cache": False,
            "thinking_budget": 0,
            "maximum_provider_calls": 1,
        }
        for key, value in expected.items():
            if self.policy.get(key) != value:
                raise BrokerError(f"broker_policy_invalid:{key}")
        if self.policy.get("allowed_data_plane_hosts") != [
            "australia-southeast1-aiplatform.googleapis.com"
        ]:
            raise BrokerError("data_plane_allowlist_invalid")
        if self.policy["endpoint_hostname"] in set(
            self.policy.get("rejected_hosts", [])
        ):
            raise BrokerError("regional_host_rejected")

    def append_event(self, event_type: str, fields: dict[str, Any]) -> None:
        previous = self.events[-1]["event_hash"] if self.events else ZERO_HASH
        event = contracts.audit_event(
            sequence=len(self.events) + 1,
            previous_hash=previous,
            event_type=event_type,
            fields=fields,
        )
        self.events.append(event)
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def consume_ledger(self, request_packet: dict[str, Any]) -> None:
        ledger = contracts.load_object(self.ledger_path)
        expected = {
            "schema_version": "ariadne.vertex_sydney_single_use_ledger.v1",
            "ledger_id": request_packet["ledger_id"],
            "attempt_id": request_packet["attempt_id"],
            "policy_id": contracts.POLICY_ID,
            "status": "open",
            "maximum_provider_calls": 0 if self.mode == "dry-run" else 1,
            "provider_calls_consumed": 0,
            "fallback_permitted": False,
        }
        if ledger != expected:
            raise BrokerError("single_use_ledger_not_exactly_open")
        consumed = dict(ledger)
        consumed["status"] = "consumed"
        consumed["provider_calls_consumed"] = 0 if self.mode == "dry-run" else 1
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
                "ledger_id": ledger["ledger_id"],
                "attempt_id": ledger["attempt_id"],
                "provider_calls_reserved": consumed["provider_calls_consumed"],
            },
        )

    def _credentials(self):
        import google.auth
        from google.auth.transport.requests import Request as GoogleRequest

        try:
            credentials, project = google.auth.default(
                scopes=[self.policy["oauth_scope"]]
            )
        except Exception:
            raise BrokerError("impersonated_adc_discovery_failed") from None
        target = getattr(credentials, "service_account_email", None)
        module = type(credentials).__module__
        target_scopes = set(getattr(credentials, "_target_scopes", []) or [])
        if (
            not module.endswith("impersonated_credentials")
            or project != self.policy["project"]
            or target != self.policy["service_account"]
            or self.policy["oauth_scope"] not in target_scopes
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
        self, vertex_request: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        credentials = self._credentials()
        url = (
            "https://"
            + self.policy["endpoint_hostname"]
            + self.policy["request_path"]
        )
        if not url.startswith(
            "https://australia-southeast1-aiplatform.googleapis.com/v1/"
        ):
            raise BrokerError("provider_url_not_allowlisted")
        body = contracts.canonical_bytes(vertex_request)
        if len(body) > self.policy["maximum_request_bytes"]:
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
                raw = response.read(
                    self.policy["maximum_provider_response_bytes"] + 1
                )
                status = int(response.status)
        except HTTPError as error:
            raw_error, raw_error_hash = read_and_hash_provider_error(
                error,
                parse_limit=self.policy["maximum_provider_error_bytes"],
            )
            bounded = contracts.sanitize_provider_error(
                http_status=error.code,
                raw=raw_error,
                maximum_message_bytes=self.policy[
                    "maximum_sanitized_error_message_bytes"
                ],
                discarded_raw_error_hash=raw_error_hash,
            )
            self.append_event("provider_call_failed", bounded)
            raise BrokerError("provider_call_failed") from error
        latency_ms = round((time.monotonic() - started) * 1000)
        if len(raw) > self.policy["maximum_provider_response_bytes"]:
            raise BrokerError("provider_response_oversized")
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError as error:
            raise BrokerError("provider_response_not_json") from error
        if not isinstance(packet, dict):
            raise BrokerError("provider_response_not_object")
        usage = packet.get("usageMetadata")
        safe_usage = {}
        if isinstance(usage, dict):
            for key in (
                "promptTokenCount",
                "candidatesTokenCount",
                "thoughtsTokenCount",
                "totalTokenCount",
            ):
                value = usage.get(key)
                if type(value) is int and value >= 0:
                    safe_usage[key] = value
        return packet, {
            "http_status": status,
            "latency_ms": latency_ms,
            "usage": safe_usage,
            "model_version": (
                packet.get("modelVersion")
                if isinstance(packet.get("modelVersion"), str)
                else None
            ),
        }

    def execute(self, request_packet: dict[str, Any]) -> dict[str, Any]:
        if self.served:
            raise BrokerError("broker_already_used")
        self.served = True
        errors = contracts.validate_cell_request(request_packet)
        if errors or request_packet != self.expected_request:
            raise BrokerError("cell_request_not_exact")
        self.append_event(
            "request_admitted",
            {
                "attempt_id": request_packet["attempt_id"],
                "ledger_id": request_packet["ledger_id"],
                "policy_id": request_packet["policy_id"],
                "request_hash": contracts.canonical_hash(request_packet),
            },
        )
        self.consume_ledger(request_packet)
        vertex_request = contracts.build_vertex_request(request_packet)
        request_hash = contracts.canonical_hash(vertex_request)
        schema_hash = contracts.canonical_hash(
            contracts.provider_response_schema()
        )
        self.append_event(
            "provider_request_constructed",
            {
                "provider": self.policy["provider"],
                "model_id": self.policy["model_id"],
                "project": self.policy["project"],
                "service_account": self.policy["service_account"],
                "authentication": self.policy["authentication"],
                "api_key_authentication_used": False,
                "location": self.policy["location"],
                "endpoint_hostname": self.policy["endpoint_hostname"],
                "request_hash": request_hash,
                "schema_hash": schema_hash,
                "provider_tools": False,
                "fallback": False,
            },
        )
        if self.mode == "dry-run":
            provider_packet = contracts.provider_free_fixture_response()
            call_meta = {
                "http_status": 200,
                "latency_ms": 0,
                "usage": provider_packet["usageMetadata"],
                "model_version": "provider-free-fixture",
            }
            self.append_event(
                "provider_call_simulated",
                {"provider_contacted": False, **call_meta},
            )
        else:
            self.append_event(
                "provider_call_started",
                {
                    "endpoint_hostname": self.policy["endpoint_hostname"],
                    "maximum_calls": 1,
                },
            )
            provider_packet, call_meta = self._provider_call(vertex_request)
            self.append_event("provider_call_completed", call_meta)
        draft = contracts.extract_provider_draft(provider_packet)
        proof = contracts.proofread(draft)
        pass_dispositions = getattr(
            contracts,
            "PROOFREADER_PASS_DISPOSITIONS",
            {"released"},
        )
        proof_passed = proof["disposition"] in pass_dispositions
        self.append_event(
            "proofreader_completed",
            {
                "disposition": proof["disposition"],
                "findings": proof["findings"],
                "safe_repairs": proof["safe_repairs"],
                "released_field_manifest": proof["released_field_manifest"],
                "freshness": "fresh",
                "supersession": "current",
                "retry_count": 0,
                "model_id": self.policy["model_id"],
                "project": self.policy["project"],
                "location": self.policy["location"],
                "human_gate": bool(proof.get("human_gate", False)),
                "edge_aborted": not proof_passed,
            },
        )
        if not proof_passed:
            raise BrokerError("proofreader_rejected")
        release = proof["release"]
        self.append_event(
            "release_committed",
            {
                "released_field_manifest": proof["released_field_manifest"],
                "released_values": release,
                "atomic_release": True,
            },
        )
        return {
            "status": "completed",
            "release": release,
            "proofreader": {
                "disposition": proof["disposition"],
                "findings": proof["findings"],
                "safe_repairs": proof["safe_repairs"],
                "released_field_manifest": proof["released_field_manifest"],
            },
        }


def build_handler(state: BrokerState):
    class Handler(BaseHTTPRequestHandler):
        server_version = "AriadneVertexBroker/1"

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def _json(self, status: int, packet: dict[str, Any]) -> None:
            body = contracts.canonical_bytes(packet)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            supplied = self.headers.get("Authorization", "")
            expected = f"Bearer {state.token}"
            if self.path != "/v1/execute":
                self._json(404, {"status": "rejected", "reason_code": "path_invalid"})
                return
            if not hmac.compare_digest(supplied, expected):
                self._json(
                    401,
                    {"status": "rejected", "reason_code": "broker_auth_invalid"},
                )
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                size = 0
            if size < 1 or size > state.policy["maximum_request_bytes"]:
                self._json(
                    413,
                    {"status": "rejected", "reason_code": "request_size_invalid"},
                )
                return
            try:
                request_packet = json.loads(self.rfile.read(size))
                if not isinstance(request_packet, dict):
                    raise BrokerError("request_not_object")
                result = state.execute(request_packet)
            except (BrokerError, json.JSONDecodeError) as error:
                reason = str(error).split(":", 1)[0]
                state.append_event(
                    "broker_rejected",
                    {"reason_code": reason, "provider_retry": False},
                )
                self._json(
                    409,
                    {"status": "rejected", "reason_code": reason},
                )
                self.server.shutdown_requested = True  # type: ignore[attr-defined]
                return
            self._json(200, result)
            self.server.shutdown_requested = True  # type: ignore[attr-defined]

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dry-run", "live"), required=True)
    parser.add_argument("--listen-port", type=int, required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    state = BrokerState(args)
    state.append_event(
        "broker_ready",
        {
            "mode": args.mode,
            "policy_id": state.policy["policy_id"],
            "provider": state.policy["provider"],
            "model_id": state.policy["model_id"],
            "project": state.policy["project"],
            "service_account": state.policy["service_account"],
            "authentication": state.policy["authentication"],
            "api_key_authentication_used": False,
            "location": state.policy["location"],
            "endpoint_hostname": state.policy["endpoint_hostname"],
        },
    )
    server = ThreadingHTTPServer(("0.0.0.0", args.listen_port), build_handler(state))
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
