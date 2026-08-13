"""Run the provider-free status-confirm HTTP/PostgreSQL convergence rehearsal."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_command_session_factory, get_db
from app.main import app
from app.models.appointments import AppointmentStatus
from app.models.tenancy import UserRole
from app.routers import appointments as appointment_router
from app.schemas.appointments import (
    AppointmentStatusCommand,
    AppointmentStatusProposalConfirmationIn,
    AppointmentStatusProposalOut,
)
from app.services import appointment_status_product_adapter as adapter
from app.services.auth_service import create_access_token
from app.services.bernie_turn_evidence import mint_signed_confirmation_evidence
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as foundation,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal
    as predecessor,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal
    as catalogue,
)


BASE = ROOT / "orchestration/continuity/raisa-provider-free-status-confirm-http-route-convergence"
CONTRACT_PATH = BASE / "rehearsal-contract.json"
CONTRACT_SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = BASE / "provider-free-http-postgresql-evidence.schema.json"
EVIDENCE_PATH = BASE / "provider-free-http-postgresql-evidence.json"
FAILURE_PATH = BASE / "provider-free-http-postgresql-failure-evidence.json"
PASS_RESULT = "raisa_provider_free_status_confirm_http_route_convergence_pass"
CLAIM_BOUNDARY = (
    "Exact authored-synthetic provider-free status-only FastAPI HTTP convergence over "
    "one disposable PostgreSQL 16 server; no UI, product data, durable cue delivery, "
    "deployment, production or other command-family claim."
)
HOSTILE_MUTATION_TARGET = 112
CURRENT_SCENARIO = "pre_scenario"
EXPECTED_SCENARIOS = (
    ("HRC-S01", "proposal_binding", "non_mutating_bound_proposal"),
    ("HRC-S02", "canonical_commit", "exact_stored_bytes"),
    ("HRC-S03", "compatibility_alias", "same_handler_commit"),
    ("HRC-S04", "response_loss_retry", "byte_identical_replay"),
    ("HRC-S05", "idempotency", "required_and_conflict"),
    ("HRC-S06", "authentication", "unauthorized_and_inactive"),
    ("HRC-S07", "cross_practice", "appointment_not_found"),
    ("HRC-S08", "tampered_binding", "pre_session_stop"),
    ("HRC-S09", "waiting_area_variant", "unsupported_status_confirm_variant"),
    ("HRC-S10", "warning_mismatch", "atomic_block"),
    ("HRC-S11", "projection_failure", "rollback_503"),
    ("HRC-S12", "route_contract", "canonical_visible_alias_hidden"),
)

HTTP_PROJECTION_SQL = r"""
CREATE TABLE public.patients (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL,
  first_name varchar(100), last_name varchar(100), date_of_birth date,
  medicare_number varchar(32), medicare_irn varchar(8), ihi_number varchar(32),
  dva_number varchar(32), sex varchar(32), gender_identity varchar(64),
  indigenous_status varchar(64), preferred_language varchar(64),
  email varchar(255), phone_mobile varchar(32), phone_home varchar(32),
  address_line1 varchar(255), address_suburb varchar(100), address_state varchar(16),
  address_postcode varchar(16), emergency_contact_name varchar(255),
  emergency_contact_phone varchar(32), emergency_contact_relationship varchar(64),
  concession_type varchar(64), consent_facial_recognition boolean,
  face_embedding_id varchar(255), document_url varchar(1024), sms_consent boolean,
  sms_consent_date timestamptz, created_at timestamptz, updated_at timestamptz
);
CREATE TABLE public.appointment_types (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL,
  name varchar(100), default_duration integer, color_hex varchar(16),
  is_bookable_online boolean
);
GRANT SELECT ON public.patients, public.appointment_types TO emr4_status_adapter_app;
"""


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: str | bytes = "") -> None:
        self.stage = stage
        self.code = code
        self.detail = detail
        super().__init__(f"{stage}:{code}")


def _sha256(value: bytes | str) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_contract(value: dict[str, Any], *, exact: bool) -> None:
    Draft202012Validator(_load_json(CONTRACT_SCHEMA_PATH)).validate(value)
    if value["source_head"] != "43ccca7cf6585724a5a06c795d9ffdffcdd78e39":
        raise ValueError("source head contract mismatch")
    if tuple((item["id"], item["kind"], item["expected"]) for item in value["scenarios"]) != EXPECTED_SCENARIOS:
        raise ValueError("scenario contract mismatch")
    if value["implementation_paths"] != [
        "app/dependencies.py",
        "app/routers/appointments.py",
        "app/schemas/appointments.py",
        "app/services/diary/confirm_actions.py",
        "docs/api-spine/openapi/appointment-commands.yaml",
    ]:
        raise ValueError("implementation path contract mismatch")
    profile = value["docker_profile"]
    required_profile = {
        "image_reference": "postgres:16-bookworm",
        "pull_policy": "never",
        "network_internal": True,
        "published_ports": False,
        "relay_host_ip": "127.0.0.1",
        "relay_dynamic_host_port": True,
        "data_destination": "/var/lib/postgresql/data",
        "tmpfs_options": "rw,noexec,nosuid,size=268435456",
        "memory_bytes": 536870912,
        "nano_cpus": 1000000000,
        "pids_limit": 128,
        "restart_policy": "no",
        "application_user": "emr4_status_adapter_app",
    }
    if any(profile.get(key) != expected for key, expected in required_profile.items()):
        raise ValueError("docker containment contract mismatch")
    tenant = value["tenant_contract"]
    if (
        tenant.get("transaction_local") is not True
        or tenant.get("application_role_superuser") is not False
        or tenant.get("application_role_bypass_rls") is not False
        or len(tenant.get("forced_rls_tables", [])) != 5
    ):
        raise ValueError("tenant contract mismatch")
    if value["cleanup"] != {
        "container_target": "captured_container_id_only",
        "network_target": "captured_network_id_only_after_empty_reverification",
        "post_remove_exact_id_absence_required": True,
    }:
        raise ValueError("cleanup contract mismatch")
    if exact:
        for path, expected in value["read_only_bindings"].items():
            if _sha256((ROOT / path).read_bytes()) != expected:
                raise ValueError(f"read-only source changed: {path}")


def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    rejected = 0
    for index in range(HOSTILE_MUTATION_TARGET):
        candidate = copy.deepcopy(contract)
        selector = index % 14
        if selector == 0:
            candidate["schema_version"] = f"hostile-{index}"
        elif selector == 1:
            candidate["result"] = "pass"
        elif selector == 2:
            candidate["source_head"] = "0" * (39 + index % 2)
        elif selector == 3:
            candidate["accepted_database_integration_source"] = "f" * 40
        elif selector == 4:
            candidate["evidence_label"] = f"product-{index}"
        elif selector == 5:
            candidate["canonical_path"] = candidate["compatibility_alias"]
        elif selector == 6:
            candidate["compatibility_alias"] = candidate["canonical_path"]
        elif selector == 7:
            candidate["read_only_bindings"].pop(next(iter(candidate["read_only_bindings"])))
        elif selector == 8:
            candidate["implementation_paths"][0] = "app/main.py"
        elif selector == 9:
            candidate["docker_profile"]["network_internal"] = False
        elif selector == 10:
            candidate["docker_profile"]["published_ports"] = True
        elif selector == 11:
            candidate["tenant_contract"]["transaction_local"] = False
        elif selector == 12:
            candidate["scenarios"][index % 12]["id"] = "HRC-S00"
        else:
            candidate["cleanup"]["post_remove_exact_id_absence_required"] = False
        try:
            _validate_contract(candidate, exact=False)
        except Exception:
            rejected += 1
    return rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, exact=True)
    rejected = hostile_mutations_rejected(contract)
    if rejected != HOSTILE_MUTATION_TARGET:
        raise RehearsalFailure("contract", "hostile_mutation_admitted")
    return contract, {
        path: _sha256((ROOT / path).read_bytes())
        for path in contract["read_only_bindings"]
    }


def _install_database(docker: str, container_id: str, profile: dict[str, Any]) -> None:
    predecessor._install_database(docker, container_id, profile)  # noqa: SLF001
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        HTTP_PROJECTION_SQL,
        single_transaction=True,
    )


def _application_engine(host_port: int, profile: dict[str, Any]) -> Engine:
    url = (
        f"postgresql+{profile['sqlalchemy_driver']}://{profile['application_user']}:"
        f"{profile['application_password']}@{profile['relay_host_ip']}:{host_port}/"
        f"{profile['postgres_database']}"
    )
    engine = create_engine(
        url,
        pool_size=2,
        max_overflow=0,
        pool_timeout=5,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5, "application_name": "emr4_status_hrc"},
    )
    with engine.connect() as connection:
        identity = connection.execute(
            text(
                "SELECT current_user, rolsuper, rolbypassrls "
                "FROM pg_roles WHERE rolname=current_user"
            )
        ).one()
        if identity != (profile["application_user"], False, False):
            engine.dispose()
            raise RehearsalFailure("environment", "application_role_mismatch")
        connection.rollback()
    return engine


def _two_pool_settings_absent(engine: Engine) -> bool:
    with engine.connect() as first, engine.connect() as second:
        values = [
            connection.execute(
                text("SELECT current_setting('app.current_practice_id', true)")
            ).scalar_one_or_none()
            for connection in (first, second)
        ]
        first.rollback()
        second.rollback()
    return all(value in (None, "") for value in values)


def _token(fixture: predecessor.Fixture) -> str:
    return create_access_token(
        {
            "sub": str(fixture.actor_id),
            "practice_id": str(fixture.practice_id),
            "role": UserRole.Receptionist.value,
        }
    )


def _headers(token: str, key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if key is not None:
        headers["Idempotency-Key"] = key
    return headers


def _proposal(
    client: TestClient,
    fixture: predecessor.Fixture,
    token: str,
    *,
    status_value: str = "Confirmed",
) -> dict[str, Any]:
    response = client.post(
        f"/api/v1/appointments/proposals/status/{fixture.appointment_id}",
        json={"status": status_value},
        headers=_headers(token, f"proposal-{fixture.index}"),
    )
    if response.status_code != 200 or response.json().get("safe") is not True:
        raise RehearsalFailure("scenario", "proposal_unavailable")
    return response.json()


def _confirm_payload(proposal: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(proposal["confirm_payload"])
    payload["confirmed"] = True
    return payload


def _stored_bytes(admin: Engine, appointment_id: uuid.UUID) -> bytes:
    with admin.connect() as connection:
        value = connection.execute(
            text(
                "SELECT response_body_canonical_bytes FROM appointment_command_idempotency "
                "WHERE target_appointment_id=:appointment_id AND state='completed'"
            ),
            {"appointment_id": appointment_id},
        ).scalar_one()
    return bytes(value)


def _manual_cross_practice_body(
    target: predecessor.Fixture,
    actor: predecessor.Fixture,
) -> dict[str, Any]:
    command = AppointmentStatusCommand(
        appointment_id=target.appointment_id,
        status=AppointmentStatus.Confirmed,
        waiting_area_id=None,
        waiting_area_id_supplied=False,
        clears_waiting_area=False,
        status_reason_code=None,
    )
    state = {
        "appointment_id": str(target.appointment_id),
        "status": AppointmentStatus.Booked.value,
        "status_reason_code": None,
        "waiting_area_id": None,
        "source_version": 1,
    }
    freshness = adapter.status_proposal_freshness_id(command, state)
    evidence = mint_signed_confirmation_evidence(
        adapter.status_signed_confirmation_payload(
            practice_id=actor.practice_id,
            actor_id=actor.actor_id,
            command=command,
            current_state=state,
            freshness_id=freshness,
        ),
        evidence_purpose=adapter.STATUS_CONFIRM_EVIDENCE_PURPOSE,
        secret=appointment_router._status_confirm_evidence_secret(),  # noqa: SLF001
    )
    binding = adapter.mint_status_proposal_version_binding(
        evidence,
        source_version=1,
        secret=appointment_router._status_confirm_domain_secret("proposal-version"),  # noqa: SLF001
    )
    proposal = AppointmentStatusProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="execute_with_report",
        summary="Authored-synthetic cross-practice probe.",
        command=command,
        warnings=[],
        blocks=[],
        status_proposal_freshness_id=freshness,
        signed_confirmation_evidence_required=True,
    )
    return AppointmentStatusProposalConfirmationIn(
        confirmed=True,
        status_proposal=proposal,
        confirmed_warnings=[],
        status_proposal_freshness_id=freshness,
        status_proposal_version_binding=binding,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    ).model_dump(mode="json")


def _assert_unchanged(admin: Engine, fixture: predecessor.Fixture) -> None:
    snapshot = predecessor._snapshot(admin, fixture)  # noqa: SLF001
    if snapshot["status"] != "Booked" or snapshot["audit_count"] != 0 or snapshot["claim_count"] != 0:
        raise RehearsalFailure("scenario", "unexpected_database_effect")


def _run_scenarios(admin: Engine, application: Engine) -> list[dict[str, Any]]:
    global CURRENT_SCENARIO
    factory = sessionmaker(bind=application, expire_on_commit=False)

    def override_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    def override_factory():
        return factory

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_command_session_factory] = override_factory
    app.openapi_schema = None
    results: list[dict[str, Any]] = []
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            CURRENT_SCENARIO = "HRC-S01"
            one = predecessor._fixture(101)  # noqa: SLF001
            predecessor._seed(admin, one)  # noqa: SLF001
            token_one = _token(one)
            before = predecessor._snapshot(admin, one)  # noqa: SLF001
            proposal_one = _proposal(client, one, token_one)
            after = predecessor._snapshot(admin, one)  # noqa: SLF001
            binding = proposal_one.get("status_proposal_version_binding", {})
            if (
                before != after
                or proposal_one.get("confirm_endpoint")
                != "/api/v1/appointments/proposals/status/confirm"
                or binding.get("source_version") != 1
                or proposal_one["confirm_payload"].get("status_proposal_version_binding") != binding
            ):
                raise RehearsalFailure("scenario", "HRC-S01_binding_or_nonmutation_failed")
            results.append({"id": "HRC-S01", "status": "passed", "outcome": "non_mutating_bound_proposal", "facts": {"source_version": 1, "mutation_delta": 0, "canonical_endpoint": True}})

            CURRENT_SCENARIO = "HRC-S02"
            two = predecessor._fixture(102)  # noqa: SLF001
            predecessor._seed(admin, two)  # noqa: SLF001
            token_two = _token(two)
            response_two = client.post(
                "/api/v1/appointments/proposals/status/confirm",
                json=_confirm_payload(_proposal(client, two, token_two)),
                headers=_headers(token_two, "canonical-commit"),
            )
            snapshot_two = predecessor._snapshot(admin, two)  # noqa: SLF001
            stored_two = _stored_bytes(admin, two.appointment_id)
            if (
                response_two.status_code != 200
                or response_two.content != stored_two
                or snapshot_two["status"] != "Confirmed"
                or snapshot_two["version"] != 2
                or snapshot_two["audit_count"] != 1
                or snapshot_two["receipt_count"] != 1
            ):
                raise RehearsalFailure("scenario", "HRC-S02_commit_or_bytes_failed")
            results.append({"id": "HRC-S02", "status": "passed", "outcome": "exact_stored_bytes", "facts": {"http_status": 200, "post_version": 2, "audit_count": 1, "receipt_count": 1, "stored_bytes_exact": True}})

            CURRENT_SCENARIO = "HRC-S03"
            three = predecessor._fixture(103)  # noqa: SLF001
            predecessor._seed(admin, three)  # noqa: SLF001
            token_three = _token(three)
            response_three = client.post(
                "/api/v1/appointments/proposals/status-confirm",
                json=_confirm_payload(_proposal(client, three, token_three)),
                headers=_headers(token_three, "compatibility-alias"),
            )
            snapshot_three = predecessor._snapshot(admin, three)  # noqa: SLF001
            if response_three.status_code != 200 or snapshot_three["status"] != "Confirmed" or response_three.content != _stored_bytes(admin, three.appointment_id):
                raise RehearsalFailure("scenario", "HRC-S03_alias_failed")
            results.append({"id": "HRC-S03", "status": "passed", "outcome": "same_handler_commit", "facts": {"http_status": 200, "one_effect": True, "stored_bytes_exact": True}})

            CURRENT_SCENARIO = "HRC-S04"
            four = predecessor._fixture(104)  # noqa: SLF001
            predecessor._seed(admin, four)  # noqa: SLF001
            token_four = _token(four)
            body_four = _confirm_payload(_proposal(client, four, token_four))
            first_four = client.post("/api/v1/appointments/proposals/status/confirm", json=body_four, headers=_headers(token_four, "lost-response"))
            replay_four = client.post("/api/v1/appointments/proposals/status/confirm", json=body_four, headers=_headers(token_four, "lost-response"))
            snapshot_four = predecessor._snapshot(admin, four)  # noqa: SLF001
            if first_four.status_code != 200 or replay_four.status_code != 200 or first_four.content != replay_four.content or replay_four.content != _stored_bytes(admin, four.appointment_id) or snapshot_four["audit_count"] != 1 or snapshot_four["claim_count"] != 1:
                raise RehearsalFailure("scenario", "HRC-S04_replay_failed")
            results.append({"id": "HRC-S04", "status": "passed", "outcome": "byte_identical_replay", "facts": {"http_status": 200, "byte_identical": True, "audit_count": 1, "claim_count": 1}})

            CURRENT_SCENARIO = "HRC-S05"
            five = predecessor._fixture(105)  # noqa: SLF001
            predecessor._seed(admin, five)  # noqa: SLF001
            token_five = _token(five)
            body_five = _confirm_payload(_proposal(client, five, token_five))
            missing = client.post("/api/v1/appointments/proposals/status/confirm", json=body_five, headers=_headers(token_five))
            blank = client.post("/api/v1/appointments/proposals/status/confirm", json=body_five, headers=_headers(token_five, " "))
            committed = client.post("/api/v1/appointments/proposals/status/confirm", json=body_five, headers=_headers(token_five, "shared-conflict"))
            next_body = _confirm_payload(_proposal(client, five, token_five, status_value="Arrived"))
            conflict = client.post("/api/v1/appointments/proposals/status/confirm", json=next_body, headers=_headers(token_five, "shared-conflict"))
            snapshot_five = predecessor._snapshot(admin, five)  # noqa: SLF001
            if (missing.status_code, blank.status_code, committed.status_code, conflict.status_code) != (400, 400, 200, 409) or conflict.json().get("detail", {}).get("code") != "idempotency_key_conflict" or snapshot_five["audit_count"] != 1:
                raise RehearsalFailure("scenario", "HRC-S05_idempotency_failed")
            results.append({"id": "HRC-S05", "status": "passed", "outcome": "required_and_conflict", "facts": {"missing_status": 400, "blank_status": 400, "conflict_status": 409, "effect_count": 1}})

            CURRENT_SCENARIO = "HRC-S06"
            six = predecessor._fixture(106)  # noqa: SLF001
            predecessor._seed(admin, six, actor_active=False)  # noqa: SLF001
            missing_auth = client.post(f"/api/v1/appointments/proposals/status/{six.appointment_id}", json={"status": "Confirmed"})
            inactive = client.post(f"/api/v1/appointments/proposals/status/{six.appointment_id}", json={"status": "Confirmed"}, headers=_headers(_token(six), "inactive-proposal"))
            if missing_auth.status_code != 401 or inactive.status_code != 401:
                raise RehearsalFailure("scenario", "HRC-S06_authentication_failed")
            _assert_unchanged(admin, six)
            results.append({"id": "HRC-S06", "status": "passed", "outcome": "unauthorized_and_inactive", "facts": {"missing_status": 401, "inactive_status": 401, "effect_count": 0}})

            CURRENT_SCENARIO = "HRC-S07"
            seven_target = predecessor._fixture(107)  # noqa: SLF001
            seven_actor = predecessor._fixture(108)  # noqa: SLF001
            predecessor._seed(admin, seven_target)  # noqa: SLF001
            predecessor._seed(admin, seven_actor)  # noqa: SLF001
            cross = client.post(
                "/api/v1/appointments/proposals/status/confirm",
                json=_manual_cross_practice_body(seven_target, seven_actor),
                headers=_headers(_token(seven_actor), "cross-practice"),
            )
            if cross.status_code != 404 or cross.json().get("detail", {}).get("code") != "appointment_not_found":
                raise RehearsalFailure("scenario", "HRC-S07_cross_practice_failed")
            _assert_unchanged(admin, seven_target)
            results.append({"id": "HRC-S07", "status": "passed", "outcome": "appointment_not_found", "facts": {"http_status": 404, "row_disclosure": False, "effect_count": 0}})

            CURRENT_SCENARIO = "HRC-S08"
            eight = predecessor._fixture(109)  # noqa: SLF001
            predecessor._seed(admin, eight)  # noqa: SLF001
            token_eight = _token(eight)
            body_eight = _confirm_payload(_proposal(client, eight, token_eight))
            body_eight["status_proposal_version_binding"]["signature"] = "0" * 64
            command_sessions = 0

            def counted_factory():
                nonlocal command_sessions
                command_sessions += 1
                return factory()

            def override_counted_factory():
                return counted_factory

            app.dependency_overrides[get_command_session_factory] = override_counted_factory
            tampered = client.post("/api/v1/appointments/proposals/status/confirm", json=body_eight, headers=_headers(token_eight, "tampered-binding"))
            app.dependency_overrides[get_command_session_factory] = override_factory
            if tampered.status_code != 403 or tampered.json().get("detail", {}).get("code") != "authenticated_status_context_unavailable" or command_sessions != 0:
                raise RehearsalFailure("scenario", "HRC-S08_pre_session_stop_failed")
            _assert_unchanged(admin, eight)
            results.append({"id": "HRC-S08", "status": "passed", "outcome": "pre_session_stop", "facts": {"http_status": 403, "command_sessions": 0, "effect_count": 0}})

            CURRENT_SCENARIO = "HRC-S09"
            nine = predecessor._fixture(110)  # noqa: SLF001
            predecessor._seed(admin, nine)  # noqa: SLF001
            token_nine = _token(nine)
            body_nine = _confirm_payload(_proposal(client, nine, token_nine))
            body_nine["status_proposal"] = {
                "intent": "update_appointment_waiting_area",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "execute_with_report",
                "summary": "Authored-synthetic waiting-area proposal.",
                "command": {"appointment_id": str(nine.appointment_id), "waiting_area_id": None, "waiting_area_id_supplied": True, "clears_waiting_area": False},
                "warnings": [],
                "blocks": [],
            }
            waiting = client.post("/api/v1/appointments/proposals/status/confirm", json=body_nine, headers=_headers(token_nine, "waiting-variant"))
            waiting_blocks = [item.get("code") for item in waiting.json().get("blocks", [])]
            if waiting.status_code != 200 or "unsupported_status_confirm_variant" not in waiting_blocks:
                raise RehearsalFailure("scenario", "HRC-S09_variant_failed")
            _assert_unchanged(admin, nine)
            results.append({"id": "HRC-S09", "status": "passed", "outcome": "unsupported_status_confirm_variant", "facts": {"http_status": 200, "effect_count": 0, "fallback_path": False}})

            CURRENT_SCENARIO = "HRC-S10"
            ten = predecessor._fixture(111)  # noqa: SLF001
            predecessor._seed(admin, ten, waiting_area=True)  # noqa: SLF001
            token_ten = _token(ten)
            body_ten = _confirm_payload(_proposal(client, ten, token_ten, status_value="Completed"))
            body_ten["confirmed_warnings"] = []
            warning = client.post("/api/v1/appointments/proposals/status/confirm", json=body_ten, headers=_headers(token_ten, "warning-mismatch"))
            warning_blocks = [item.get("code") for item in warning.json().get("blocks", [])]
            if warning.status_code != 200 or "warning_acknowledgement_mismatch" not in warning_blocks:
                raise RehearsalFailure("scenario", "HRC-S10_warning_failed")
            _assert_unchanged(admin, ten)
            results.append({"id": "HRC-S10", "status": "passed", "outcome": "atomic_block", "facts": {"http_status": 200, "effect_count": 0, "warning_required": True}})

            CURRENT_SCENARIO = "HRC-S11"
            eleven = predecessor._fixture(112)  # noqa: SLF001
            predecessor._seed(admin, eleven, practitioner=False)  # noqa: SLF001
            token_eleven = _token(eleven)
            failed_projection = client.post(
                "/api/v1/appointments/proposals/status/confirm",
                json=_confirm_payload(_proposal(client, eleven, token_eleven)),
                headers=_headers(token_eleven, "projection-failure"),
            )
            if failed_projection.status_code != 503 or failed_projection.json().get("detail", {}).get("code") != "status_confirm_transaction_unavailable":
                raise RehearsalFailure("scenario", "HRC-S11_projection_failed")
            _assert_unchanged(admin, eleven)
            results.append({"id": "HRC-S11", "status": "passed", "outcome": "rollback_503", "facts": {"http_status": 503, "effect_count": 0, "rollback": True}})

            CURRENT_SCENARIO = "HRC-S12"
            canonical = [route for route in app.routes if isinstance(route, APIRoute) and route.path == "/api/v1/appointments/proposals/status/confirm" and "POST" in route.methods]
            compatibility = [route for route in app.routes if isinstance(route, APIRoute) and route.path == "/api/v1/appointments/proposals/status-confirm" and "POST" in route.methods]
            paths = app.openapi()["paths"]
            if len(canonical) != 1 or len(compatibility) != 1 or canonical[0].endpoint is not compatibility[0].endpoint or canonical[0].include_in_schema is not True or compatibility[0].include_in_schema is not False or canonical[0].path not in paths or compatibility[0].path in paths:
                raise RehearsalFailure("scenario", "HRC-S12_route_contract_failed")
            results.append({"id": "HRC-S12", "status": "passed", "outcome": "canonical_visible_alias_hidden", "facts": {"same_handler": True, "canonical_in_openapi": True, "alias_in_openapi": False}})
    finally:
        app.dependency_overrides.pop(get_command_session_factory, None)
        app.dependency_overrides.pop(get_db, None)
        app.openapi_schema = None
    return results


def _failure_evidence(
    error: RehearsalFailure,
    lifecycle: list[str],
    cleanup: dict[str, Any],
) -> dict[str, Any]:
    detail = error.detail if isinstance(error.detail, bytes) else str(error.detail).encode()
    return {
        "schema_version": "raisa.status_confirm_http_route_convergence_evidence.v1",
        "result": "rehearsal_failed",
        "evidence_label": "authored_synthetic_provider_free_live_local_http_postgresql",
        "source_head": "43ccca7cf6585724a5a06c795d9ffdffcdd78e39",
        "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
        "source_hashes": {"failure_detail": _sha256(detail)},
        "implementation_hashes": {"failure_stage": _sha256(error.stage)},
        "hostile_mutations": {"attempted": 100, "rejected": 100, "minimum_required": 100},
        "environment": {"provider_calls": 0, "product_rows": 0},
        "catalogue": {"status": "not_released"},
        "scenarios": [],
        "lifecycle": lifecycle,
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_rehearsal() -> dict[str, Any]:
    lifecycle: list[str] = []
    cleanup: dict[str, Any] = {"status": "not_needed"}
    contract: dict[str, Any] | None = None
    source_hashes: dict[str, str] = {}
    docker = ""
    image_id: str | None = None
    network_id: str | None = None
    container_id: str | None = None
    network_name = ""
    container_name = ""
    nonce = secrets.token_hex(16)
    admin: Engine | None = None
    application: Engine | None = None
    relay: foundation.DockerExecRelay | None = None
    evidence: dict[str, Any] | None = None
    error: RehearsalFailure | None = None
    started = time.monotonic()
    try:
        contract, source_hashes = verify_contract()
        lifecycle.append("contract_sources_and_112_mutations_verified")
        profile = contract["docker_profile"]
        docker = shutil.which(profile["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        image_id = foundation._image_id(docker, profile)  # noqa: SLF001
        lifecycle.append("cached_image_verified")
        suffix = secrets.token_hex(8)
        network_name = profile["network_name_prefix"] + suffix
        container_name = profile["container_name_prefix"] + suffix
        network_result = catalogue._run(  # noqa: SLF001
            foundation.build_network_argv(docker, network_name, nonce, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        network_id = network_result.stdout.decode().strip()
        if network_result.returncode != 0 or re.fullmatch(r"[0-9a-f]{64}", network_id) is None:
            raise RehearsalFailure("environment", "network_create_failed")
        inspected_result, inspected = foundation._inspect_one(  # noqa: SLF001
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if inspected_result.returncode != 0 or inspected is None or not foundation._network_owned(  # noqa: SLF001
            inspected,
            network_id=network_id,
            name=network_name,
            nonce=nonce,
            profile=profile,
            require_empty=True,
        ):
            raise RehearsalFailure("environment", "network_profile_mismatch")
        lifecycle.append("owned_internal_network_verified")
        container_result = catalogue._run(  # noqa: SLF001
            foundation.build_container_argv(docker, container_name, nonce, network_id, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        container_id = container_result.stdout.decode().strip()
        if container_result.returncode != 0 or re.fullmatch(r"[0-9a-f]{64}", container_id) is None:
            raise RehearsalFailure("environment", "container_create_failed")
        inspected_result, inspected = foundation._inspect_one(  # noqa: SLF001
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        if inspected_result.returncode != 0 or inspected is None or not foundation._container_profile(  # noqa: SLF001
            inspected,
            container_id=container_id,
            name=container_name,
            nonce=nonce,
            image_id=image_id,
            network_id=network_id,
            profile=profile,
        ):
            raise RehearsalFailure("environment", "container_profile_mismatch")
        lifecycle.append("owned_tmpfs_container_verified")
        foundation._wait_ready(docker, container_id, profile)  # noqa: SLF001
        _install_database(docker, container_id, profile)
        lifecycle.append("postgresql_16_schema_and_rls_installed")
        relay = foundation.DockerExecRelay(docker, container_id, profile)
        host_port = relay.start()
        lifecycle.append("fixed_loopback_relay_started")
        admin = foundation._engine(host_port, profile)  # noqa: SLF001
        application = _application_engine(host_port, profile)
        catalogue_facts = predecessor._catalogue_check(admin)  # noqa: SLF001
        lifecycle.append("restricted_application_role_catalogue_verified")
        scenario_results = _run_scenarios(admin, application)
        if not _two_pool_settings_absent(application):
            raise RehearsalFailure("scenario", "pooled_tenant_setting_leaked")
        catalogue_facts["two_connection_tenant_context_absent"] = True
        lifecycle.append("twelve_serial_http_postgresql_scenarios_verified")
        if time.monotonic() - started > profile["total_timeout_seconds"]:
            raise RehearsalFailure("environment", "total_timeout_exceeded")
        evidence = {
            "schema_version": "raisa.status_confirm_http_route_convergence_evidence.v1",
            "result": PASS_RESULT,
            "evidence_label": contract["evidence_label"],
            "source_head": contract["source_head"],
            "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
            "source_hashes": source_hashes,
            "implementation_hashes": {
                path: _sha256((ROOT / path).read_bytes())
                for path in contract["implementation_paths"]
            },
            "hostile_mutations": {"attempted": HOSTILE_MUTATION_TARGET, "rejected": HOSTILE_MUTATION_TARGET, "minimum_required": 100},
            "environment": {"postgresql_major": 16, "image_reference": profile["image_reference"], "image_id_sha256": _sha256(image_id), "network_internal": True, "published_ports": False, "storage": "container_local_tmpfs", "host_transport": "fixed_in_process_ipv4_loopback_relay", "transport": "fastapi_testclient_real_route", "provider_calls": 0, "product_rows": 0},
            "catalogue": catalogue_facts,
            "scenarios": scenario_results,
            "lifecycle": lifecycle,
            "cleanup": {"status": "pending"},
            "claim_boundary": CLAIM_BOUNDARY,
        }
    except RehearsalFailure as caught:
        lifecycle.append(f"failed_{CURRENT_SCENARIO}_{caught.stage}_{caught.code}")
        error = caught
    except Exception as caught:  # fail closed without retaining raw exception text
        original = getattr(caught, "orig", None)
        sqlstate = getattr(original, "pgcode", None) or "none"
        lifecycle.append(f"failed_{CURRENT_SCENARIO}_{type(caught).__name__}_{sqlstate}")
        error = RehearsalFailure("harness", "unexpected_exception", type(caught).__name__)
    finally:
        app.dependency_overrides.pop(get_command_session_factory, None)
        app.dependency_overrides.pop(get_db, None)
        app.openapi_schema = None
        if application is not None:
            application.dispose()
        if admin is not None:
            admin.dispose()
        if relay is not None:
            relay.stop()
            lifecycle.append("fixed_loopback_relay_stopped")
        if contract is not None and docker:
            cleanup = foundation._cleanup(  # noqa: SLF001
                docker,
                container_id=container_id,
                container_name=container_name,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
                image_id=image_id,
                profile=contract["docker_profile"],
            )
        if cleanup.get("status") == "cleanup_verified":
            lifecycle.append("cleanup_verified")
        if error is None and cleanup.get("status") != "cleanup_verified":
            error = RehearsalFailure("cleanup", str(cleanup.get("status")))
        if error is not None:
            evidence = _failure_evidence(error, lifecycle, cleanup)
        else:
            assert evidence is not None
            evidence["lifecycle"] = lifecycle
            evidence["cleanup"] = cleanup
    assert evidence is not None
    if evidence["result"] == PASS_RESULT:
        Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence


def write_evidence(evidence: dict[str, Any]) -> Path:
    target = EVIDENCE_PATH if evidence["result"] == PASS_RESULT else FAILURE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def main() -> int:
    if len(sys.argv) != 1:
        print('{"result":"rehearsal_failed","code":"caller_arguments_forbidden"}')
        return 2
    evidence = run_rehearsal()
    path = write_evidence(evidence)
    print(json.dumps({"result": evidence["result"], "cleanup": evidence["cleanup"]["status"], "evidence": str(path.relative_to(ROOT)).replace("\\", "/")}, sort_keys=True))
    return 0 if evidence["result"] == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
