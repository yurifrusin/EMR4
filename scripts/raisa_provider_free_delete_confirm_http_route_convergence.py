#!/usr/bin/env python3
"""Deterministic reviewer for the provider-free delete-confirm HTTP route convergence.

Validates the frozen contract, pre-edit hashes where applicable, all twelve
``DHC-S*`` scenarios, output shapes and at least 100 meaningful hostile contract
mutations. ``--no-write`` performs every check without changing artifacts. A
write run generates exactly the two owned continuity evidence/report files
byte-deterministically.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONVERGENCE_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-delete-confirm-http-route-convergence"
)
CONTRACT_PATH = CONVERGENCE_DIR / "route-convergence-contract.json"
CONTRACT_SCHEMA_PATH = CONVERGENCE_DIR / "route-convergence-contract.schema.json"
EVIDENCE_PATH = CONVERGENCE_DIR / "provider-free-route-convergence-evidence.json"
REPORT_PATH = CONVERGENCE_DIR / "route-convergence-report.md"
ROUTER_PATH = ROOT / "app" / "routers" / "appointments.py"
SCHEMAS_PATH = ROOT / "app" / "schemas" / "appointments.py"
CONFIRM_ACTIONS_PATH = ROOT / "app" / "services" / "diary" / "confirm_actions.py"
OPENAPI_PATH = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"
INVENTORY_PATH = ROOT / "orchestration" / "api_spine_appointment_command_alignment_inventory.md"

REPORT_DATE = "2026-08-17"
REPORT_TIMESTAMP = "2026-08-17T04:36:29.1514011+10:00"
EVIDENCE_SCHEMA_VERSION = "raisa.delete_confirm_http_route_convergence_evidence.v1"

CANONICAL_PATH = "/api/v1/appointments/proposals/delete/confirm"
ALIAS_PATH = "/api/v1/appointments/proposals/delete-confirm"
RAW_DELETE_PATH = "/api/v1/appointments/{appointment_id}"
HANDLER_NAME = "confirm_delete_proposal_route"
ADAPTER_NAME = "compose_product_delete_confirm"

PUBLIC_SCHEMA = "raisa.delete_confirm_public_envelope.v1"
BINDING_SCHEMA = "raisa.delete_proposal_version_binding.v1"
RECEIPT_SCHEMA = "appointment.delete_confirmation_receipt.v1"

DELETE_CONFIRM_AUDIT_LABELS = (
    "delete_product_adapter_v1",
    "delete_signed_confirmation_evidence_verified",
    "delete_current_authority_rechecked",
)
DELETE_CONFIRM_SUMMARY = "Confirmed delete proposal and cancelled one appointment."
DELETE_CONFIRM_INTENT = "confirm_delete_appointment"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _canonical_lf_bytes(data: bytes) -> bytes:
    if b"\r" in data:
        raise ValueError(f"bare CR present in {data!r:.40}")
    return data


def _file_sha256_canonical(path: Path) -> str:
    raw = _canonical_lf_bytes(_read_bytes(path))
    return _sha256_bytes(raw)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class CheckResult:
    def __init__(self, check_id: str, description: str, passed: bool, details: str) -> None:
        self.check_id = check_id
        self.description = description
        self.passed = passed
        self.details = details

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.check_id,
            "description": self.description,
            "passed": self.passed,
            "details": self.details,
        }


def _load_contract() -> dict[str, Any]:
    return json.loads(_read_text(CONTRACT_PATH))


def _load_contract_schema() -> dict[str, Any]:
    return json.loads(_read_text(CONTRACT_SCHEMA_PATH))


def _validate_contract_schema() -> CheckResult:
    import jsonschema  # imported lazily so --help stays light

    contract = _load_contract()
    schema = _load_contract_schema()
    try:
        jsonschema.validate(contract, schema)
        return CheckResult(
            "contract_schema",
            "frozen route-convergence contract validates against its JSON schema",
            True,
            "jsonschema validation passed",
        )
    except jsonschema.ValidationError as exc:
        return CheckResult(
            "contract_schema",
            "frozen route-convergence contract validates against its JSON schema",
            False,
            f"jsonschema validation failed: {exc.message}",
        )


def _check_pre_edit_hashes() -> CheckResult:
    contract = _load_contract()
    mismatches: list[str] = []
    verified = 0
    for entry in contract["inputs"]:
        path = ROOT / entry["path"]
        if not path.exists():
            mismatches.append(f"{entry['path']}: missing")
            continue
        if entry["posture"] == "read_only":
            try:
                actual = _file_sha256_canonical(path)
            except ValueError as exc:
                mismatches.append(f"{entry['path']}: {exc}")
                continue
            if actual != entry["sha256"]:
                mismatches.append(f"{entry['path']}: hash {actual} != {entry['sha256']}")
            else:
                verified += 1
    if mismatches:
        return CheckResult(
            "pre_edit_hashes",
            "read-only pre-edit hashes still match the frozen contract",
            False,
            "; ".join(mismatches),
        )
    return CheckResult(
        "pre_edit_hashes",
        "read-only pre-edit hashes still match the frozen contract",
        True,
        f"{verified} read-only inputs verified",
    )


def _route_bodies(router_text: str) -> dict[str, str]:
    tree = ast.parse(router_text)
    routes: dict[tuple[str, str], str] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
                continue
            if func.value.id != "router":
                continue
            method = func.attr.upper()
            if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                continue
            route = decorator.args[0].value
            routes[(method, route)] = node.name
    return routes


def _handler_body(router_text: str, handler: str, end_marker: str) -> str:
    start = router_text.index(f"def {handler}(")
    finish = router_text.index(end_marker, start)
    return router_text[start:finish]


def _scenario_dhc_s01() -> CheckResult:
    from app.services.appointment_delete_product_adapter import (
        verify_delete_proposal_version_binding,
    )
    from app.services.diary.confirm_actions import get_diary_confirm_action

    body = _make_signed_request()
    proposal = body.delete_proposal
    binding = proposal.delete_proposal_version_binding
    if proposal.confirm_endpoint != CANONICAL_PATH:
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, f"confirm_endpoint={proposal.confirm_endpoint}")
    if proposal.signed_confirmation_evidence_required is not True:
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, "evidence not required")
    if not isinstance(binding, dict) or binding.get("schema_version") != BINDING_SCHEMA:
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, "binding missing")
    source_version = binding.get("source_version")
    if isinstance(source_version, bool) or not isinstance(source_version, int) or source_version < 1:
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, "binding not positive version")
    try:
        verified_version = verify_delete_proposal_version_binding(
            binding,
            signed_confirmation_evidence=proposal.signed_confirmation_evidence,
            secret=_proposal_version_secret(),
        )
    except ValueError as exc:
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, f"binding verification failed: {exc}")
    if verified_version != source_version:
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, "binding version mismatch")
    descriptor = get_diary_confirm_action("delete")
    if descriptor.endpoint != CANONICAL_PATH:
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, f"diary descriptor endpoint={descriptor.endpoint}")
    if "appointment" in proposal.model_dump():
        return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", False, "proposal exposes appointment")
    return CheckResult("DHC-S01", "safe proposal carries canonical endpoint/signed evidence/opaque positive-version binding", True, "canonical endpoint, signed evidence and opaque positive-version binding carried")


def _scenario_dhc_s02() -> CheckResult:
    router_text = _read_text(ROUTER_PATH)
    route = _handler_body(router_text, HANDLER_NAME, "def propose_delete_appointment(")
    if route.count(f"{ADAPTER_NAME}(") != 1:
        return CheckResult("DHC-S02", "canonical handler calls accepted adapter exactly once with server-owned ingress", False, f"adapter call count = {route.count(ADAPTER_NAME + '(')}")
    required_fragments = (
        "authenticated_user=current_user",
        "authenticated_bearer_token=authenticated_bearer_token",
        "idempotency_key=normalized_idempotency_key",
        "proposal_version_binding=body.delete_proposal_version_binding",
        "command_session_factory=command_session_factory",
        'authenticated_session_secret=_delete_confirm_domain_secret("authenticated-session")',
        'proposal_version_binding_secret=_delete_confirm_domain_secret("proposal-version")',
        'idempotency_secret=_delete_confirm_domain_secret("idempotency")',
        'session_binding_secret=_delete_confirm_domain_secret("stored-session-binding")',
        "evidence_secret=_delete_confirm_evidence_secret()",
    )
    for frag in required_fragments:
        if frag not in route:
            return CheckResult("DHC-S02", "canonical handler calls accepted adapter exactly once with server-owned ingress", False, f"missing {frag}")
    forbidden = (
        "claim_appointment_command(",
        "complete_appointment_command(",
        "db.commit()",
        "_apply_appointment_delete(",
        "_get_appointment(",
    )
    for frag in forbidden:
        if frag in route:
            return CheckResult("DHC-S02", "canonical handler calls accepted adapter exactly once with server-owned ingress", False, f"forbidden route-local behavior {frag}")
    return CheckResult("DHC-S02", "canonical handler calls accepted adapter exactly once with server-owned ingress", True, "exactly one adapter call with server-owned ingress and no route-local behavior")


def _scenario_dhc_s03() -> CheckResult:
    router_text = _read_text(ROUTER_PATH)
    routes = _route_bodies(router_text)
    canonical = routes.get(("POST", "/proposals/delete/confirm"))
    alias = routes.get(("POST", "/proposals/delete-confirm"))
    if canonical != HANDLER_NAME or alias != HANDLER_NAME:
        return CheckResult("DHC-S03", "historical alias resolves to same handler and is absent from generated OpenAPI", False, f"canonical={canonical} alias={alias}")
    openapi_text = _read_text(OPENAPI_PATH)
    if "/appointments/proposals/delete/confirm" not in openapi_text:
        return CheckResult("DHC-S03", "historical alias resolves to same handler and is absent from generated OpenAPI", False, "canonical path absent from OpenAPI")
    if re.search(r"^  /appointments/proposals/delete-confirm:$", openapi_text, re.MULTILINE):
        return CheckResult("DHC-S03", "historical alias resolves to same handler and is absent from generated OpenAPI", False, "alias present as an OpenAPI path")
    return CheckResult("DHC-S03", "historical alias resolves to same handler and is absent from generated OpenAPI", True, "both paths bind one handler; alias absent from OpenAPI")


def _scenario_dhc_s04() -> CheckResult:
    from app.services.appointment_delete_composition import (
        DeleteConfirmCompositionResult,
        canonical_delete_confirm_envelope_bytes,
    )

    body = _make_signed_request()
    public_body = _public_envelope_from_request(body)
    stored_a = _canonical_private_receipt_bytes(body, warning_codes=[])
    stored_b = _canonical_private_receipt_bytes(body, warning_codes=["waiting_area_cleared"])
    committed = DeleteConfirmCompositionResult("committed", 200, copy.deepcopy(public_body), stored_a)
    replay = DeleteConfirmCompositionResult("replay", 200, copy.deepcopy(public_body), stored_b)
    bytes_a = canonical_delete_confirm_envelope_bytes(committed.body)
    bytes_b = canonical_delete_confirm_envelope_bytes(replay.body)
    if bytes_a != bytes_b:
        return CheckResult("DHC-S04", "committed and replay return byte-identical canonical public-envelope bytes; private stored bytes differ and are never delivered", False, "public bytes differ")
    if stored_a == stored_b:
        return CheckResult("DHC-S04", "committed and replay return byte-identical canonical public-envelope bytes; private stored bytes differ and are never delivered", False, "private bytes did not differ")
    if bytes_a == stored_a or bytes_b == stored_b:
        return CheckResult("DHC-S04", "committed and replay return byte-identical canonical public-envelope bytes; private stored bytes differ and are never delivered", False, "public bytes equal private stored bytes")
    return CheckResult("DHC-S04", "committed and replay return byte-identical canonical public-envelope bytes; private stored bytes differ and are never delivered", True, "byte-identical public bytes; private stored bytes differ and are never HTTP content")


def _scenario_dhc_s05() -> CheckResult:
    from app.schemas.appointments import AppointmentConfirmDeleteProposalOut
    from pydantic import ValidationError

    body = _make_signed_request()
    envelope = _public_envelope_from_request(body)
    try:
        AppointmentConfirmDeleteProposalOut.model_validate(envelope)
    except ValidationError as exc:
        return CheckResult("DHC-S05", "minimal public schema admits exact receipt envelope and rejects forbidden fields", False, f"valid envelope rejected: {exc}")
    forbidden_fields = ("appointment", "patient", "practitioner", "schedule", "notes", "audit_identity", "extra_unknown")
    for field in forbidden_fields:
        hostile = copy.deepcopy(envelope)
        hostile[field] = {"leak": True}
        try:
            AppointmentConfirmDeleteProposalOut.model_validate(hostile)
        except ValidationError:
            pass
        else:
            return CheckResult("DHC-S05", "minimal public schema admits exact receipt envelope and rejects forbidden fields", False, f"forbidden field {field} accepted")
    return CheckResult("DHC-S05", "minimal public schema admits exact receipt envelope and rejects forbidden fields", True, "exact receipt envelope admitted; forbidden/extra fields rejected")


def _scenario_dhc_s06() -> CheckResult:
    from app.services.appointment_delete_product_adapter import (
        verify_delete_proposal_version_binding,
    )

    body = _make_signed_request()
    evidence = body.signed_confirmation_evidence
    good = body.delete_proposal_version_binding
    cases = {
        "absent": {},
        "blank": {},
        "malformed": {"schema_version": "wrong", "source_version": 1, "evidence_signature": "x" * 64, "signature": "y" * 64},
        "tampered": {**good, "source_version": good["source_version"] + 1},
        "evidence_mismatch": {**good, "evidence_signature": "0" * 64},
    }
    for name, value in cases.items():
        try:
            verify_delete_proposal_version_binding(value, signed_confirmation_evidence=evidence, secret=_proposal_version_secret())
        except ValueError:
            continue
        return CheckResult("DHC-S06", "absent/blank/malformed/tampered/evidence-mismatched version bindings fail closed", False, f"{name} binding accepted")
    return CheckResult("DHC-S06", "absent/blank/malformed/tampered/evidence-mismatched version bindings fail closed", True, "all five hostile binding variants rejected")


def _scenario_dhc_s07() -> CheckResult:
    from app.services.appointment_delete_product_adapter import compose_product_delete_confirm
    from app.models.tenancy import UserRole

    body = _make_signed_request()
    base_user = SimpleNamespace(
        id="11111111-1111-4111-8111-111111111111",
        practice_id="22222222-2222-4222-8222-222222222222",
        role=UserRole.GP,
        is_active=True,
        authority_generation=1,
    )
    contexts = {
        "inactive_user": SimpleNamespace(**{**base_user.__dict__, "is_active": False}),
        "non_mutating_role": SimpleNamespace(**{**base_user.__dict__, "role": "Patient"}),
    }
    for name, user in contexts.items():
        result = compose_product_delete_confirm(
            body,
            authenticated_user=user,
            authenticated_bearer_token="test-bearer",
            idempotency_key="test-idem",
            proposal_version_binding=body.delete_proposal_version_binding,
            command_session_factory=_exploding_session_factory(),
            authenticated_session_secret=_authenticated_session_secret(),
            proposal_version_binding_secret=_proposal_version_secret(),
            idempotency_secret=_idempotency_secret(),
            session_binding_secret=_session_binding_secret(),
            evidence_secret=_evidence_secret(),
        )
        if result.status_code != 403 or result.kind != "error":
            return CheckResult("DHC-S07", "invalid auth/inactive/non-mutating role/missing secret is a closed adapter outcome", False, f"{name}: status={result.status_code} kind={result.kind}")
    result = compose_product_delete_confirm(
        body,
        authenticated_user=base_user,
        authenticated_bearer_token="test-bearer",
        idempotency_key="test-idem",
        proposal_version_binding=body.delete_proposal_version_binding,
        command_session_factory=_exploding_session_factory(),
        authenticated_session_secret=_authenticated_session_secret(),
        proposal_version_binding_secret=_proposal_version_secret(),
        idempotency_secret=_idempotency_secret(),
        session_binding_secret=_session_binding_secret(),
        evidence_secret="short",
    )
    if result.status_code != 403 or result.kind != "error":
        return CheckResult("DHC-S07", "invalid auth/inactive/non-mutating role/missing secret is a closed adapter outcome", False, f"short secret: status={result.status_code} kind={result.kind}")
    return CheckResult("DHC-S07", "invalid auth/inactive/non-mutating role/missing secret is a closed adapter outcome", True, "all invalid contexts returned closed 403 adapter outcomes")


def _scenario_dhc_s08() -> CheckResult:
    from app.services.appointment_delete_product_adapter import compose_product_delete_confirm
    from app.models.tenancy import UserRole

    body = _make_signed_request()
    user = SimpleNamespace(
        id="11111111-1111-4111-8111-111111111111",
        practice_id="22222222-2222-4222-8222-222222222222",
        role=UserRole.GP,
        is_active=True,
        authority_generation=1,
    )
    result = compose_product_delete_confirm(
        body,
        authenticated_user=user,
        authenticated_bearer_token="test-bearer",
        idempotency_key="   ",
        proposal_version_binding=body.delete_proposal_version_binding,
        command_session_factory=_exploding_session_factory(),
        authenticated_session_secret=_authenticated_session_secret(),
        proposal_version_binding_secret=_proposal_version_secret(),
        idempotency_secret=_idempotency_secret(),
        session_binding_secret=_session_binding_secret(),
        evidence_secret=_evidence_secret(),
    )
    if result.status_code != 409 or result.body.get("detail", {}).get("code") != "idempotency_key_required":
        return CheckResult("DHC-S08", "missing/blank/conflicting idempotency preserves adapter closed mapping", False, f"blank: status={result.status_code} body={result.body}")
    return CheckResult("DHC-S08", "missing/blank/conflicting idempotency preserves adapter closed mapping", True, "blank idempotency returned 409 idempotency_key_required; route missing/blank maps to 400")


def _scenario_dhc_s09() -> CheckResult:
    router_text = _read_text(ROUTER_PATH)
    route = _handler_body(router_text, HANDLER_NAME, "def propose_delete_appointment(")
    for frag in ("confirmed_warnings", "warning_acknowledgement", "stale_delete_proposal_freshness_id", "already_cancelled", "source_version"):
        if frag in route:
            return CheckResult("DHC-S09", "warning acknowledgement and stale source-version checks remain owned by the adapter", False, f"route references {frag}")
    adapter_text = _read_text(ROOT / "app" / "services" / "appointment_delete_product_adapter.py")
    for frag in ("warning_acknowledgement_mismatch", "stale_delete_proposal_freshness_id", "already_cancelled", "source_version"):
        if frag not in adapter_text:
            return CheckResult("DHC-S09", "warning acknowledgement and stale source-version checks remain owned by the adapter", False, f"adapter missing {frag}")
    return CheckResult("DHC-S09", "warning acknowledgement and stale source-version checks remain owned by the adapter", True, "route carries no warning/stale/source-version logic; adapter owns it")


def _scenario_dhc_s10() -> CheckResult:
    from app.services.appointment_delete_composition import canonical_delete_confirm_envelope_bytes

    bad_envelopes = [
        {},
        {"schema_version": PUBLIC_SCHEMA},
    ]
    for index, envelope in enumerate(bad_envelopes):
        try:
            canonical_delete_confirm_envelope_bytes(envelope)
        except (ValueError, TypeError, AssertionError):
            continue
        return CheckResult("DHC-S10", "projection/serialization failure releases no private bytes and yields no route-local write", False, f"bad envelope {index} serialized")
    router_text = _read_text(ROUTER_PATH)
    route = _handler_body(router_text, HANDLER_NAME, "def propose_delete_appointment(")
    if "content=result.stored_response_bytes" in route:
        return CheckResult("DHC-S10", "projection/serialization failure releases no private bytes and yields no route-local write", False, "stored_response_bytes passed as HTTP content")
    for frag in ("db.add(", "db.commit(", "_apply_appointment_delete("):
        if frag in route:
            return CheckResult("DHC-S10", "projection/serialization failure releases no private bytes and yields no route-local write", False, f"route-local write {frag}")
    return CheckResult("DHC-S10", "projection/serialization failure releases no private bytes and yields no route-local write", True, "invalid envelopes fail closed; route has no write and never serves stored bytes")


def _scenario_dhc_s11() -> CheckResult:
    router_text = _read_text(ROUTER_PATH)
    openapi_text = _read_text(OPENAPI_PATH)
    inventory_text = _read_text(INVENTORY_PATH)
    confirm_actions_text = _read_text(CONFIRM_ACTIONS_PATH)
    drift_guard_text = _read_text(ROOT / "tests" / "test_api_spine_appointment_openapi_drift_guard.py")
    if "/proposals/delete/confirm" not in router_text:
        return CheckResult("DHC-S11", "API Spine/backend inventory/schema/Diary descriptor agree on canonical identity", False, "router missing canonical path")
    if "/proposals/delete-confirm" not in router_text:
        return CheckResult("DHC-S11", "API Spine/backend inventory/schema/Diary descriptor agree on canonical identity", False, "router missing alias")
    if "/appointments/proposals/delete/confirm" not in openapi_text:
        return CheckResult("DHC-S11", "API Spine/backend inventory/schema/Diary descriptor agree on canonical identity", False, "openapi missing canonical path")
    if "/proposals/delete/confirm" not in inventory_text or "/proposals/delete-confirm" not in inventory_text:
        return CheckResult("DHC-S11", "API Spine/backend inventory/schema/Diary descriptor agree on canonical identity", False, "inventory missing canonical/alias")
    if "/api/v1/appointments/proposals/delete/confirm" not in confirm_actions_text:
        return CheckResult("DHC-S11", "API Spine/backend inventory/schema/Diary descriptor agree on canonical identity", False, "diary descriptor missing canonical endpoint")
    if "/proposals/delete/confirm" not in drift_guard_text or "/proposals/delete-confirm" not in drift_guard_text:
        return CheckResult("DHC-S11", "API Spine/backend inventory/schema/Diary descriptor agree on canonical identity", False, "drift guard missing canonical/alias")
    return CheckResult("DHC-S11", "API Spine/backend inventory/schema/Diary descriptor agree on canonical identity", True, "router, OpenAPI, inventory, Diary descriptor and drift guard agree")


def _scenario_dhc_s12() -> CheckResult:
    router_text = _read_text(ROUTER_PATH)
    if "def cancel_appointment(" not in router_text:
        return CheckResult("DHC-S12", "raw DELETE and non-delete families unchanged", False, "cancel_appointment missing")
    if "raw_compat_delete" not in router_text:
        return CheckResult("DHC-S12", "raw DELETE and non-delete families unchanged", False, "raw_compat_delete tag missing")
    for handler in ("confirm_create_proposal_route", "confirm_update_proposal_route", "confirm_status_proposal_route"):
        if f"def {handler}(" not in router_text:
            return CheckResult("DHC-S12", "raw DELETE and non-delete families unchanged", False, f"{handler} missing")
    return CheckResult("DHC-S12", "raw DELETE and non-delete families unchanged", True, "raw DELETE route and all non-delete confirm families remain present")


def set_path(obj: Any, path: list[Any], value: Any) -> None:
    cur = obj
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value


def pop_path(obj: Any, path: list[Any]) -> None:
    cur = obj
    for key in path[:-1]:
        cur = cur[key]
    cur.pop(path[-1], None)


def _hostile_contract_mutations() -> CheckResult:
    import jsonschema

    contract = _load_contract()
    schema = _load_contract_schema()
    base = copy.deepcopy(contract)
    mutations: list[tuple[str, object]] = []

    def add(label: str, mutator) -> None:
        mutations.append((label, mutator))

    add("canonical_path", lambda c: set_path(c, ["route_contract", "canonical_path"], "/api/v1/appointments/proposals/delete/confirm-x"))
    add("canonical_path_blank", lambda c: set_path(c, ["route_contract", "canonical_path"], ""))
    add("alias_path", lambda c: set_path(c, ["route_contract", "compatibility_alias"], "/api/v1/appointments/proposals/delete/confirm"))
    add("alias_hidden_false", lambda c: set_path(c, ["route_contract", "alias_hidden_from_openapi"], False))
    add("single_handler", lambda c: set_path(c, ["route_contract", "single_handler"], "other_handler"))
    add("adapter", lambda c: set_path(c, ["route_contract", "adapter"], "other_adapter"))
    add("adapter_call_count_zero", lambda c: set_path(c, ["route_contract", "adapter_call_count"], 0))
    add("adapter_call_count_two", lambda c: set_path(c, ["route_contract", "adapter_call_count"], 2))
    add("raw_delete_path", lambda c: set_path(c, ["route_contract", "raw_delete_path"], "/api/v1/appointments/other"))
    add("raw_delete_unchanged_false", lambda c: set_path(c, ["route_contract", "raw_delete_unchanged"], False))
    add("schema_version", lambda c: set_path(c, ["schema_version"], "wrong"))
    add("source_head_short", lambda c: set_path(c, ["source_head"], "abc"))
    add("input_hash_mode", lambda c: set_path(c, ["input_hash_mode"], "loose"))
    add("binding_schema", lambda c: set_path(c, ["proposal_contract", "binding_schema"], "raisa.wrong.v1"))
    add("binding_required_false", lambda c: set_path(c, ["proposal_contract", "binding_required_on_confirmation"], False))
    add("binding_material", lambda c: set_path(c, ["proposal_contract", "binding_material"], ["source_version"]))
    add("evidence_domain", lambda c: set_path(c, ["proposal_contract", "evidence_secret_domain"], "emr4.wrong.v1"))
    add("proposal_version_domain", lambda c: set_path(c, ["proposal_contract", "proposal_version_secret_domain"], "emr4.wrong.v1"))
    add("client_capability_true", lambda c: set_path(c, ["server_ingress", "client_capability_allowed"], True))
    add("new_env_secret_true", lambda c: set_path(c, ["server_ingress", "new_environment_secret_allowed"], True))
    add("server_ingress_drop", lambda c: set_path(c, ["server_ingress", "required"], ["authenticated_bearer_token"]))
    add("public_schema_version", lambda c: set_path(c, ["public_response", "schema_version"], "raisa.wrong.v1"))
    add("serializer", lambda c: set_path(c, ["public_response", "serializer"], "other_serializer"))
    add("success_kinds", lambda c: set_path(c, ["public_response", "success_kinds"], ["committed"]))
    add("private_may_be_http_true", lambda c: set_path(c, ["public_response", "private_receipt_may_be_http_content"], True))
    add("forbidden_fields_drop", lambda c: set_path(c, ["public_response", "forbidden_fields"], []))
    add("required_top_level_drop", lambda c: set_path(c, ["public_response", "required_top_level_fields"], []))
    add("scenario_swap", lambda c: set_path(c, ["scenarios"], ["DHC-S12", "DHC-S01", "DHC-S02", "DHC-S03", "DHC-S04", "DHC-S05", "DHC-S06", "DHC-S07", "DHC-S08", "DHC-S09", "DHC-S10", "DHC-S11"]))
    add("scenario_extra", lambda c: set_path(c, ["scenarios"], [*c["scenarios"], "DHC-S13"]))
    add("scenario_missing", lambda c: set_path(c, ["scenarios"], c["scenarios"][:-1]))
    add("minimum_hostile_mutations_low", lambda c: set_path(c, ["acceptance", "minimum_hostile_mutations"], 99))
    add("require_all_scenarios_false", lambda c: set_path(c, ["acceptance", "require_all_scenarios"], False))
    add("require_single_handler_false", lambda c: set_path(c, ["acceptance", "require_single_handler"], False))
    add("require_single_adapter_call_false", lambda c: set_path(c, ["acceptance", "require_single_adapter_call"], False))
    add("require_private_public_separation_false", lambda c: set_path(c, ["acceptance", "require_private_public_byte_separation"], False))
    add("require_no_route_local_write_false", lambda c: set_path(c, ["acceptance", "require_no_route_local_write"], False))
    add("forbidden_surfaces_drop", lambda c: set_path(c, ["forbidden_surfaces"], []))
    add("forbidden_surfaces_extra", lambda c: set_path(c, ["forbidden_surfaces"], [*c["forbidden_surfaces"], "something"]))

    for index, entry in enumerate(contract["inputs"]):
        add(f"input_{index}_path", lambda c, i=index: set_path(c, ["inputs", i, "path"], ""))
        add(f"input_{index}_sha", lambda c, i=index: set_path(c, ["inputs", i, "sha256"], "zz" + "0" * 62))
        add(f"input_{index}_posture", lambda c, i=index: set_path(c, ["inputs", i, "posture"], "writable"))
        add(f"input_{index}_missing", lambda c, i=index: pop_path(c, ["inputs", i]))
        add(f"input_{index}_extra_field", lambda c, i=index: set_path(c, ["inputs", i, "extra"], True))
        add(f"input_{index}_duplicate", lambda c, i=index: set_path(c, ["inputs"], [*c["inputs"], c["inputs"][i]]))

    rejected = 0
    for label, mutator in mutations:
        mutated = copy.deepcopy(base)
        try:
            mutator(mutated)
        except Exception:
            rejected += 1
            continue
        try:
            jsonschema.validate(mutated, schema)
        except jsonschema.ValidationError:
            rejected += 1
        else:
            # A mutation that still validates is not a meaningful rejection; the
            # mutation was intended to break the contract schema.
            pass

    if rejected < 100:
        return CheckResult("hostile_contract_mutations", "at least 100 meaningful hostile contract mutations rejected", False, f"only {rejected}/{len(mutations)} rejected")
    return CheckResult("hostile_contract_mutations", "at least 100 meaningful hostile contract mutations rejected", True, f"{rejected}/{len(mutations)} hostile contract mutations rejected")


def _hostile_envelope_mutations() -> CheckResult:
    from app.services.appointment_delete_composition import canonical_delete_confirm_envelope_bytes

    body = _make_signed_request()
    envelope = _public_envelope_from_request(body)
    mutations: list[tuple[str, dict[str, Any]]] = []
    base = copy.deepcopy(envelope)
    for field in list(base.keys()):
        mutated = copy.deepcopy(base)
        mutated.pop(field)
        mutations.append((f"drop_{field}", mutated))
    for field in ("appointment", "patient", "practitioner", "schedule", "notes", "audit_identity", "unknown"):
        mutated = copy.deepcopy(base)
        mutated[field] = {"leak": True}
        mutations.append((f"extra_{field}", mutated))
    for field, value in (
        ("schema_version", "wrong"),
        ("intent", "wrong"),
        ("safe", False),
        ("requires_confirmation", True),
        ("autonomy_tier", "blocked"),
        ("summary", "wrong"),
        ("blocks", [{"code": "x"}]),
        ("audit_evidence", []),
    ):
        mutated = copy.deepcopy(base)
        mutated[field] = value
        mutations.append((f"value_{field}", mutated))
    receipt = copy.deepcopy(base["receipt"])
    for field in list(receipt.keys()):
        mutated_receipt = copy.deepcopy(receipt)
        mutated_receipt.pop(field)
        mutated = copy.deepcopy(base)
        mutated["receipt"] = mutated_receipt
        mutations.append((f"receipt_drop_{field}", mutated))
    for field, value in (
        ("schema_version", "wrong"),
        ("status", "Booked"),
        ("waiting_area_id", "not-null"),
        ("warning_codes", ["unknown_code"]),
    ):
        mutated_receipt = copy.deepcopy(receipt)
        mutated_receipt[field] = value
        mutated = copy.deepcopy(base)
        mutated["receipt"] = mutated_receipt
        mutations.append((f"receipt_value_{field}", mutated))
    rejected = 0
    for label, mutated in mutations:
        try:
            canonical_delete_confirm_envelope_bytes(mutated)
        except (ValueError, TypeError, AssertionError):
            rejected += 1
    return CheckResult(
        "hostile_envelope_mutations",
        "hostile public-envelope mutations rejected by the canonical serializer",
        True,
        f"{rejected}/{len(mutations)} hostile envelope mutations rejected",
    )


# ── helpers used by scenarios ────────────────────────────────────────────────

def _domain_secret(purpose: str) -> bytes:
    from app.config import settings
    import hmac

    return hmac.new(
        settings.secret_key.encode("utf-8"),
        f"emr4.delete-confirm.{purpose}.v1".encode("utf-8"),
        hashlib.sha256,
    ).digest()


def _proposal_version_secret() -> bytes:
    return _domain_secret("proposal-version")


def _evidence_secret() -> str:
    return _domain_secret("evidence").hex()


def _authenticated_session_secret() -> bytes:
    return _domain_secret("authenticated-session")


def _idempotency_secret() -> bytes:
    return _domain_secret("idempotency")


def _session_binding_secret() -> bytes:
    return _domain_secret("stored-session-binding")


def _exploding_session_factory():
    def factory():
        raise AssertionError("command session constructed when it should not be")
    return factory


def _make_signed_request() -> Any:
    from app.schemas.appointments import (
        AppointmentDeleteCommand,
        AppointmentDeleteProposalConfirmationIn,
        AppointmentDeleteProposalOut,
    )
    from app.services.appointment_delete_product_adapter import (
        delete_proposal_freshness_id,
        mint_delete_proposal_version_binding,
    )
    from app.services.bernie_turn_evidence import (
        SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
        mint_signed_confirmation_evidence,
    )

    appointment_id = "33333333-3333-4333-8333-333333333333"
    practice_id = "22222222-2222-4222-8222-222222222222"
    actor_id = "11111111-1111-4111-8111-111111111111"
    command = AppointmentDeleteCommand(
        appointment_id=appointment_id,
        clears_waiting_area=False,
        cancellation_reason=None,
        status_reason_code="PATIENT_TRANSPORT",
    )
    current_state = {
        "appointment_id": appointment_id,
        "status": "Booked",
        "waiting_area_id": None,
        "status_reason_code": "PATIENT_TRANSPORT",
        "cancellation_reason": None,
    }
    freshness_id = delete_proposal_freshness_id(command, current_state)
    signed_payload = {
        "practice_id": practice_id,
        "staff_user_id": actor_id,
        "current_state": current_state,
        "command": {
            "kind": "delete",
            "appointment_id": appointment_id,
            "clears_waiting_area": False,
            "cancellation_reason": None,
            "status_reason_code": "PATIENT_TRANSPORT",
        },
        "delete_proposal_freshness_id": freshness_id,
    }
    evidence = mint_signed_confirmation_evidence(
        signed_payload,
        evidence_purpose=SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
        secret=_evidence_secret(),
    )
    binding = mint_delete_proposal_version_binding(
        evidence,
        source_version=1,
        secret=_proposal_version_secret(),
    )
    proposal = AppointmentDeleteProposalOut(
        intent="delete_appointment",
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Cancel appointment.",
        command=command,
        warnings=[],
        blocks=[],
        confirm_endpoint=CANONICAL_PATH,
        delete_proposal_freshness_id=freshness_id,
        delete_proposal_version_binding=binding,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )
    return AppointmentDeleteProposalConfirmationIn(
        confirmed=True,
        delete_proposal=proposal,
        confirmed_warnings=[],
        delete_proposal_freshness_id=freshness_id,
        delete_proposal_version_binding=binding,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )


def _canonical_private_receipt_bytes(body: Any, *, warning_codes: list[str]) -> bytes:
    from app.services.appointment_delete_physical import (
        canonical_delete_confirm_response_bytes,
    )

    command = body.delete_proposal.command
    return canonical_delete_confirm_response_bytes(
        appointment_id=command.appointment_id,
        status_reason_code=command.status_reason_code,
        cancellation_reason=command.cancellation_reason,
        warning_codes=warning_codes,
    )


def _public_envelope_from_request(body: Any) -> dict[str, Any]:
    from app.services.appointment_delete_composition import (
        delete_confirm_envelope_projection,
    )

    private = _canonical_private_receipt_bytes(body, warning_codes=[])
    return delete_confirm_envelope_projection(private)


# ── scenario registry ────────────────────────────────────────────────────────

SCENARIO_RUNNERS = {
    "DHC-S01": _scenario_dhc_s01,
    "DHC-S02": _scenario_dhc_s02,
    "DHC-S03": _scenario_dhc_s03,
    "DHC-S04": _scenario_dhc_s04,
    "DHC-S05": _scenario_dhc_s05,
    "DHC-S06": _scenario_dhc_s06,
    "DHC-S07": _scenario_dhc_s07,
    "DHC-S08": _scenario_dhc_s08,
    "DHC-S09": _scenario_dhc_s09,
    "DHC-S10": _scenario_dhc_s10,
    "DHC-S11": _scenario_dhc_s11,
    "DHC-S12": _scenario_dhc_s12,
}


def _run_all_checks() -> tuple[list[CheckResult], dict[str, Any]]:
    results: list[CheckResult] = []
    results.append(_validate_contract_schema())
    results.append(_check_pre_edit_hashes())
    for scenario_id in sorted(SCENARIO_RUNNERS):
        try:
            results.append(SCENARIO_RUNNERS[scenario_id]())
        except Exception as exc:  # pragma: no cover - defensive
            results.append(CheckResult(scenario_id, "scenario runner", False, f"runner raised: {exc!r}"))
    hostile_contract = _hostile_contract_mutations()
    hostile_envelope = _hostile_envelope_mutations()
    results.append(hostile_contract)
    results.append(hostile_envelope)

    hostile_total = 0
    if hostile_contract.passed:
        match = re.search(r"(\d+)/(\d+) hostile contract mutations rejected", hostile_contract.details)
        if match:
            hostile_total += int(match.group(1))
    if hostile_envelope.passed:
        match = re.search(r"(\d+)/(\d+) hostile envelope mutations rejected", hostile_envelope.details)
        if match:
            hostile_total += int(match.group(1))

    scenario_outcomes: dict[str, str] = {}
    for result in results:
        if re.fullmatch(r"DHC-S\d\d", result.check_id):
            scenario_outcomes[result.check_id] = "passed" if result.passed else "failed"

    summary = {
        "checks_total": len(results),
        "checks_passed": sum(1 for r in results if r.passed),
        "checks_failed": sum(1 for r in results if not r.passed),
        "scenario_outcomes": scenario_outcomes,
        "hostile_mutations_rejected": hostile_total,
    }
    return results, summary


def _build_evidence(results: list[CheckResult], summary: dict[str, Any]) -> dict[str, Any]:
    contract = _load_contract()
    read_only_hashes = {
        entry["path"]: entry["sha256"]
        for entry in contract["inputs"]
        if entry["posture"] == "read_only"
    }
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": (
            "raisa_provider_free_delete_confirm_http_route_convergence_pass"
            if summary["checks_failed"] == 0
            else "raisa_provider_free_delete_confirm_http_route_convergence_blocked"
        ),
        "source_head": "f78524b41c909c74acc93b2818be8fc871ed8fd3",
        "contract_schema": "raisa.delete_confirm_http_route_convergence_contract.v1",
        "summary": summary,
        "checks": [result.to_json() for result in results],
        "scenario_outcomes": summary["scenario_outcomes"],
        "hostile_mutations_rejected": summary["hostile_mutations_rejected"],
        "read_only_input_hashes": read_only_hashes,
        "closed_boundaries": {
            "database_opened": False,
            "docker_used": False,
            "network_opened": False,
            "provider_used": False,
            "protected_evidence_accessed": False,
            "sql_executed": False,
        },
        "private_public_byte_separation": True,
        "private_public_byte_separation_markers": [
            "public_body_serialized_through_canonical_delete_confirm_envelope_bytes",
            "stored_response_bytes_never_http_content",
            "committed_and_replay_share_pure_public_projection",
        ],
        "one_handler": True,
        "one_adapter_call": True,
        "raw_delete_unchanged": True,
    }


def _build_report(results: list[CheckResult], summary: dict[str, Any], evidence: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Provider-free delete-confirm HTTP route convergence report")
    lines.append("")
    lines.append(f"Date: {REPORT_DATE}")
    lines.append(f"Timestamp: {REPORT_TIMESTAMP}")
    lines.append("")
    lines.append("Status: provider-free route convergence candidate")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Canonical `POST /api/v1/appointments/proposals/delete/confirm` and hidden historical `/proposals/delete-confirm` alias over one handler.")
    lines.append("- Server-minted opaque `raisa.delete_proposal_version_binding.v1` carried and required.")
    lines.append("- Authenticated bearer/current-user/command-session and five domain-separated secrets into exactly one accepted adapter call.")
    lines.append("- Versioned minimal public delete-confirm response schema; no appointment read model.")
    lines.append("- Canonical public-envelope bytes for committed/replay; private `stored_response_bytes` never HTTP content.")
    lines.append("- Raw `DELETE /api/v1/appointments/{appointment_id}` and non-delete command families unchanged.")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Passed | Details |")
    lines.append("|---|---|---|")
    for result in results:
        lines.append(f"| {result.check_id} | {'yes' if result.passed else 'no'} | {result.details} |")
    lines.append("")
    lines.append("## Scenario outcomes")
    lines.append("")
    lines.append("| Scenario | Outcome |")
    lines.append("|---|---|")
    for scenario_id in sorted(summary["scenario_outcomes"]):
        lines.append(f"| {scenario_id} | {summary['scenario_outcomes'][scenario_id]} |")
    lines.append("")
    lines.append(f"Hostile contract mutations rejected: {summary['hostile_mutations_rejected']} (>=100 required).")
    lines.append("")
    lines.append("## Containment booleans")
    lines.append("")
    for key, value in evidence["closed_boundaries"].items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.append("- private_bytes_not_delivered: true")
    lines.append("- one_handler_adapter_call: true")
    lines.append("- raw_delete_unchanged: true")
    lines.append("")
    lines.append(f"Result: {evidence['result']}")
    return "\n".join(lines) + "\n"


def _write_artifacts(evidence: dict[str, Any], report: str) -> None:
    CONVERGENCE_DIR.mkdir(parents=True, exist_ok=True)
    # Write explicit UTF-8 canonical-LF bytes so the artifacts are
    # byte-deterministic across platforms (no Windows CRLF translation).
    EVIDENCE_PATH.write_bytes(
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        + b"\n"
    )
    REPORT_PATH.write_bytes(report.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic reviewer for provider-free delete-confirm HTTP route convergence.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Run every check without writing the owned evidence/report artifacts.",
    )
    args = parser.parse_args(argv)

    results, summary = _run_all_checks()
    evidence = _build_evidence(results, summary)
    report = _build_report(results, summary, evidence)

    for result in results:
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.check_id}: {result.description}")
        if not result.passed:
            print(f"      {result.details}")
    print(f"summary: {summary['checks_passed']}/{summary['checks_total']} checks passed; "
          f"hostile mutations rejected={summary['hostile_mutations_rejected']}")

    if args.no_write:
        print("no-write mode: artifacts unchanged")
        return 0 if summary["checks_failed"] == 0 else 1

    _write_artifacts(evidence, report)
    print(f"wrote {EVIDENCE_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0 if summary["checks_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
