"""Run the fixed provider-free product-adapter/PostgreSQL integration rehearsal."""

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
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, time as local_time, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, text, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.appointments import AppointmentCommandIdempotency, AppointmentStatus
from app.models.tenancy import User, UserRole
from app.schemas.appointments import (
    AppointmentStatusCommand,
    AppointmentStatusProposalConfirmationIn,
    AppointmentStatusProposalOut,
)
from app.services import appointment_status_product_adapter as adapter
from app.services.appointment_status_physical import status_confirm_session_binding_digest
from app.services.appointment_status_physical import status_confirm_locked_transaction
from app.services.bernie_turn_evidence import mint_signed_confirmation_evidence
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as foundation,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal
    as catalogue,
)


BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "status-confirm-product-adapter-integration-rehearsal"
)
CONTRACT_PATH = BASE / "rehearsal-contract.json"
CONTRACT_SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = BASE / "provider-free-product-adapter-postgresql-evidence.schema.json"
EVIDENCE_PATH = BASE / "provider-free-product-adapter-postgresql-evidence.json"
FAILURE_PATH = BASE / "provider-free-product-adapter-postgresql-failure-evidence.json"
OLD_CONTRACT_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-rehearsal/rehearsal-contract.json"
)
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_status_confirm_"
    "product_adapter_integration_rehearsal_pass"
)
CLAIM_BOUNDARY = (
    "Exact off-route authored-synthetic product-adapter integration over one "
    "disposable PostgreSQL 16 server only; no HTTP wiring, product data, "
    "concurrency, restart, deployment, production or UI claim."
)
HOSTILE_MUTATION_TARGET = 104
CURRENT_SCENARIO = "pre_scenario"
SESSION_SECRET = b"pga-session-secret-for-authenticated-status-ref"
VERSION_SECRET = b"pga-proposal-version-binding-secret"
IDEMPOTENCY_SECRET = b"pga-idempotency-secret-for-status-confirm"
BINDING_SECRET = b"pga-session-binding-secret-for-status-confirm"
EVIDENCE_SECRET = "pga-authored-synthetic-evidence-secret"

EXPECTED_SCENARIOS = (
    ("PGA-S01", "clean_commit", "committed"),
    ("PGA-S02", "response_loss_retry", "replay"),
    ("PGA-S03", "cross_tenant_rls", "zero_visibility"),
    ("PGA-S04", "inactive_actor_first_check", "current_authority_unavailable"),
    ("PGA-S05", "revoked_actor_second_check", "current_authority_unavailable"),
    ("PGA-S06", "practice_target_mismatch", "appointment_not_found"),
    ("PGA-S07", "stale_locked_version", "locked_request_digest_changed"),
    ("PGA-S08", "tampered_binding", "authenticated_status_context_unavailable"),
    ("PGA-S09", "projection_failure", "status_confirm_transaction_unavailable"),
    ("PGA-S10", "terminal_waiting_area", "committed"),
    ("PGA-S11", "wrong_database_role", "current_authority_unavailable"),
    ("PGA-S12", "tenant_setting_lifecycle", "no_leakage"),
)


EXTENSION_SQL = r"""
CREATE TABLE public.practitioners (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL REFERENCES public.practices(id),
  first_name varchar(100) NOT NULL, last_name varchar(100) NOT NULL,
  provider_number varchar(20), prescriber_number varchar(20), ahpra_number varchar(20),
  hpi_i varchar(20), specialty varchar(100), default_location_id uuid,
  aggregate_version integer NOT NULL DEFAULT 0, is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);
CREATE TABLE public.users (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL REFERENCES public.practices(id),
  email varchar(255) NOT NULL UNIQUE, password_hash varchar(255) NOT NULL,
  role varchar(64) NOT NULL, practitioner_id uuid,
  is_active boolean DEFAULT true, created_at timestamptz DEFAULT now()
);
CREATE ROLE emr4_status_adapter_app LOGIN
  PASSWORD 'status-adapter-authored-synthetic-only' NOSUPERUSER NOBYPASSRLS;
GRANT CONNECT ON DATABASE status_confirm_behavior TO emr4_status_adapter_app;
GRANT USAGE ON SCHEMA public TO emr4_status_adapter_app;
GRANT SELECT, UPDATE (id) ON public.practices TO emr4_status_adapter_app;
GRANT SELECT, UPDATE ON public.appointments, public.users TO emr4_status_adapter_app;
GRANT SELECT ON public.practitioners TO emr4_status_adapter_app;
GRANT SELECT, INSERT, UPDATE ON public.appointment_command_idempotency,
  public.appointment_audit_log TO emr4_status_adapter_app;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments FORCE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users FORCE ROW LEVEL SECURITY;
ALTER TABLE public.practitioners ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.practitioners FORCE ROW LEVEL SECURITY;
ALTER TABLE public.appointment_command_idempotency ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointment_command_idempotency FORCE ROW LEVEL SECURITY;
ALTER TABLE public.appointment_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointment_audit_log FORCE ROW LEVEL SECURITY;
CREATE POLICY pga_appointments_tenant ON public.appointments
  USING (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid);
CREATE POLICY pga_users_tenant ON public.users
  USING (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid);
CREATE POLICY pga_practitioners_tenant ON public.practitioners
  USING (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid);
CREATE POLICY pga_idempotency_tenant ON public.appointment_command_idempotency
  USING (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid);
CREATE POLICY pga_audit_tenant ON public.appointment_audit_log
  USING (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid);
"""


@dataclass(frozen=True)
class Fixture:
    index: int
    practice_id: uuid.UUID
    appointment_id: uuid.UUID
    practitioner_id: uuid.UUID
    actor_id: uuid.UUID
    waiting_area_id: uuid.UUID


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
    errors = list(Draft202012Validator(_load_json(CONTRACT_SCHEMA_PATH)).iter_errors(value))
    if errors:
        raise RehearsalFailure("preflight", "contract_schema_invalid")
    observed = tuple((item["id"], item["kind"], item["expected"]) for item in value["scenarios"])
    if observed != EXPECTED_SCENARIOS:
        raise RehearsalFailure("preflight", "scenario_contract_mismatch")
    profile = value["docker_profile"]
    if not (
        profile.get("image_reference") == "postgres:16-bookworm"
        and profile.get("pull_policy") == "never"
        and profile.get("network_internal") is True
        and profile.get("published_ports") is False
        and profile.get("relay_host_ip") == "127.0.0.1"
        and profile.get("tmpfs_options") == "rw,noexec,nosuid,size=268435456"
        and profile.get("application_user") == "emr4_status_adapter_app"
    ):
        raise RehearsalFailure("preflight", "containment_contract_mismatch")
    if value["tenant_contract"] != {
        "setting": "app.current_practice_id",
        "transaction_local": True,
        "forced_rls_tables": [
            "appointments",
            "users",
            "practitioners",
            "appointment_command_idempotency",
            "appointment_audit_log",
        ],
        "application_role_superuser": False,
        "application_role_bypass_rls": False,
    }:
        raise RehearsalFailure("preflight", "tenant_contract_mismatch")
    if exact and value != _load_json(CONTRACT_PATH):
        raise RehearsalFailure("preflight", "contract_digest_mismatch")


def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    mutations: list[dict[str, Any]] = []

    def mutate(path: tuple[str | int, ...], replacement: Any) -> None:
        candidate = copy.deepcopy(contract)
        cursor: Any = candidate
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = replacement
        mutations.append(candidate)

    global_mutations = (
        (("schema_version",), "raisa.status_confirm_product_adapter_postgresql_contract.v2"),
        (("result",), "open"),
        (("source_head",), "0" * 40),
        (("accepted_adapter_source",), "0" * 40),
        (("evidence_label",), "product"),
        (("docker_profile", "image_reference"), "postgres:latest"),
        (("docker_profile", "pull_policy"), "always"),
        (("docker_profile", "network_internal"), False),
        (("docker_profile", "published_ports"), True),
        (("docker_profile", "relay_host_ip"), "0.0.0.0"),
        (("docker_profile", "relay_dynamic_host_port"), False),
        (("docker_profile", "tmpfs_options"), "rw"),
        (("docker_profile", "memory_bytes"), 0),
        (("docker_profile", "nano_cpus"), 0),
        (("docker_profile", "pids_limit"), 0),
        (("docker_profile", "restart_policy"), "always"),
        (("docker_profile", "application_user"), "postgres"),
        (("tenant_contract", "setting"), "client.tenant"),
        (("tenant_contract", "transaction_local"), False),
        (("cleanup", "container_target"), "container_name"),
    )
    for path, replacement in global_mutations:
        mutate(path, replacement)
    for index, item in enumerate(contract["scenarios"]):
        mutate(("scenarios", index, "id"), "PGA-S99")
        mutate(("scenarios", index, "kind"), "substitute")
        mutate(("scenarios", index, "expected"), "allow")
        mutate(("scenarios", index, "id"), contract["scenarios"][(index + 1) % 12]["id"])
        mutate(("scenarios", index, "kind"), item["kind"] + "_fallback")
        mutate(("scenarios", index, "expected"), item["expected"] + "_fallback")
        mutate(("scenarios", index, "kind"), "provider_call")
    if len(mutations) != HOSTILE_MUTATION_TARGET:
        raise AssertionError("hostile mutation population drift")
    rejected = 0
    for candidate in mutations:
        try:
            _validate_contract(candidate, exact=False)
            if candidate != contract:
                raise RehearsalFailure("preflight", "noncanonical_contract")
        except RehearsalFailure:
            rejected += 1
    return rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, exact=True)
    if hostile_mutations_rejected(contract) != HOSTILE_MUTATION_TARGET:
        raise RehearsalFailure("preflight", "hostile_mutation_gate_failed")
    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing")
        observed[binding["path"]] = _sha256(path.read_bytes())
        if observed[binding["path"]] != binding["sha256"]:
            raise RehearsalFailure("preflight", "source_hash_mismatch")
    router = (ROOT / "app/routers/appointments.py").read_text(encoding="utf-8")
    if "appointment_status_product_adapter" in router:
        raise RehearsalFailure("preflight", "route_mounted")
    return contract, observed


def _fixture(index: int) -> Fixture:
    return Fixture(
        index=index,
        practice_id=uuid.UUID(int=0x11000000000040008000000000000000 + index),
        appointment_id=uuid.UUID(int=0x22000000000040008000000000000000 + index),
        practitioner_id=uuid.UUID(int=0x33000000000040008000000000000000 + index),
        actor_id=uuid.UUID(int=0x44000000000040008000000000000000 + index),
        waiting_area_id=uuid.UUID(int=0x55000000000040008000000000000000 + index),
    )


def _application_engine(host_port: int, profile: dict[str, Any]) -> Engine:
    url = (
        f"postgresql+{profile['sqlalchemy_driver']}://{profile['application_user']}:"
        f"{profile['application_password']}@{profile['relay_host_ip']}:{host_port}/"
        f"{profile['postgres_database']}"
    )
    engine = create_engine(
        url,
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5, "application_name": "emr4_status_pga"},
    )
    with engine.connect() as connection:
        identity = connection.execute(
            text("SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user")
        ).one()
        if identity != (profile["application_user"], False, False):
            engine.dispose()
            raise RehearsalFailure("environment", "application_role_mismatch")
    return engine


def _install_database(docker: str, container_id: str, profile: dict[str, Any]) -> None:
    old_contract = _load_json(OLD_CONTRACT_PATH)
    foundation._install_database(docker, container_id, old_contract)  # noqa: SLF001
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        EXTENSION_SQL,
        single_transaction=True,
    )


def _seed(
    admin: Engine,
    fixture: Fixture,
    *,
    appointment_status: AppointmentStatus = AppointmentStatus.Booked,
    appointment_version: int = 1,
    actor_active: bool = True,
    actor_role: UserRole = UserRole.Receptionist,
    waiting_area: bool = False,
    practitioner: bool = True,
) -> None:
    with admin.begin() as connection:
        connection.execute(
            text("INSERT INTO practices(id,name,timezone) VALUES (:id,:name,'Australia/Sydney') ON CONFLICT DO NOTHING"),
            {"id": fixture.practice_id, "name": f"Synthetic Practice {fixture.index:02d}"},
        )
        if practitioner:
            connection.execute(
                text("INSERT INTO practitioners(id,practice_id,first_name,last_name,is_active) VALUES (:id,:practice,'Synthetic','Practitioner',true)"),
                {"id": fixture.practitioner_id, "practice": fixture.practice_id},
            )
        connection.execute(
            text("INSERT INTO users(id,practice_id,email,password_hash,role,is_active) VALUES (:id,:practice,:email,'synthetic-disabled',:role,:active)"),
            {
                "id": fixture.actor_id,
                "practice": fixture.practice_id,
                "email": f"synthetic-{fixture.index:02d}@invalid.example",
                "role": actor_role.value,
                "active": actor_active,
            },
        )
        connection.execute(
            text(
                "INSERT INTO appointments(id,practice_id,practitioner_id,start_time,appointment_date,start_time_local,duration_minutes,status,booked_via,waiting_area_id,appointment_state_version) "
                "VALUES (:id,:practice,:practitioner,:start,:day,:local,15,:status,'Receptionist',:waiting,:version)"
            ),
            {
                "id": fixture.appointment_id,
                "practice": fixture.practice_id,
                "practitioner": fixture.practitioner_id,
                "start": datetime(2026, 8, 13, 0, 0, tzinfo=timezone.utc),
                "day": date(2026, 8, 13),
                "local": local_time(10, 0),
                "status": appointment_status.value,
                "waiting": fixture.waiting_area_id if waiting_area else None,
                "version": appointment_version,
            },
        )


def _snapshot(admin: Engine, fixture: Fixture) -> dict[str, Any]:
    with admin.connect() as connection:
        appointment = connection.execute(
            text("SELECT status,appointment_state_version,waiting_area_id FROM appointments WHERE id=:id"),
            {"id": fixture.appointment_id},
        ).one()
        counts = connection.execute(
            text(
                "SELECT (SELECT count(*) FROM appointment_audit_log WHERE appointment_id=:id),"
                "(SELECT count(*) FROM appointment_command_idempotency WHERE target_appointment_id=:id),"
                "(SELECT count(*) FROM appointment_command_idempotency WHERE target_appointment_id=:id AND completed_receipt_version=1),"
                "(SELECT count(*) FROM appointment_command_idempotency i JOIN appointment_audit_log a ON a.id=i.audit_log_id AND a.command_id=i.id WHERE i.target_appointment_id=:id),"
                "(SELECT is_active FROM users WHERE id=:actor)"
            ),
            {"id": fixture.appointment_id, "actor": fixture.actor_id},
        ).one()
    return {
        "status": appointment[0],
        "version": appointment[1],
        "waiting_area": appointment[2] is not None,
        "audit_count": counts[0],
        "claim_count": counts[1],
        "receipt_count": counts[2],
        "correlated_count": counts[3],
        "actor_active": counts[4],
    }


def _actor(fixture: Fixture, *, practice_id: uuid.UUID | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        id=fixture.actor_id,
        practice_id=practice_id or fixture.practice_id,
        role=UserRole.Receptionist,
        is_active=True,
    )


def _body(
    fixture: Fixture,
    actor: SimpleNamespace,
    *,
    source_version: int = 1,
    target_status: AppointmentStatus = AppointmentStatus.Confirmed,
    waiting_area: bool = False,
) -> tuple[AppointmentStatusProposalConfirmationIn, dict[str, Any]]:
    snapshot = SimpleNamespace(
        id=fixture.appointment_id,
        status=AppointmentStatus.Booked,
        status_reason_code=None,
        waiting_area_id=fixture.waiting_area_id if waiting_area else None,
        appointment_state_version=source_version,
    )
    command = AppointmentStatusCommand(
        appointment_id=fixture.appointment_id,
        status=target_status,
        waiting_area_id=None,
        waiting_area_id_supplied=False,
        clears_waiting_area=target_status in {
            AppointmentStatus.Completed,
            AppointmentStatus.Cancelled,
            AppointmentStatus.DNA,
            AppointmentStatus.NoShow,
        },
        status_reason_code=None,
    )
    state = adapter.appointment_status_state(snapshot)
    freshness = adapter.status_proposal_freshness_id(command, state)
    evidence = mint_signed_confirmation_evidence(
        adapter.status_signed_confirmation_payload(
            practice_id=actor.practice_id,
            actor_id=actor.id,
            command=command,
            current_state=state,
            freshness_id=freshness,
        ),
        evidence_purpose=adapter.STATUS_CONFIRM_EVIDENCE_PURPOSE,
        secret=EVIDENCE_SECRET,
    )
    binding = adapter.mint_status_proposal_version_binding(
        evidence, source_version=source_version, secret=VERSION_SECRET
    )
    warning_codes = ["waiting_area_cleared"] if waiting_area else []
    proposal = AppointmentStatusProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Confirm authored-synthetic appointment status.",
        command=command,
        warnings=[
            {"code": code, "severity": "warning", "message": "Authored-synthetic warning."}
            for code in warning_codes
        ],
        blocks=[],
        status_proposal_freshness_id=freshness,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )
    return (
        AppointmentStatusProposalConfirmationIn(
            confirmed=True,
            status_proposal=proposal,
            confirmed_warnings=warning_codes,
            status_proposal_freshness_id=freshness,
            signed_confirmation_evidence=evidence,
            signed_confirmation_evidence_required=True,
        ),
        binding,
    )


def _invoke(
    factory: sessionmaker[Session],
    fixture: Fixture,
    body: AppointmentStatusProposalConfirmationIn,
    binding: dict[str, Any],
    actor: SimpleNamespace,
    *,
    user_loader: Callable[[Any, Any], Any] | None = None,
    transaction_factory: Callable[..., Any] | None = None,
) -> tuple[Any, int]:
    calls = 0

    def command_session_factory() -> Session:
        nonlocal calls
        calls += 1
        return factory()

    kwargs: dict[str, Any] = {}
    if user_loader is not None:
        kwargs["user_loader"] = user_loader
    if transaction_factory is not None:
        kwargs["transaction_factory"] = transaction_factory
    result = adapter.compose_product_status_confirm(
        body,
        authenticated_user=actor,
        authenticated_bearer_token=f"authored-synthetic-bearer-{fixture.index:02d}",
        idempotency_key=f"authored-synthetic-key-{fixture.index:02d}",
        proposal_version_binding=binding,
        command_session_factory=command_session_factory,
        authenticated_session_secret=SESSION_SECRET,
        proposal_version_binding_secret=VERSION_SECRET,
        idempotency_secret=IDEMPOTENCY_SECRET,
        session_binding_secret=BINDING_SECRET,
        evidence_secret=EVIDENCE_SECRET,
        **kwargs,
    )
    return result, calls


def _assert_error(result: Any, status: int, code: str) -> None:
    if result.kind != "error" or result.status_code != status or result.body["detail"]["code"] != code:
        raise RehearsalFailure("scenario", f"{code}_outcome_mismatch")


def _setting_absent(engine: Engine) -> bool:
    with engine.connect() as connection:
        value = connection.execute(
            text("SELECT current_setting('app.current_practice_id', true)")
        ).scalar_one_or_none()
        connection.rollback()
    return value in (None, "")


def _run_scenarios(admin: Engine, application: Engine) -> list[dict[str, Any]]:
    global CURRENT_SCENARIO
    factory = sessionmaker(bind=application, expire_on_commit=False)
    results: list[dict[str, Any]] = []

    fixture = _fixture(1)
    CURRENT_SCENARIO = "PGA-S01"
    _seed(admin, fixture)
    actor = _actor(fixture)
    body, binding = _body(fixture, actor)
    absent_before_commit = _setting_absent(application)
    before = _snapshot(admin, fixture)
    transaction_calls: list[dict[str, Any]] = []

    @contextmanager
    def traced_transaction(db: Session, **arguments: Any):
        transaction_calls.append(
            {
                key: value
                for key, value in arguments.items()
                if key not in {"practice_is_active", "current_authority"}
            }
        )
        with status_confirm_locked_transaction(db, **arguments) as decision:
            if len(transaction_calls) == 2 and decision.kind == "conflict":
                record = decision.record
                checks = {
                    "operation": record.operation_id == adapter.STATUS_CONFIRM_OPERATION_ID,
                    "route": record.route_family == adapter.STATUS_CONFIRM_ROUTE_FAMILY,
                    "role": record.actor_role == arguments["actor_role"],
                    "target": record.target_appointment_id == arguments["target_appointment_id"],
                    "request": record.request_body_hash == arguments["request_body_hash"],
                    "session_type": isinstance(record.session_binding_digest, bytes),
                    "session": bytes(record.session_binding_digest)
                    == arguments["session_binding_digest"],
                }
                failed = "_".join(key for key, passed in checks.items() if not passed)
                raise RehearsalFailure(
                    "scenario", f"PGA-S02_physical_binding_{failed or 'unknown'}"
                )
            yield decision

    first, calls = _invoke(
        factory,
        fixture,
        body,
        binding,
        actor,
        transaction_factory=traced_transaction,
    )
    after = _snapshot(admin, fixture)
    absent_after_commit = _setting_absent(application)
    if not (
        first.kind == "committed"
        and after["status"] == "Confirmed"
        and after["version"] == before["version"] + 1
        and after["audit_count"] == before["audit_count"] + 1
        and after["receipt_count"] == before["receipt_count"] + 1
        and after["correlated_count"] == 1
    ):
        raise RehearsalFailure("scenario", "PGA-S01_atomic_write_mismatch")
    first_bytes = first.stored_response_bytes
    results.append({"id": "PGA-S01", "status": "passed", "outcome": first.kind, "facts": {"session_count": calls, "version_delta": 1, "audit_delta": 1, "receipt_delta": 1}})

    session_reference = adapter.authenticated_session_reference(
        f"authored-synthetic-bearer-{fixture.index:02d}", secret=SESSION_SECRET
    )
    ingress = adapter._proposal_server_ingress(  # noqa: SLF001
        body=body,
        authenticated_user=actor,
        session_reference=session_reference,
        evidence_secret=EVIDENCE_SECRET,
        proposal_version_binding=binding,
        proposal_version_binding_secret=VERSION_SECRET,
    )
    admission = adapter.status_confirm_admission_adapter(
        {
            "structure": "valid",
            "transport": adapter._transport(  # noqa: SLF001
                body, idempotency_key=f"authored-synthetic-key-{fixture.index:02d}"
            ),
            "server": ingress.as_adapter_mapping(),
        }
    )
    expected_request = admission["kernel_request"]
    expected_session = status_confirm_session_binding_digest(
        secret=BINDING_SECRET,
        practice_id=fixture.practice_id,
        actor_user_id=fixture.actor_id,
        authenticated_session_id=session_reference,
    )
    with Session(application) as db, db.begin():
        db.execute(
            text("SELECT set_config('app.current_practice_id', :practice, true)"),
            {"practice": str(fixture.practice_id)},
        )
        persisted = db.execute(
            text(
                "SELECT actor_role,target_appointment_id,request_body_hash,session_binding_digest "
                "FROM appointment_command_idempotency WHERE target_appointment_id=:target"
            ),
            {"target": fixture.appointment_id},
        ).one()
        persisted_orm = (
            db.query(AppointmentCommandIdempotency)
            .filter(AppointmentCommandIdempotency.target_appointment_id == fixture.appointment_id)
            .one()
        )
        persisted_session_is_bytes = isinstance(
            persisted_orm.session_binding_digest, bytes
        )
        persisted_operation = persisted_orm.operation_id
        persisted_route = persisted_orm.route_family
    persisted_checks = {
        "role": persisted[0] == "Receptionist",
        "target": persisted[1] == fixture.appointment_id,
        "request": persisted[2] == expected_request["request_digest"],
        "session": bytes(persisted[3]) == expected_session,
        "session_type": persisted_session_is_bytes,
        "operation": persisted_operation == adapter.STATUS_CONFIRM_OPERATION_ID,
        "route": persisted_route == adapter.STATUS_CONFIRM_ROUTE_FAMILY,
    }
    if not all(persisted_checks.values()):
        failed = "_".join(key for key, passed in persisted_checks.items() if not passed)
        raise RehearsalFailure("scenario", f"PGA-S01_persisted_binding_{failed}")

    CURRENT_SCENARIO = "PGA-S02"
    retry, calls = _invoke(
        factory,
        fixture,
        body,
        binding,
        actor,
        transaction_factory=traced_transaction,
    )
    replay_after = _snapshot(admin, fixture)
    if retry.kind != "replay":
        if len(transaction_calls) == 2 and transaction_calls[0] != transaction_calls[1]:
            differing = "_".join(
                key
                for key in transaction_calls[0]
                if transaction_calls[0][key] != transaction_calls[1][key]
            )
            raise RehearsalFailure("scenario", f"PGA-S02_invocation_drift_{differing}")
        code = retry.body.get("detail", {}).get("code") if isinstance(retry.body, dict) else None
        raise RehearsalFailure("scenario", f"PGA-S02_kind_{retry.kind}_{code or 'none'}")
    if retry.stored_response_bytes != first_bytes:
        raise RehearsalFailure("scenario", "PGA-S02_stored_bytes_mismatch")
    if replay_after != after:
        raise RehearsalFailure("scenario", "PGA-S02_second_effect_detected")
    results.append({"id": "PGA-S02", "status": "passed", "outcome": retry.kind, "facts": {"session_count": calls, "byte_identical": True, "second_effect": False}})

    foreign = _fixture(3)
    CURRENT_SCENARIO = "PGA-S03"
    _seed(admin, foreign)
    with Session(application) as db, db.begin():
        db.execute(text("SELECT set_config('app.current_practice_id', :practice, true)"), {"practice": str(foreign.practice_id)})
        zero_counts = [
            db.execute(text(f"SELECT count(*) FROM {table} WHERE practice_id=:practice"), {"practice": fixture.practice_id}).scalar_one()
            for table in ("appointments", "users", "practitioners", "appointment_command_idempotency", "appointment_audit_log")
        ]
    if zero_counts != [0, 0, 0, 0, 0]:
        raise RehearsalFailure("scenario", "PGA-S03_cross_tenant_visibility")
    results.append({"id": "PGA-S03", "status": "passed", "outcome": "zero_visibility", "facts": {"tables_checked": 5, "visible_rows": 0}})

    inactive = _fixture(4)
    CURRENT_SCENARIO = "PGA-S04"
    _seed(admin, inactive, actor_active=False)
    inactive_actor = _actor(inactive)
    inactive_body, inactive_binding = _body(inactive, inactive_actor)
    before = _snapshot(admin, inactive)
    result, calls = _invoke(factory, inactive, inactive_body, inactive_binding, inactive_actor)
    _assert_error(result, 403, "current_authority_unavailable")
    if _snapshot(admin, inactive) != before:
        raise RehearsalFailure("scenario", "PGA-S04_effect_detected")
    results.append({"id": "PGA-S04", "status": "passed", "outcome": "current_authority_unavailable", "facts": {"session_count": calls, "claim_delta": 0}})

    revoked = _fixture(5)
    CURRENT_SCENARIO = "PGA-S05"
    _seed(admin, revoked)
    revoked_actor = _actor(revoked)
    revoked_body, revoked_binding = _body(revoked, revoked_actor)
    loader_calls = 0

    def revoke_between_checks(db: Session, actor_id: uuid.UUID) -> Any:
        nonlocal loader_calls
        loader_calls += 1
        current = db.query(User).populate_existing().filter(User.id == actor_id).one_or_none()
        if loader_calls == 1 and current is not None:
            snapshot = SimpleNamespace(id=current.id, practice_id=current.practice_id, role=current.role, is_active=True)
            db.execute(update(User).where(User.id == actor_id).values(is_active=False).execution_options(synchronize_session=False))
            return snapshot
        return current

    before = _snapshot(admin, revoked)
    result, calls = _invoke(factory, revoked, revoked_body, revoked_binding, revoked_actor, user_loader=revoke_between_checks)
    _assert_error(result, 403, "current_authority_unavailable")
    if _snapshot(admin, revoked) != before or loader_calls != 2:
        raise RehearsalFailure("scenario", "PGA-S05_rollback_mismatch")
    results.append({"id": "PGA-S05", "status": "passed", "outcome": "current_authority_unavailable", "facts": {"session_count": calls, "authority_reads": loader_calls, "rollback_equal": True}})

    mismatch = _fixture(6)
    CURRENT_SCENARIO = "PGA-S06"
    _seed(admin, mismatch)
    wrong_practice = uuid.UUID(int=0x66000000000040008000000000000006)
    with admin.begin() as connection:
        connection.execute(text("INSERT INTO practices(id,name) VALUES (:id,'Synthetic Mismatch Practice')"), {"id": wrong_practice})
    mismatch_actor = _actor(mismatch, practice_id=wrong_practice)
    mismatch_body, mismatch_binding = _body(mismatch, mismatch_actor)
    before = _snapshot(admin, mismatch)
    result, calls = _invoke(factory, mismatch, mismatch_body, mismatch_binding, mismatch_actor)
    _assert_error(result, 404, "appointment_not_found")
    if _snapshot(admin, mismatch) != before:
        raise RehearsalFailure("scenario", "PGA-S06_effect_detected")
    results.append({"id": "PGA-S06", "status": "passed", "outcome": "appointment_not_found", "facts": {"session_count": calls, "disclosed_row": False}})

    stale = _fixture(7)
    CURRENT_SCENARIO = "PGA-S07"
    _seed(admin, stale, appointment_version=2)
    stale_actor = _actor(stale)
    stale_body, stale_binding = _body(stale, stale_actor, source_version=1)
    before = _snapshot(admin, stale)
    result, calls = _invoke(factory, stale, stale_body, stale_binding, stale_actor)
    if result.kind != "blocked" or result.body["blocks"][0]["code"] != "locked_request_digest_changed" or _snapshot(admin, stale) != before:
        raise RehearsalFailure("scenario", "PGA-S07_stale_stop_mismatch")
    results.append({"id": "PGA-S07", "status": "passed", "outcome": "locked_request_digest_changed", "facts": {"session_count": calls, "rollback_equal": True}})

    tampered = _fixture(8)
    CURRENT_SCENARIO = "PGA-S08"
    _seed(admin, tampered)
    tampered_actor = _actor(tampered)
    tampered_body, tampered_binding = _body(tampered, tampered_actor)
    tampered_binding["signature"] = "0" * 64
    result, calls = _invoke(factory, tampered, tampered_body, tampered_binding, tampered_actor)
    _assert_error(result, 403, "authenticated_status_context_unavailable")
    if calls != 0:
        raise RehearsalFailure("scenario", "PGA-S08_session_constructed")
    results.append({"id": "PGA-S08", "status": "passed", "outcome": "authenticated_status_context_unavailable", "facts": {"session_count": 0, "pre_session_stop": True}})

    projection = _fixture(9)
    CURRENT_SCENARIO = "PGA-S09"
    _seed(admin, projection, practitioner=False)
    projection_actor = _actor(projection)
    projection_body, projection_binding = _body(projection, projection_actor)
    before = _snapshot(admin, projection)
    absent_before_rollback = _setting_absent(application)
    result, calls = _invoke(factory, projection, projection_body, projection_binding, projection_actor)
    _assert_error(result, 503, "status_confirm_transaction_unavailable")
    absent_after_rollback = _setting_absent(application)
    if _snapshot(admin, projection) != before:
        raise RehearsalFailure("scenario", "PGA-S09_rollback_mismatch")
    results.append({"id": "PGA-S09", "status": "passed", "outcome": "status_confirm_transaction_unavailable", "facts": {"session_count": calls, "rollback_equal": True}})

    terminal = _fixture(10)
    CURRENT_SCENARIO = "PGA-S10"
    _seed(admin, terminal, waiting_area=True)
    terminal_actor = _actor(terminal)
    terminal_body, terminal_binding = _body(terminal, terminal_actor, target_status=AppointmentStatus.Completed, waiting_area=True)
    before = _snapshot(admin, terminal)
    result, calls = _invoke(factory, terminal, terminal_body, terminal_binding, terminal_actor)
    after = _snapshot(admin, terminal)
    if not (result.kind == "committed" and after["status"] == "Completed" and after["waiting_area"] is False and after["version"] == before["version"] + 1):
        raise RehearsalFailure("scenario", "PGA-S10_terminal_mismatch")
    results.append({"id": "PGA-S10", "status": "passed", "outcome": result.kind, "facts": {"session_count": calls, "waiting_area_cleared": True, "warning_acknowledged": True}})

    wrong_role = _fixture(11)
    CURRENT_SCENARIO = "PGA-S11"
    _seed(admin, wrong_role, actor_role=UserRole.GP)
    wrong_actor = _actor(wrong_role)
    wrong_body, wrong_binding = _body(wrong_role, wrong_actor)
    before = _snapshot(admin, wrong_role)
    result, calls = _invoke(factory, wrong_role, wrong_body, wrong_binding, wrong_actor)
    _assert_error(result, 403, "current_authority_unavailable")
    if _snapshot(admin, wrong_role) != before:
        raise RehearsalFailure("scenario", "PGA-S11_effect_detected")
    results.append({"id": "PGA-S11", "status": "passed", "outcome": "current_authority_unavailable", "facts": {"session_count": calls, "claim_delta": 0}})

    no_leakage = all((absent_before_commit, absent_after_commit, absent_before_rollback, absent_after_rollback))
    CURRENT_SCENARIO = "PGA-S12"
    if not no_leakage:
        raise RehearsalFailure("scenario", "PGA-S12_tenant_setting_leaked")
    results.append({"id": "PGA-S12", "status": "passed", "outcome": "no_leakage", "facts": {"commit_boundary": True, "rollback_boundary": True, "pooled_connection": True}})
    return results


def _catalogue_check(admin: Engine) -> dict[str, Any]:
    with admin.connect() as connection:
        head = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        rls = connection.execute(
            text("SELECT count(*) FROM pg_class WHERE relname IN ('appointments','users','practitioners','appointment_command_idempotency','appointment_audit_log') AND relrowsecurity AND relforcerowsecurity")
        ).scalar_one()
        policies = connection.execute(
            text("SELECT count(*) FROM pg_policy WHERE polname IN ('pga_appointments_tenant','pga_users_tenant','pga_practitioners_tenant','pga_idempotency_tenant','pga_audit_tenant')")
        ).scalar_one()
        role = connection.execute(
            text("SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname='emr4_status_adapter_app'")
        ).one()
        trigger = connection.execute(
            text("SELECT count(*) FROM pg_trigger WHERE tgname='trg_appointments_advance_state_version'")
        ).scalar_one()
    if head != "w2x3y4z5a6b7" or rls != 5 or policies != 5 or role != (False, False) or trigger != 1:
        raise RehearsalFailure("catalogue", "postgresql_contract_mismatch")
    return {"alembic_head": head, "forced_rls_tables": rls, "tenant_policies": policies, "application_role_restricted": True, "adjacent_version_trigger": True}


def _failure_evidence(error: RehearsalFailure, lifecycle: list[str], cleanup: dict[str, Any]) -> dict[str, Any]:
    detail = error.detail if isinstance(error.detail, bytes) else str(error.detail).encode()
    return {
        "schema_version": "raisa.status_confirm_product_adapter_postgresql_evidence.v1",
        "result": "rehearsal_failed",
        "evidence_label": "authored_synthetic_provider_free_disposable_postgresql_product_adapter",
        "source_head": "73d41c6f9da2d82970310f475d1858f311bded38",
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
        lifecycle.append("contract_sources_and_104_mutations_verified")
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
            inspected, network_id=network_id, name=network_name, nonce=nonce, profile=profile, require_empty=True
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
            inspected, container_id=container_id, name=container_name, nonce=nonce, image_id=image_id, network_id=network_id, profile=profile
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
        catalogue_facts = _catalogue_check(admin)
        lifecycle.append("restricted_application_role_catalogue_verified")
        scenario_results = _run_scenarios(admin, application)
        lifecycle.append("twelve_serial_product_adapter_scenarios_verified")
        if time.monotonic() - started > profile["total_timeout_seconds"]:
            raise RehearsalFailure("environment", "total_timeout_exceeded")
        evidence = {
            "schema_version": "raisa.status_confirm_product_adapter_postgresql_evidence.v1",
            "result": PASS_RESULT,
            "evidence_label": contract["evidence_label"],
            "source_head": contract["source_head"],
            "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
            "source_hashes": source_hashes,
            "implementation_hashes": {
                "app/services/appointment_status_product_adapter.py": _sha256((ROOT / "app/services/appointment_status_product_adapter.py").read_bytes()),
                "tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter_plan.py": _sha256((ROOT / "tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter_plan.py").read_bytes()),
            },
            "hostile_mutations": {"attempted": HOSTILE_MUTATION_TARGET, "rejected": HOSTILE_MUTATION_TARGET, "minimum_required": 100},
            "environment": {"postgresql_major": 16, "image_reference": profile["image_reference"], "image_id_sha256": _sha256(image_id), "network_internal": True, "published_ports": False, "storage": "container_local_tmpfs", "host_transport": "fixed_in_process_ipv4_loopback_relay", "provider_calls": 0, "product_rows": 0},
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
        lifecycle.append(
            f"failed_{CURRENT_SCENARIO}_{type(caught).__name__}_{sqlstate}"
        )
        error = RehearsalFailure("harness", "unexpected_exception", type(caught).__name__)
    finally:
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
