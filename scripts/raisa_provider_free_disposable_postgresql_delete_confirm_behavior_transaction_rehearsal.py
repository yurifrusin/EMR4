"""Run the fixed provider-free delete-confirm PostgreSQL behavior/transaction rehearsal.

The harness accepts no caller-selected input. It operates one uniquely named,
labelled ``--internal``-network, tmpfs-backed local PostgreSQL 16 container
through a fixed in-process IPv4-loopback relay and removes only exact captured
IDs after ownership re-verification. It exercises the exact accepted
delete-confirm scaffold triggers and the exact unmounted
``delete_confirm_locked_transaction`` seam with fixed authored-synthetic serial
authority and transaction cases.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models.appointments import (
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentStatus,
)
from app.services import appointment_delete_physical as physical
from scripts import (
    raisa_provider_free_disposable_postgresql_delete_confirm_scaffold_parse_catalogue_rehearsal
    as catalogue,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as status_btr,
)


BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "delete-confirm-behavior-transaction-rehearsal"
)
CONTRACT_PATH = BASE / "rehearsal-contract.json"
SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = BASE / "provider-free-behavior-transaction-evidence.schema.json"
EVIDENCE_PATH = BASE / "provider-free-behavior-transaction-evidence.json"
FAILURE_EVIDENCE_PATH = BASE / "provider-free-behavior-transaction-failure-evidence.json"
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_delete_confirm_behavior_"
    "transaction_rehearsal_pass"
)
SOURCE_HEAD = "2a5042f80941e2bd191999c430ff2517ba7e8cb2"
EXPECTED_CONTRACT_DIGEST = (
    "53ec90e0193d85a7749a503b44c0952242c64b457f2eb581661833c1774b6944"
)
CLAIM_BOUNDARY = (
    "Exact serial unmounted SQLAlchemy/PostgreSQL delete-confirm authority and "
    "transaction behavior only; no route, product database, concurrency, restart, "
    "unknown commit, deployment or production claim."
)
FIXED_RELAY_COMMAND = (
    "exec 3<>/dev/tcp/127.0.0.1/5432; cat <&3 & cat >&3; wait"
)
GENERATION_MAX = 9223372036854775807

NEW_COMMAND_TOKENS = (
    "user_for_share",
    "appointment_for_update",
    "grant_authority_check",
    "idempotency_select_for_update",
    "idempotency_insert_on_conflict",
    "idempotency_winner_for_update",
    "grant_authority_check",
)
REPLAY_TOKENS = (
    "user_for_share",
    "appointment_for_update",
    "grant_authority_check",
    "idempotency_select_for_update",
    "grant_authority_check",
)
FIRST_AUTH_REVOKED_TOKENS = (
    "user_for_share",
    "appointment_for_update",
    "grant_authority_check",
)

AUTH_GROUP_IDS = tuple(f"AUTH-S{index:02d}" for index in range(1, 10))
TX_GROUP_IDS = tuple(f"TX-S{index:02d}" for index in range(1, 12))


BOOTSTRAP_SQL = r"""
CREATE TABLE public.practices (
  id uuid PRIMARY KEY, name varchar(255) NOT NULL, abn varchar(20),
  address_line1 varchar(255), address_line2 varchar(255),
  address_suburb varchar(100), address_state varchar(10),
  address_postcode varchar(10), phone varchar(20), email varchar(255),
  logo_url varchar(500), timezone varchar(50), hive_mind_opt_in boolean,
  practice_embedding text, specialty_tags jsonb, asgc_ra_code varchar(10),
  latitude double precision, longitude double precision,
  proda_device_cert_path varchar(500), proda_cert_expiry timestamptz,
  created_at timestamptz DEFAULT now()
);
CREATE TABLE public.users (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL,
  email varchar(255) NOT NULL, password_hash varchar(255) NOT NULL,
  role varchar(50) NOT NULL, practitioner_id uuid,
  is_active boolean DEFAULT true, created_at timestamptz DEFAULT now(),
  CONSTRAINT uq_btr_users_email UNIQUE (email),
  CONSTRAINT fk_btr_user_practice FOREIGN KEY (practice_id)
    REFERENCES public.practices(id)
);
CREATE TABLE public.appointments (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL, location_id uuid,
  patient_id uuid, patient_name_provisional varchar(200),
  practitioner_id uuid NOT NULL, appointment_type_id uuid, booked_by uuid,
  start_time timestamptz NOT NULL, appointment_date date NOT NULL,
  start_time_local time NOT NULL, duration_minutes integer DEFAULT 15,
  status text DEFAULT 'Booked', reason varchar(500), notes varchar(1000),
  cancellation_reason varchar(500), status_reason_code varchar(50),
  booked_via text DEFAULT 'Receptionist', waiting_room varchar(50),
  waiting_area_id uuid, queue_position integer, created_at timestamptz DEFAULT now(),
  appointment_state_version bigint DEFAULT 1,
  CONSTRAINT uq_appointments_practice_id_id UNIQUE (practice_id, id),
  CONSTRAINT ck_appointments_state_version_positive CHECK (appointment_state_version >= 1),
  CONSTRAINT fk_btr_appointment_practice FOREIGN KEY (practice_id)
    REFERENCES public.practices(id)
);
CREATE FUNCTION public.emr4_advance_appointment_state_version()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.appointment_state_version >= 9223372036854775807 THEN
    RAISE EXCEPTION 'appointment_state_version overflow' USING ERRCODE = '22003';
  END IF;
  NEW.appointment_state_version := OLD.appointment_state_version + 1;
  RETURN NEW;
END;
$$;
CREATE TRIGGER trg_appointments_advance_state_version
BEFORE UPDATE ON public.appointments FOR EACH ROW
EXECUTE FUNCTION public.emr4_advance_appointment_state_version();
CREATE TABLE public.appointment_command_idempotency (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL, actor_user_id varchar(64) NOT NULL,
  actor_role varchar(64) NOT NULL, operation_id varchar(100) NOT NULL,
  route_family varchar(100) NOT NULL, idempotency_key_hash varchar(128) NOT NULL,
  request_body_hash varchar(128) NOT NULL,
  request_body_canonicalization_version integer NOT NULL DEFAULT 1,
  state varchar(32) NOT NULL, response_status_code integer,
  response_body_hash varchar(128), response_body_json jsonb,
  result_kind varchar(50), target_appointment_id uuid, audit_log_id uuid,
  bernie_session_id varchar(64), created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(), expires_at timestamptz,
  confirmation_evidence_hash varchar(128),
  confirmation_evidence_consumed_at timestamptz,
  completed_receipt_version smallint,
  session_binding_digest bytea,
  pre_state_version bigint,
  post_state_version bigint,
  response_body_canonical_bytes bytea,
  CONSTRAINT uq_appt_cmd_idem_practice_id_id UNIQUE (practice_id, id),
  CONSTRAINT uq_appt_cmd_idem_practice_actor_operation_key UNIQUE
    (practice_id, actor_user_id, operation_id, idempotency_key_hash),
  CONSTRAINT ck_appt_cmd_idem_state CHECK
    (state IN ('in_progress', 'completed', 'failed_transient')),
  CONSTRAINT ck_appt_cmd_idem_completed_response CHECK
    (state != 'completed' OR (response_status_code IS NOT NULL AND
      response_body_hash IS NOT NULL AND response_body_json IS NOT NULL)),
  CONSTRAINT ck_appt_cmd_idem_completed_create_correlation CHECK
    (NOT (state = 'completed' AND operation_id IN
      ('confirmAppointmentCreateProposal', 'confirmAppointmentCheckInProposal')
      AND result_kind = 'confirmed_write') OR
      (target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL)),
  CONSTRAINT ck_appt_cmd_idem_completed_check_in_evidence CHECK
    (NOT (state = 'completed' AND operation_id =
      'confirmAppointmentCheckInProposal' AND result_kind = 'confirmed_write') OR
      (confirmation_evidence_hash IS NOT NULL AND
       confirmation_evidence_consumed_at IS NOT NULL)),
  CONSTRAINT ck_appt_cmd_idem_receipt_version CHECK
    (completed_receipt_version IS NULL OR completed_receipt_version = 1),
  CONSTRAINT ck_appt_cmd_idem_status_receipt_v1_complete CHECK
    (completed_receipt_version IS NULL OR
     (state = 'completed' AND
      operation_id = 'confirmAppointmentStatusProposal' AND
      route_family = 'status-confirm' AND
      result_kind = 'confirmed_write' AND
      session_binding_digest IS NOT NULL AND
      octet_length(session_binding_digest) = 32 AND
      pre_state_version IS NOT NULL AND pre_state_version >= 1 AND
      post_state_version IS NOT NULL AND
      post_state_version = pre_state_version + 1 AND
      response_body_canonical_bytes IS NOT NULL AND
      octet_length(response_body_canonical_bytes) > 0 AND
      target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND
      response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND
      response_body_json IS NOT NULL))
);
CREATE TABLE public.appointment_audit_log (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL, appointment_id uuid NOT NULL,
  confirmed_by_user_id uuid NOT NULL, action text NOT NULL,
  status_before text, status_after text, cancellation_reason varchar(500),
  status_reason_code varchar(50), confirmed_warnings jsonb, command_id uuid,
  bernie_session_id varchar(64), created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_appt_audit_log_practice_id_id UNIQUE (practice_id, id)
);
CREATE TABLE public.alembic_version (
  version_num varchar(32) NOT NULL PRIMARY KEY
);
INSERT INTO public.alembic_version(version_num) VALUES ('w2x3y4z5a6b7');
""".strip() + "\n"


CORRELATION_SQL = r"""
ALTER TABLE public.appointment_command_idempotency
  ADD CONSTRAINT fk_appt_cmd_idem_practice_target
  FOREIGN KEY (practice_id, target_appointment_id)
  REFERENCES public.appointments(practice_id, id);
ALTER TABLE public.appointment_audit_log
  ADD CONSTRAINT fk_appt_audit_log_practice_appointment
  FOREIGN KEY (practice_id, appointment_id)
  REFERENCES public.appointments(practice_id, id);
ALTER TABLE public.appointment_audit_log
  ADD CONSTRAINT fk_appt_audit_log_practice_command
  FOREIGN KEY (practice_id, command_id)
  REFERENCES public.appointment_command_idempotency(practice_id, id);
ALTER TABLE public.appointment_command_idempotency
  ADD CONSTRAINT fk_appt_cmd_idem_practice_audit
  FOREIGN KEY (practice_id, audit_log_id)
  REFERENCES public.appointment_audit_log(practice_id, id);
CREATE UNIQUE INDEX uq_appt_audit_log_command_id
  ON public.appointment_audit_log(command_id) WHERE command_id IS NOT NULL;
CREATE UNIQUE INDEX uq_appt_cmd_idem_audit_log_id
  ON public.appointment_command_idempotency(audit_log_id)
  WHERE audit_log_id IS NOT NULL;
""".strip() + "\n"


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: str | bytes = "") -> None:
        self.stage = stage
        self.code = code
        self.detail = detail.encode("utf-8") if isinstance(detail, str) else detail
        super().__init__(f"{stage}:{code}")


class OuterAbort(RuntimeError):
    pass


@dataclass(frozen=True)
class Fixture:
    index: int
    practice_id: UUID
    appointment_id: UUID
    actor_id: UUID
    actor_text: str
    audit_id: UUID
    idempotency_key_hash: str
    request_body_hash: str
    session_digest: bytes
    session_id: str
    signed_generation: int = 2


@dataclass(frozen=True)
class Invocation:
    outcome: str
    response_digest: str | None
    authority_calls: int
    statement_tokens: tuple[str, ...]


@dataclass(frozen=True)
class AuthResult:
    id: str
    generation: int | None
    grant_count: int
    subcases: tuple[dict[str, Any], ...] = ()


def _sha256(value: bytes | str) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def _canonical_digest(value: Any) -> str:
    return _sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sub_uuid(base: UUID, salt: int) -> UUID:
    return UUID(int=base.int + salt)


def _validate_contract(value: dict[str, Any], *, require_digest: bool) -> None:
    schema = _load_json(SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        raise RehearsalFailure("preflight", "contract_schema_invalid")
    if require_digest and _canonical_digest(value) != EXPECTED_CONTRACT_DIGEST:
        raise RehearsalFailure("preflight", "contract_digest_mismatch")
    if tuple(item["id"] for item in value["authority_groups"]) != AUTH_GROUP_IDS:
        raise RehearsalFailure("preflight", "authority_group_contract_mismatch")
    if tuple(item["id"] for item in value["transaction_groups"]) != TX_GROUP_IDS:
        raise RehearsalFailure("preflight", "transaction_group_contract_mismatch")
    if value["scenario_categories"] != {"authority": 9, "transaction": 11}:
        raise RehearsalFailure("preflight", "scenario_category_mismatch")
    if len({item["path"] for item in value["source_bindings"]}) != 16:
        raise RehearsalFailure("preflight", "source_binding_mismatch")


def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    """Return how many closed semantic mutations are rejected by the contract.

    Every mutation maps to a frozen threat in the plan's threat-model delta.
    """
    mutations: list[dict[str, Any]] = []

    def mutate(path: tuple[str | int, ...], replacement: Any) -> None:
        candidate = copy.deepcopy(contract)
        cursor: Any = candidate
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = replacement
        mutations.append(candidate)

    globals_to_mutate = (
        (("schema_version",), "raisa.delete_confirm_behavior_transaction_rehearsal.v2"),
        (("result",), "rehearsal_failed"),
        (("source_head",), "0" * 40),
        (("evidence_label",), "product"),
        (("alembic", "from_revision"), "x9y9z9a9b9c9"),
        (("alembic", "to_revision"), "w9x9y9z9a9b9"),
        (("alembic", "offline_range"), "x9y9z9a9b9c9:z9a9b9c9d9e9"),
        (("alembic", "synthetic_url"), "postgresql+psycopg://product:product@127.0.0.1:1/product"),
        (("docker_profile", "image_reference"), "postgres:latest"),
        (("docker_profile", "pull_policy"), "always"),
        (("docker_profile", "network_internal"), False),
        (("docker_profile", "published_ports"), True),
        (("docker_profile", "relay_host_ip"), "0.0.0.0"),
        (("docker_profile", "relay_dynamic_host_port"), False),
        (("docker_profile", "relay_container_command"), "cat"),
        (("docker_profile", "relay_container_executable"), "sh"),
        (("docker_profile", "sqlalchemy_driver"), "psycopg"),
        (("docker_profile", "tmpfs_options"), "rw"),
        (("docker_profile", "data_destination"), "/mnt/data"),
        (("docker_profile", "restart_policy"), "always"),
        (("docker_profile", "total_timeout_seconds"), 30),
        (("transaction_contract", "entry_point"), "substitute"),
        (("transaction_contract", "isolation"), "AUTOCOMMIT"),
        (("transaction_contract", "cumulative_deadline_ms"), 1500),
        (("transaction_contract", "lock_order"), list(reversed(contract["transaction_contract"]["lock_order"]))),
        (("transaction_contract", "effect_write_set"), ["appointment_mutation"]),
        (("transaction_contract", "response_source"), "public_response_envelope"),
        (("transaction_contract", "nested_transaction"), True),
        (("transaction_contract", "savepoint"), True),
        (("transaction_contract", "retry"), True),
        (("transaction_contract", "concurrency"), True),
        (("cleanup", "container_target"), "container_name"),
        (("cleanup", "network_target"), "captured_network_id_broad"),
        (("cleanup", "engine_relay_before_container"), False),
        (("cleanup", "post_remove_exact_id_absence_required"), False),
        (("scenario_categories", "authority"), 8),
        (("scenario_categories", "transaction"), 10),
        (("evidence_allowlist",), ["raw_sql", "credentials"]),
        (("forbidden", "existing_or_product_database_used"), True),
        (("forbidden", "external_network_used"), True),
        (("forbidden", "patient_product_or_protected_data_used"), True),
        (("forbidden", "provider_adc_credentials_or_browser_used"), True),
        (("forbidden", "protected_ref_moved"), True),
        (("next_candidate",), "product_deployment"),
    )
    for path, replacement in globals_to_mutate:
        mutate(path, replacement)

    added_url = copy.deepcopy(contract)
    added_url["caller_database_url"] = "postgresql://product"
    mutations.append(added_url)

    added_sql = copy.deepcopy(contract)
    added_sql["raw_sql_callback"] = True
    mutations.append(added_sql)

    extra_binding = copy.deepcopy(contract)
    extra_binding["source_bindings"].append(
        {"path": "alembic.ini", "sha256": "0" * 64}
    )
    mutations.append(extra_binding)

    removed_binding = copy.deepcopy(contract)
    removed_binding["source_bindings"].pop(0)
    mutations.append(removed_binding)

    for index in range(9):
        auth = contract["authority_groups"][index]
        mutate(("authority_groups", index, "id"), AUTH_GROUP_IDS[(index + 1) % 9])
        mutate(("authority_groups", index, "kind"), "invalid_kind")

    for index in range(11):
        tx = contract["transaction_groups"][index]
        mutate(("transaction_groups", index, "id"), TX_GROUP_IDS[(index + 1) % 11])
        mutate(("transaction_groups", index, "kind"), "invalid_kind")
        mutate(("transaction_groups", index, "expected"), "invalid_expected")
        mutate(("transaction_groups", index, "appointment_delta"), 2)
        mutate(("transaction_groups", index, "authority_calls"), tx["authority_calls"] + 9)

    if len(mutations) != HOSTILE_MUTATION_TARGET:
        raise AssertionError("hostile mutation population drift")
    rejected = 0
    for candidate in mutations:
        try:
            _validate_contract(candidate, require_digest=False)
        except RehearsalFailure:
            rejected += 1
    return rejected


HOSTILE_MUTATION_TARGET = 44 + 4 + 9 * 2 + 11 * 5


def verify_contract() -> tuple[dict[str, Any], dict[str, str]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, require_digest=True)
    if hostile_mutations_rejected(contract) != HOSTILE_MUTATION_TARGET:
        raise RehearsalFailure("preflight", "hostile_mutation_gate_failed")
    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing", binding["path"])
        digest = _sha256(path.read_bytes())
        observed[binding["path"]] = digest
        if digest != binding["sha256"]:
            raise RehearsalFailure(
                "preflight", "source_hash_mismatch", binding["path"]
            )
    return contract, observed


def _engine(host_port: int, profile: dict[str, Any]) -> Engine:
    url = (
        f"postgresql+{profile['sqlalchemy_driver']}://{profile['postgres_user']}:"
        f"{profile['postgres_password']}@{profile['relay_host_ip']}:{host_port}/"
        f"{profile['postgres_database']}"
    )
    engine = create_engine(
        url,
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5, "application_name": "emr4_delete_btr"},
    )
    with engine.connect() as connection:
        version = connection.execute(text("SHOW server_version_num")).scalar_one()
        if not str(version).startswith("16"):
            engine.dispose()
            raise RehearsalFailure("environment", "host_connection_version_mismatch")
    return engine


def _install_database(
    docker: str, container_id: str, contract: dict[str, Any]
) -> bytes:
    profile = contract["docker_profile"]
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        BOOTSTRAP_SQL,
        single_transaction=True,
    )
    offline_sql = catalogue._generate_offline_sql(contract)  # noqa: SLF001
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        offline_sql,
        single_transaction=True,
    )
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        CORRELATION_SQL,
        single_transaction=True,
    )
    return offline_sql


def _catalogue_check(engine: Engine) -> dict[str, Any]:
    with engine.connect() as connection:
        head = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        constraints = connection.execute(
            text(
                "SELECT count(*) FROM pg_constraint WHERE conname IN "
                "('fk_appt_cmd_idem_practice_target','fk_appt_audit_log_practice_appointment',"
                "'fk_appt_audit_log_practice_command','fk_appt_cmd_idem_practice_audit',"
                "'ck_appt_cmd_idem_status_receipt_v1_complete')"
            )
        ).scalar_one()
        indexes = connection.execute(
            text(
                "SELECT count(*) FROM pg_class WHERE relkind='i' AND relname IN "
                "('uq_appt_audit_log_command_id','uq_appt_cmd_idem_audit_log_id')"
            )
        ).scalar_one()
        triggers = connection.execute(
            text(
                "SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgname IN "
                "('trg_users_authority_generation_guard',"
                "'trg_user_capability_grants_generation',"
                "'trg_user_capability_grants_reject_update',"
                "'trg_appointments_advance_state_version')"
            )
        ).scalar_one()
    if head != "x3y4z5a6b7c8" or constraints != 5 or indexes != 2 or triggers != 4:
        raise RehearsalFailure("catalogue", "transaction_schema_mismatch")
    return {
        "head": head,
        "selected_constraints": constraints,
        "correlation_indexes": indexes,
        "trigger_inventory": triggers,
    }


def _fixture(index: int) -> Fixture:
    practice_id = UUID(int=0x10000000000040008000000000000000 + index)
    appointment_id = UUID(int=0x20000000000040008000000000000000 + index)
    actor_id = UUID(int=0x30000000000040008000000000000000 + index)
    session_id = f"synthetic-session-{index:02d}"
    actor_text = str(actor_id)
    return Fixture(
        index=index,
        practice_id=practice_id,
        appointment_id=appointment_id,
        actor_id=actor_id,
        actor_text=actor_text,
        audit_id=UUID(int=0x40000000000040008000000000000000 + index),
        idempotency_key_hash=_sha256(f"idempotency:{index}"),
        request_body_hash=_sha256(f"request:{index}"),
        session_digest=physical.delete_confirm_session_binding_digest(
            secret=b"delete-confirm-btr-synthetic-secret",
            practice_id=practice_id,
            actor_user_id=actor_text,
            authenticated_session_id=session_id,
        ),
        session_id=session_id,
    )


def _seed_base(
    engine: Engine,
    fixture: Fixture,
    *,
    with_grant: bool = True,
    appointment: bool = True,
    active: bool = True,
    role: str = "Receptionist",
    second_practice_id: UUID | None = None,
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO practices(id, name, timezone, hive_mind_opt_in) "
                "VALUES (:id, :name, 'Australia/Sydney', false)"
            ),
            {"id": fixture.practice_id, "name": f"Synthetic Practice {fixture.index:02d}"},
        )
        if second_practice_id is not None:
            connection.execute(
                text(
                    "INSERT INTO practices(id, name, timezone, hive_mind_opt_in) "
                    "VALUES (:id, :name, 'Australia/Sydney', false)"
                ),
                {
                    "id": second_practice_id,
                    "name": f"Synthetic Practice {fixture.index:02d} secondary",
                },
            )
        connection.execute(
            text(
                "INSERT INTO users(id, practice_id, email, password_hash, role, is_active) "
                "VALUES (:id, :practice_id, :email, :pw, :role, :active)"
            ),
            {
                "id": fixture.actor_id,
                "practice_id": fixture.practice_id,
                "email": f"synthetic-user-{fixture.index:02d}",
                "pw": "0" * 64,
                "role": role,
                "active": active,
            },
        )
        if appointment:
            connection.execute(
                text(
                    "INSERT INTO appointments(id, practice_id, practitioner_id, start_time, "
                    "appointment_date, start_time_local, duration_minutes, status, booked_via) "
                    "VALUES (:id, :practice_id, :practitioner_id, '2026-08-12 09:00:00+10', "
                    "'2026-08-12', '09:00:00', 15, 'Booked', 'Receptionist')"
                ),
                {
                    "id": fixture.appointment_id,
                    "practice_id": fixture.practice_id,
                    "practitioner_id": UUID(
                        int=0x50000000000040008000000000000000 + fixture.index
                    ),
                },
            )
        if with_grant:
            connection.execute(
                text(
                    "INSERT INTO user_capability_grants(practice_id, user_id, capability_code) "
                    "VALUES (:p, :u, 'appointment.cancel.confirm')"
                ),
                {"p": fixture.practice_id, "u": fixture.actor_id},
            )


def _seed_auth_partition(
    engine: Engine,
    fixture: Fixture,
    *,
    active: bool = True,
    role: str = "Receptionist",
    actor_id: UUID | None = None,
    practice_id: UUID | None = None,
) -> None:
    user_id = actor_id or fixture.actor_id
    practice = practice_id or fixture.practice_id
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO practices(id, name, timezone, hive_mind_opt_in) "
                "VALUES (:id, :name, 'Australia/Sydney', false)"
            ),
            {"id": practice, "name": f"Synthetic Practice {fixture.index:02d}"},
        )
        connection.execute(
            text(
                "INSERT INTO users(id, practice_id, email, password_hash, role, is_active) "
                "VALUES (:id, :practice_id, :email, :pw, :role, :active)"
            ),
            {
                "id": user_id,
                "practice_id": practice,
                "email": f"synthetic-user-{user_id.int:x}",
                "pw": "0" * 64,
                "role": role,
                "active": active,
            },
        )


def _auth_snapshot(engine: Engine, fixture: Fixture) -> dict[str, Any]:
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT authority_generation FROM users WHERE practice_id=:p AND id=:u"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        ).one_or_none()
        grant_count = connection.execute(
            text(
                "SELECT count(*) FROM user_capability_grants WHERE practice_id=:p AND user_id=:u"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        ).scalar_one()
    return {
        "generation": row[0] if row is not None else None,
        "grant_count": grant_count,
    }


def _pgcode(exc: Exception) -> str:
    origin = getattr(exc, "orig", None)
    code = getattr(origin, "pgcode", None)
    if isinstance(code, str) and len(code) == 5 and code.isalnum():
        return code
    raise RehearsalFailure("auth", "sqlstate_unavailable")


def _expect_pgcode(action, expected: str) -> None:
    try:
        action()
    except Exception as exc:  # noqa: BLE001 - bounded SQLSTATE extraction only
        if _pgcode(exc) != expected:
            raise RehearsalFailure("auth", "sqlstate_mismatch", _pgcode(exc)) from None
        return
    raise RehearsalFailure("auth", "expected_sql_failure_missing")


def _force_authority_generation_max(engine: Engine, fixture: Fixture) -> None:
    """Fixed fixture-only probe setup: move one synthetic user to BIGINT max.

    The accepted triggers deliberately reject direct generation writes, so the
    only way to reach the overflow boundary is to suspend trigger firing for one
    session-scoped fixture UPDATE. This is not a durable grant, schema change,
    product path or caller surface; it is the exact frozen AUTH-S08 setup.
    """
    with engine.begin() as connection:
        connection.execute(text("SET session_replication_role = replica"))
        connection.execute(
            text(
                "UPDATE public.users SET authority_generation = :max "
                "WHERE practice_id=:p AND id=:u"
            ),
            {
                "max": GENERATION_MAX,
                "p": fixture.practice_id,
                "u": fixture.actor_id,
            },
        )
        connection.execute(text("SET session_replication_role = origin"))


def _statement_token(statement: str) -> str | None:
    normalized = " ".join(statement.lower().replace('"', "").split())
    if " from users " in f" {normalized} " and " for share" in normalized:
        return "user_for_share"
    if " from appointments " in f" {normalized} " and " for update" in normalized:
        return "appointment_for_update"
    if (
        " from user_capability_grants " in f" {normalized} "
        and "exists" in normalized
    ):
        return "grant_authority_check"
    if (
        "insert into appointment_command_idempotency" in normalized
        and "on conflict" in normalized
    ):
        return "idempotency_insert_on_conflict"
    if (
        " from appointment_command_idempotency " in f" {normalized} "
        and " for update" in normalized
    ):
        return "idempotency_for_update"
    return None


def _snapshot(engine: Engine, fixture: Fixture) -> dict[str, Any]:
    with engine.connect() as connection:
        appointment = connection.execute(
            text(
                "SELECT status, appointment_state_version FROM appointments "
                "WHERE practice_id=:p AND id=:a"
            ),
            {"p": fixture.practice_id, "a": fixture.appointment_id},
        ).one_or_none()
        params = {"p": fixture.practice_id, "a": fixture.appointment_id}
        audit_count = connection.execute(
            text(
                "SELECT count(*) FROM appointment_audit_log "
                "WHERE practice_id=:p AND appointment_id=:a"
            ),
            params,
        ).scalar_one()
        idempotency_rows = connection.execute(
            text(
                "SELECT count(*) FROM appointment_command_idempotency "
                "WHERE practice_id=:p AND target_appointment_id=:a"
            ),
            params,
        ).scalar_one()
        complete_count = connection.execute(
            text(
                "SELECT count(*) FROM appointment_command_idempotency "
                "WHERE practice_id=:p AND target_appointment_id=:a "
                "AND completed_receipt_version=1 AND route_family='delete-confirm'"
            ),
            params,
        ).scalar_one()
        correlated = connection.execute(
            text(
                "SELECT count(*) FROM appointment_command_idempotency i "
                "JOIN appointment_audit_log a ON a.id=i.audit_log_id AND a.command_id=i.id "
                "AND a.practice_id=i.practice_id "
                "WHERE i.practice_id=:p AND i.target_appointment_id=:a AND a.appointment_id=:a"
            ),
            params,
        ).scalar_one()
    return {
        "status": appointment[0] if appointment is not None else None,
        "version": appointment[1] if appointment is not None else None,
        "audit_count": audit_count,
        "idempotency_rows": idempotency_rows,
        "completed_v1_count": complete_count,
        "correlated_count": correlated,
    }


def _insert_grant(
    engine: Engine,
    fixture: Fixture,
    *,
    capability: str = "appointment.cancel.confirm",
    user_id: UUID | None = None,
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO user_capability_grants(practice_id, user_id, capability_code) "
                "VALUES (:p, :u, :c)"
            ),
            {
                "p": fixture.practice_id,
                "u": user_id or fixture.actor_id,
                "c": capability,
            },
        )


def _insert_grant_on_conflict_nothing(engine: Engine, fixture: Fixture) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO user_capability_grants(practice_id, user_id, capability_code) "
                "VALUES (:p, :u, 'appointment.cancel.confirm') ON CONFLICT DO NOTHING"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        )


def _update_grant(engine: Engine, fixture: Fixture) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE user_capability_grants SET capability_code='appointment.read' "
                "WHERE practice_id=:p AND user_id=:u"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        )


def _update_user_role(engine: Engine, fixture: Fixture, role: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE users SET role=:role WHERE practice_id=:p AND id=:u"),
            {"role": role, "p": fixture.practice_id, "u": fixture.actor_id},
        )


def _run_auth_case(
    engine: Engine, group: dict[str, Any], index: int
) -> AuthResult:
    kind = group["kind"]
    if kind == "insert_forces_generation_one":
        return _auth_s01(engine, group, index)
    if kind == "qualifying_changes_advance_once":
        return _auth_s02(engine, group, index)
    if kind == "grant_insert_advances_parent":
        return _auth_s03(engine, group, index)
    if kind == "duplicate_grant_does_not_advance":
        return _auth_s04(engine, group, index)
    if kind == "grant_delete_restores_denial":
        return _auth_s05(engine, group, index)
    if kind == "grant_update_rejected":
        return _auth_s06(engine, group, index)
    if kind == "unknown_capability_or_missing_parent_fails":
        return _auth_s07(engine, group, index)
    if kind == "generation_maximum_overflow":
        return _auth_s08(engine, group, index)
    if kind == "reassignment_delete_then_insert":
        return _auth_s09(engine, group, index)
    raise RehearsalFailure("auth", "unknown_auth_group", group["id"])


def _auth_s01(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    user2 = _sub_uuid(fixture.actor_id, 1)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users(id, practice_id, email, password_hash, role, is_active, "
                "authority_generation) VALUES (:id, :p, :email, :pw, 'Receptionist', true, 5)"
            ),
            {
                "id": user2,
                "p": fixture.practice_id,
                "email": f"synthetic-user-{user2.int:x}",
                "pw": "0" * 64,
            },
        )
    with engine.connect() as connection:
        after_insert = connection.execute(
            text("SELECT authority_generation FROM users WHERE id=:u"),
            {"u": user2},
        ).scalar_one()
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE users SET authority_generation = 10 WHERE practice_id=:p AND id=:u"),
            {"p": fixture.practice_id, "u": user2},
        )
    with engine.connect() as connection:
        after_update = connection.execute(
            text("SELECT authority_generation FROM users WHERE id=:u"),
            {"u": user2},
        ).scalar_one()
    if after_insert != 1 or after_update != 1:
        raise RehearsalFailure("auth", "AUTH-S01_generation_not_forced")
    return AuthResult(group["id"], generation=after_update, grant_count=0)


def _auth_s02(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    second_practice = _sub_uuid(fixture.practice_id, 0x10)
    role_user = _sub_uuid(fixture.actor_id, 1)
    active_user = _sub_uuid(fixture.actor_id, 2)
    practice_user = _sub_uuid(fixture.actor_id, 3)
    unrelated_user = _sub_uuid(fixture.actor_id, 4)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO practices(id, name, timezone, hive_mind_opt_in) "
                "VALUES (:id, :name, 'Australia/Sydney', false)"
            ),
            {"id": second_practice, "name": f"Synthetic Practice {index:02d} secondary"},
        )
        for uid in (role_user, active_user, practice_user, unrelated_user):
            connection.execute(
                text(
                    "INSERT INTO users(id, practice_id, email, password_hash, role, is_active) "
                    "VALUES (:id, :p, :email, :pw, 'Receptionist', true)"
                ),
                {
                    "id": uid,
                    "p": fixture.practice_id,
                    "email": f"synthetic-user-{uid.int:x}",
                    "pw": "0" * 64,
                },
            )
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE users SET role='Nurse' WHERE practice_id=:p AND id=:u"),
            {"p": fixture.practice_id, "u": role_user},
        )
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE users SET is_active=false WHERE practice_id=:p AND id=:u"),
            {"p": fixture.practice_id, "u": active_user},
        )
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE users SET practice_id=:p2 WHERE practice_id=:p AND id=:u"),
            {"p2": second_practice, "p": fixture.practice_id, "u": practice_user},
        )
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE users SET email='synthetic-user-renamed' WHERE practice_id=:p AND id=:u"),
            {"p": fixture.practice_id, "u": unrelated_user},
        )
    with engine.connect() as connection:
        role_gen = connection.execute(
            text("SELECT authority_generation FROM users WHERE id=:u"), {"u": role_user}
        ).scalar_one()
        active_gen = connection.execute(
            text("SELECT authority_generation FROM users WHERE id=:u"), {"u": active_user}
        ).scalar_one()
        practice_gen = connection.execute(
            text("SELECT authority_generation FROM users WHERE id=:u"), {"u": practice_user}
        ).scalar_one()
        unrelated_gen = connection.execute(
            text("SELECT authority_generation FROM users WHERE id=:u"), {"u": unrelated_user}
        ).scalar_one()
    if (role_gen, active_gen, practice_gen, unrelated_gen) != (2, 2, 2, 1):
        raise RehearsalFailure("auth", "AUTH-S02_advance_mismatch")
    subcases = (
        {"id": "role", "label": "role_change", "generation": role_gen, "grant_count": 0},
        {"id": "active", "label": "active_state_change", "generation": active_gen, "grant_count": 0},
        {"id": "practice", "label": "practice_membership_change", "generation": practice_gen, "grant_count": 0},
        {"id": "unrelated", "label": "unrelated_update", "generation": unrelated_gen, "grant_count": 0},
    )
    return AuthResult(group["id"], generation=unrelated_gen, grant_count=0, subcases=subcases)


def _auth_s03(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    before = _auth_snapshot(engine, fixture)
    if before["grant_count"] != 0:
        raise RehearsalFailure("auth", "AUTH-S03_default_denial_missing")
    _insert_grant(engine, fixture)
    after = _auth_snapshot(engine, fixture)
    if after["generation"] != before["generation"] + 1 or after["grant_count"] != 1:
        raise RehearsalFailure("auth", "AUTH-S03_advance_mismatch")
    return AuthResult(group["id"], generation=after["generation"], grant_count=after["grant_count"])


def _auth_s04(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    _insert_grant(engine, fixture)
    before = _auth_snapshot(engine, fixture)
    _expect_pgcode(lambda: _insert_grant(engine, fixture), "23505")
    _insert_grant_on_conflict_nothing(engine, fixture)
    after = _auth_snapshot(engine, fixture)
    if after != before:
        raise RehearsalFailure("auth", "AUTH-S04_duplicate_advanced")
    return AuthResult(group["id"], generation=after["generation"], grant_count=after["grant_count"])


def _auth_s05(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    _insert_grant(engine, fixture)
    before = _auth_snapshot(engine, fixture)
    with engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM user_capability_grants WHERE practice_id=:p AND user_id=:u "
                "AND capability_code='appointment.cancel.confirm'"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        )
    after = _auth_snapshot(engine, fixture)
    if after["generation"] != before["generation"] + 1 or after["grant_count"] != 0:
        raise RehearsalFailure("auth", "AUTH-S05_delete_advance_mismatch")
    return AuthResult(group["id"], generation=after["generation"], grant_count=after["grant_count"])


def _auth_s06(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    _insert_grant(engine, fixture)
    before = _auth_snapshot(engine, fixture)
    _expect_pgcode(lambda: _update_grant(engine, fixture), "55000")
    after = _auth_snapshot(engine, fixture)
    if after != before:
        raise RehearsalFailure("auth", "AUTH-S06_update_mutated")
    with engine.connect() as connection:
        code = connection.execute(
            text(
                "SELECT capability_code FROM user_capability_grants "
                "WHERE practice_id=:p AND user_id=:u"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        ).scalar_one()
    if code != "appointment.cancel.confirm":
        raise RehearsalFailure("auth", "AUTH-S06_identity_mutated")
    return AuthResult(group["id"], generation=after["generation"], grant_count=after["grant_count"])


def _auth_s07(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    before = _auth_snapshot(engine, fixture)
    _expect_pgcode(
        lambda: _insert_grant(engine, fixture, capability="unknown.capability"), "23514"
    )
    missing_parent = UUID(int=0x70000000000040008000000000000000 + index)
    _expect_pgcode(
        lambda: _insert_grant(engine, fixture, user_id=missing_parent), "23503"
    )
    after = _auth_snapshot(engine, fixture)
    if after != before:
        raise RehearsalFailure("auth", "AUTH-S07_partial_survived")
    return AuthResult(group["id"], generation=after["generation"], grant_count=after["grant_count"])


def _auth_s08(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    _force_authority_generation_max(engine, fixture)
    _expect_pgcode(lambda: _update_user_role(engine, fixture, "GP"), "22003")
    after_role = _auth_snapshot(engine, fixture)
    if after_role["generation"] != GENERATION_MAX:
        raise RehearsalFailure("auth", "AUTH-S08_wrapped")
    _expect_pgcode(lambda: _insert_grant(engine, fixture), "22003")
    after_grant = _auth_snapshot(engine, fixture)
    if after_grant["generation"] != GENERATION_MAX or after_grant["grant_count"] != 0:
        raise RehearsalFailure("auth", "AUTH-S08_partial_effect")
    return AuthResult(group["id"], generation=GENERATION_MAX, grant_count=0)


def _auth_s09(engine: Engine, group: dict[str, Any], index: int) -> AuthResult:
    fixture = _fixture(index)
    _seed_auth_partition(engine, fixture)
    _insert_grant(engine, fixture, capability="appointment.read")
    before = _auth_snapshot(engine, fixture)
    with engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM user_capability_grants WHERE practice_id=:p AND user_id=:u "
                "AND capability_code='appointment.read'"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        )
    mid = _auth_snapshot(engine, fixture)
    _insert_grant(engine, fixture, capability="appointment.cancel.confirm")
    after = _auth_snapshot(engine, fixture)
    if mid["generation"] != before["generation"] + 1:
        raise RehearsalFailure("auth", "AUTH-S09_delete_advance_mismatch")
    if after["generation"] != mid["generation"] + 1:
        raise RehearsalFailure("auth", "AUTH-S09_insert_advance_mismatch")
    if after["grant_count"] != 1:
        raise RehearsalFailure("auth", "AUTH-S09_identity_mismatch")
    with engine.connect() as connection:
        code = connection.execute(
            text(
                "SELECT capability_code FROM user_capability_grants "
                "WHERE practice_id=:p AND user_id=:u"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        ).scalar_one()
    if code != "appointment.cancel.confirm":
        raise RehearsalFailure("auth", "AUTH-S09_identity_not_reassigned")
    return AuthResult(group["id"], generation=after["generation"], grant_count=after["grant_count"])


def _seed_classification(engine: Engine, fixture: Fixture, kind: str) -> None:
    command_id = UUID(int=0x60000000000040008000000000000000 + fixture.index)
    base = {
        "id": command_id,
        "practice": fixture.practice_id,
        "actor": fixture.actor_text,
        "key": fixture.idempotency_key_hash,
        "request": fixture.request_body_hash,
        "target": fixture.appointment_id,
        "session_digest": fixture.session_digest,
    }
    with engine.begin() as connection:
        if kind == "in_progress":
            connection.execute(
                text(
                    "INSERT INTO appointment_command_idempotency(id, practice_id, actor_user_id, "
                    "actor_role, operation_id, route_family, idempotency_key_hash, request_body_hash, "
                    "state, target_appointment_id, session_binding_digest, authority_generation) "
                    "VALUES (:id, :practice, :actor, 'Receptionist', 'confirmAppointmentDeleteProposal', "
                    "'delete-confirm', :key, :request, 'in_progress', :target, :session_digest, 2)"
                ),
                base,
            )
            return
        if kind == "legacy":
            connection.execute(
                text(
                    "INSERT INTO appointment_command_idempotency(id, practice_id, actor_user_id, "
                    "actor_role, operation_id, route_family, idempotency_key_hash, request_body_hash, "
                    "state, target_appointment_id, session_binding_digest, authority_generation, "
                    "response_status_code, response_body_hash, response_body_json, result_kind) "
                    "VALUES (:id, :practice, :actor, 'Receptionist', 'confirmAppointmentDeleteProposal', "
                    "'delete-confirm', :key, :request, 'completed', :target, :session_digest, 2, 200, "
                    ":hash, '{}'::jsonb, 'legacy_result')"
                ),
                {**base, "hash": "0" * 64},
            )
            return
        if kind != "corrupt":
            raise AssertionError("unknown classification seed")
        response_bytes = physical.canonical_delete_confirm_response_bytes(
            appointment_id=fixture.appointment_id,
            status_reason_code="PATIENT_CANCELLED",
            cancellation_reason=None,
            warning_codes=["synthetic-warning-01"],
        )
        connection.execute(
            text(
                "INSERT INTO appointment_command_idempotency(id, practice_id, actor_user_id, "
                "actor_role, operation_id, route_family, idempotency_key_hash, request_body_hash, "
                "state, target_appointment_id, session_binding_digest, authority_generation) "
                "VALUES (:id, :practice, :actor, 'Receptionist', 'confirmAppointmentDeleteProposal', "
                "'delete-confirm', :key, :request, 'in_progress', :target, :session_digest, 2)"
            ),
            base,
        )
        connection.execute(
            text(
                "INSERT INTO appointment_audit_log(id, practice_id, appointment_id, "
                "confirmed_by_user_id, action, status_before, status_after, cancellation_reason, "
                "status_reason_code, confirmed_warnings, command_id, audit_contract_version, "
                "authority_generation, pre_state_version, post_state_version, waiting_area_after_id, "
                "audit_evidence_codes) VALUES (:audit, :practice, :target, :actor_uuid, 'delete', "
                "'Booked', 'Cancelled', NULL, 'PATIENT_CANCELLED', '[\"synthetic-warning-01\"]'::jsonb, "
                ":id, 1, 2, 1, 2, NULL, '[\"delete-confirm\", \"synthetic-audit-01\"]'::jsonb)"
            ),
            {
                **base,
                "audit": fixture.audit_id,
                "actor_uuid": fixture.actor_id,
            },
        )
        connection.execute(
            text(
                "UPDATE appointment_command_idempotency SET state='completed', "
                "response_status_code=200, response_body_hash=:bad_hash, "
                "response_body_json=CAST(:body AS jsonb), result_kind='confirmed_write', "
                "audit_log_id=:audit, completed_receipt_version=1, pre_state_version=1, "
                "post_state_version=2, response_body_canonical_bytes=:bytes WHERE id=:id"
            ),
            {
                **base,
                "bad_hash": "0" * 64,
                "body": response_bytes.decode("utf-8"),
                "audit": fixture.audit_id,
                "bytes": response_bytes,
            },
        )


def _stage_audit(
    db: Session,
    decision: physical.DeleteConfirmPhysicalDecision,
    fixture: Fixture,
    *,
    signed_generation: int,
) -> AppointmentAuditLog:
    audit = AppointmentAuditLog(
        id=fixture.audit_id,
        practice_id=fixture.practice_id,
        appointment_id=fixture.appointment_id,
        confirmed_by_user_id=fixture.actor_id,
        action=AppointmentAuditAction.delete,
        status_before=AppointmentStatus.Booked,
        status_after=AppointmentStatus.Cancelled,
        cancellation_reason=None,
        status_reason_code="PATIENT_CANCELLED",
        confirmed_warnings=["synthetic-warning-01"],
        command_id=decision.record.id,
        audit_contract_version=1,
        authority_generation=signed_generation,
        pre_state_version=decision.pre_state_version,
        post_state_version=decision.appointment.appointment_state_version,
        waiting_area_before_id=None,
        waiting_area_after_id=None,
        audit_evidence_codes=["delete-confirm", "synthetic-audit-01"],
    )
    db.add(audit)
    return audit


def _stage_complete(
    db: Session,
    decision: physical.DeleteConfirmPhysicalDecision,
    fixture: Fixture,
    *,
    signed_generation: int,
) -> bytes:
    decision.appointment.status = AppointmentStatus.Cancelled
    decision.appointment.status_reason_code = "PATIENT_CANCELLED"
    decision.appointment.cancellation_reason = None
    decision.appointment.waiting_area_id = None
    db.flush()
    db.refresh(decision.appointment)
    audit = _stage_audit(db, decision, fixture, signed_generation=signed_generation)
    db.flush()
    response_bytes = physical.canonical_delete_confirm_response_bytes(
        appointment_id=fixture.appointment_id,
        status_reason_code="PATIENT_CANCELLED",
        cancellation_reason=None,
        warning_codes=["synthetic-warning-01"],
    )
    record = decision.record
    record.state = "completed"
    record.response_status_code = 200
    record.response_body_hash = physical.delete_confirm_response_digest(response_bytes)
    record.response_body_json = json.loads(response_bytes.decode("utf-8"))
    record.result_kind = "confirmed_write"
    record.audit_log_id = audit.id
    record.completed_receipt_version = 1
    record.pre_state_version = decision.pre_state_version
    record.post_state_version = decision.appointment.appointment_state_version
    record.response_body_canonical_bytes = response_bytes
    db.flush()
    return response_bytes


def _assert_token_order(outcome: str, tokens: tuple[str, ...]) -> None:
    if outcome == "new_command":
        expected = NEW_COMMAND_TOKENS
    elif outcome in (
        "replay",
        "conflict",
        "in_progress_not_replayable",
        "legacy_receipt_not_replayable",
        "receipt_integrity_failure",
    ):
        expected = REPLAY_TOKENS
    elif outcome == "authority_revoked":
        if len(tokens) == len(NEW_COMMAND_TOKENS):
            expected = NEW_COMMAND_TOKENS
        elif len(tokens) == len(REPLAY_TOKENS):
            expected = REPLAY_TOKENS
        else:
            expected = FIRST_AUTH_REVOKED_TOKENS
    elif outcome == "target_unavailable":
        expected = (
            ("user_for_share", "appointment_for_update")
            if len(tokens) == 2
            else ("user_for_share",)
        )
    elif outcome == "wait_budget_exhausted":
        expected = ("user_for_share",)
    elif outcome in ("scaffold_incomplete", "outer_abort"):
        expected = NEW_COMMAND_TOKENS
    else:
        raise RehearsalFailure("transaction", "unknown_token_outcome")
    if tokens != expected:
        raise RehearsalFailure("transaction", "lock_authority_order_mismatch")


def _invoke_tx(
    engine: Engine,
    fixture: Fixture,
    *,
    action: str = "none",
    signed_generation: int | None = None,
    request_body_hash: str | None = None,
    session_digest: bytes | None = None,
    actor_role: str = "Receptionist",
    revoke_second_check: bool = False,
    clock_exhaust: bool = False,
) -> Invocation:
    tokens: list[str] = []
    authority_calls = 0
    inserted_seen = False
    response_bytes: bytes | None = None
    outcome = "unknown"
    original_monotonic = physical.time.monotonic
    effective_generation = (
        signed_generation if signed_generation is not None else fixture.signed_generation
    )

    def observe(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
        nonlocal inserted_seen, authority_calls
        token = _statement_token(statement)
        if token == "idempotency_for_update":
            token = (
                "idempotency_winner_for_update"
                if inserted_seen
                else "idempotency_select_for_update"
            )
        if token is not None:
            tokens.append(token)
            if token == "idempotency_insert_on_conflict":
                inserted_seen = True
            elif token == "grant_authority_check":
                authority_calls += 1

    def revoke_hook(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
        # The winner FOR UPDATE is the second idempotency FOR UPDATE (after the
        # only-if-absent insert); the statement token is the raw class token.
        if _statement_token(statement) == "idempotency_for_update" and inserted_seen:
            _conn.execute(
                text(
                    "DELETE FROM user_capability_grants WHERE practice_id=:p AND user_id=:u "
                    "AND capability_code='appointment.cancel.confirm'"
                ),
                {"p": fixture.practice_id, "u": fixture.actor_id},
            )

    event.listen(engine, "before_cursor_execute", observe)
    if revoke_second_check:
        event.listen(engine, "after_cursor_execute", revoke_hook)
    try:
        if clock_exhaust:
            counter = [0]

            def fake_monotonic() -> float:
                counter[0] += 1
                return 0.0 if counter[0] <= 2 else 100.0

            physical.time.monotonic = fake_monotonic
        with Session(engine, expire_on_commit=False) as db:
            with physical.delete_confirm_locked_transaction(
                db,
                practice_id=fixture.practice_id,
                target_appointment_id=fixture.appointment_id,
                actor_user_id=fixture.actor_text,
                actor_role=actor_role,
                idempotency_key_hash=fixture.idempotency_key_hash,
                request_body_hash=request_body_hash or fixture.request_body_hash,
                session_binding_digest=session_digest or fixture.session_digest,
                signed_authority_generation=effective_generation,
            ) as decision:
                outcome = decision.kind
                if decision.kind == "new_command":
                    if action == "complete":
                        response_bytes = _stage_complete(
                            db, decision, fixture, signed_generation=effective_generation
                        )
                    elif action == "appointment":
                        decision.appointment.status = AppointmentStatus.Cancelled
                        decision.appointment.status_reason_code = "PATIENT_CANCELLED"
                        db.flush()
                    elif action == "appointment_audit":
                        decision.appointment.status = AppointmentStatus.Cancelled
                        decision.appointment.status_reason_code = "PATIENT_CANCELLED"
                        db.flush()
                        db.refresh(decision.appointment)
                        _stage_audit(
                            db, decision, fixture, signed_generation=effective_generation
                        )
                        db.flush()
                    elif action == "mismatched":
                        response_bytes = _stage_complete(
                            db, decision, fixture, signed_generation=effective_generation
                        )
                        decision.record.response_body_hash = "0" * 64
                        db.flush()
                    elif action == "abort_complete":
                        _stage_complete(
                            db, decision, fixture, signed_generation=effective_generation
                        )
                        raise OuterAbort("fixed authored-synthetic outer abort")
                    elif action != "none":
                        raise AssertionError("unknown transaction action")
                elif decision.response_body_canonical_bytes is not None:
                    response_bytes = decision.response_body_canonical_bytes
    except physical.DeleteConfirmTargetUnavailable:
        outcome = "target_unavailable"
    except physical.DeleteConfirmAuthorityRevoked:
        outcome = "authority_revoked"
    except physical.DeleteConfirmScaffoldIncomplete:
        outcome = "scaffold_incomplete"
    except physical.DeleteConfirmWaitBudgetExhausted:
        outcome = "wait_budget_exhausted"
    except OuterAbort:
        outcome = "outer_abort"
    finally:
        if clock_exhaust:
            physical.time.monotonic = original_monotonic
        event.remove(engine, "before_cursor_execute", observe)
        if revoke_second_check:
            event.remove(engine, "after_cursor_execute", revoke_hook)
    _assert_token_order(outcome, tuple(tokens))
    return Invocation(
        outcome=outcome,
        response_digest=(
            physical.delete_confirm_response_digest(response_bytes)
            if response_bytes is not None
            else None
        ),
        authority_calls=authority_calls,
        statement_tokens=tuple(tokens),
    )


def _assert_tx_outcome(
    group: dict[str, Any],
    before: dict[str, Any],
    after: dict[str, Any],
    invocation: Invocation,
    disclosure_count: int,
) -> None:
    if invocation.outcome != group["expected"]:
        raise RehearsalFailure("transaction", f"{group['id']}_outcome_mismatch")
    before_version = before["version"] or 0
    after_version = after["version"] or 0
    if after_version - before_version != group["appointment_delta"]:
        raise RehearsalFailure("transaction", f"{group['id']}_appointment_delta_mismatch")
    if after["audit_count"] - before["audit_count"] != group["audit_delta"]:
        raise RehearsalFailure("transaction", f"{group['id']}_audit_delta_mismatch")
    if after["completed_v1_count"] - before["completed_v1_count"] != group["receipt_delta"]:
        raise RehearsalFailure("transaction", f"{group['id']}_receipt_delta_mismatch")
    if disclosure_count != group["disclosure_count"]:
        raise RehearsalFailure("transaction", f"{group['id']}_disclosure_mismatch")
    if invocation.authority_calls != group["authority_calls"]:
        raise RehearsalFailure("transaction", f"{group['id']}_authority_count_mismatch")
    if group["appointment_delta"] == 1:
        if after["status"] != "Cancelled" or after["correlated_count"] != 1:
            raise RehearsalFailure("transaction", f"{group['id']}_write_set_mismatch")
    elif after != before:
        raise RehearsalFailure("transaction", f"{group['id']}_rollback_or_no_effect_mismatch")


def _case_result(
    group: dict[str, Any],
    invocation: Invocation,
    before: dict[str, Any],
    after: dict[str, Any],
    disclosure_count: int,
    *,
    subcases: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    return {
        "id": group["id"],
        "status": "passed",
        "outcome": invocation.outcome,
        "appointment_version_before": before["version"],
        "appointment_version_after": after["version"],
        "audit_delta": after["audit_count"] - before["audit_count"],
        "completed_receipt_delta": (
            after["completed_v1_count"] - before["completed_v1_count"]
        ),
        "disclosure_count": disclosure_count,
        "authority_calls": invocation.authority_calls,
        "statement_tokens": list(invocation.statement_tokens),
        "subcases": list(subcases),
    }


def _run_tx_case(
    engine: Engine, group: dict[str, Any], index: int
) -> dict[str, Any]:
    kind = group["kind"]
    if kind == "clean_new_command":
        return _tx_clean_new_command(engine, group, index)
    if kind == "response_loss_replay":
        return _tx_response_loss_replay(engine, group, index)
    if kind == "binding_conflict":
        return _tx_binding_conflict(engine, group, index)
    if kind == "non_replayable_classifications":
        return _tx_classifications(engine, group, index)
    if kind == "target_unavailable_before_idempotency":
        return _tx_target_unavailable(engine, group, index)
    if kind == "authority_revoked_before_idempotency":
        return _tx_authority_revoked(engine, group, index)
    if kind == "same_transaction_second_check_revocation":
        return _tx_second_check_revocation(engine, group, index)
    if kind == "replay_after_revocation":
        return _tx_replay_after_revocation(engine, group, index)
    if kind == "incomplete_write_set":
        return _tx_incomplete_write_set(engine, group, index)
    if kind == "complete_write_outer_abort":
        return _tx_outer_abort(engine, group, index)
    if kind == "cumulative_deadline_exhaustion":
        return _tx_deadline_exhaustion(engine, group, index)
    raise RehearsalFailure("transaction", "unknown_transaction_group", group["id"])


def _tx_clean_new_command(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    _seed_base(engine, fixture, with_grant=True)
    before = _snapshot(engine, fixture)
    invocation = _invoke_tx(engine, fixture, action="complete", signed_generation=2)
    after = _snapshot(engine, fixture)
    disclosure = int(invocation.response_digest is not None)
    _assert_tx_outcome(group, before, after, invocation, disclosure)
    return _case_result(group, invocation, before, after, disclosure)


def _tx_response_loss_replay(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    _seed_base(engine, fixture, with_grant=True)
    before = _snapshot(engine, fixture)
    first = _invoke_tx(engine, fixture, action="complete", signed_generation=2)
    retry = _invoke_tx(engine, fixture, signed_generation=2)
    if first.response_digest is None or retry.response_digest != first.response_digest:
        raise RehearsalFailure("transaction", "TX-S02_stored_bytes_mismatch")
    invocation = Invocation(
        retry.outcome,
        retry.response_digest,
        first.authority_calls + retry.authority_calls,
        first.statement_tokens + retry.statement_tokens,
    )
    after = _snapshot(engine, fixture)
    _assert_tx_outcome(group, before, after, invocation, 1)
    return _case_result(group, invocation, before, after, 1)


def _tx_binding_conflict(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    _seed_base(engine, fixture, with_grant=True)
    before = _snapshot(engine, fixture)
    first = _invoke_tx(engine, fixture, action="complete", signed_generation=2)
    conflict_request = _invoke_tx(
        engine,
        fixture,
        request_body_hash=_sha256(f"changed-request:{index}"),
        signed_generation=2,
    )
    conflict_session = _invoke_tx(
        engine,
        fixture,
        session_digest=_sha256(f"changed-session:{index}").encode("ascii")[:32],
        signed_generation=2,
    )
    if conflict_request.response_digest is not None or conflict_session.response_digest is not None:
        raise RehearsalFailure("transaction", "TX-S03_conflict_disclosed")
    invocation = Invocation(
        conflict_request.outcome,
        None,
        first.authority_calls + conflict_request.authority_calls + conflict_session.authority_calls,
        first.statement_tokens + conflict_request.statement_tokens + conflict_session.statement_tokens,
    )
    after = _snapshot(engine, fixture)
    _assert_tx_outcome(group, before, after, invocation, 1)
    return _case_result(group, invocation, before, after, 1)


def _tx_classifications(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    specs = (
        ("in_progress", "in_progress_not_replayable"),
        ("legacy", "legacy_receipt_not_replayable"),
        ("corrupt", "receipt_integrity_failure"),
    )
    subcases = []
    total_authority = 0
    total_tokens: tuple[str, ...] = ()
    for sub_index, (seed_kind, expected) in enumerate(specs):
        sub_fixture = _fixture(index * 10 + sub_index)
        _seed_base(engine, sub_fixture, with_grant=True)
        _seed_classification(engine, sub_fixture, seed_kind)
        before = _snapshot(engine, sub_fixture)
        invocation = _invoke_tx(engine, sub_fixture, signed_generation=2)
        after = _snapshot(engine, sub_fixture)
        if invocation.outcome != expected:
            raise RehearsalFailure("transaction", f"TX-S04_{seed_kind}_classification_mismatch")
        if invocation.response_digest is not None:
            raise RehearsalFailure("transaction", "TX-S04_disclosed_bytes")
        if after != before:
            raise RehearsalFailure("transaction", f"TX-S04_{seed_kind}_effect_mismatch")
        subcases.append(
            {
                "id": f"TX-S04-{sub_index + 1}",
                "label": seed_kind,
                "outcome": invocation.outcome,
                "authority_calls": invocation.authority_calls,
            }
        )
        total_authority += invocation.authority_calls
        total_tokens += invocation.statement_tokens
    invocation = Invocation("non_replayable_classifications", None, total_authority, total_tokens)
    before = _snapshot(engine, _fixture(index * 10))
    _assert_tx_outcome(group, before, before, invocation, 0)
    return _case_result(group, invocation, before, before, 0, subcases=tuple(subcases))


def _tx_target_unavailable(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    specs = (
        ("inactive_user", dict(with_grant=False, appointment=True, active=False)),
        ("absent_appointment", dict(with_grant=False, appointment=False, active=True)),
    )
    subcases = []
    total_authority = 0
    total_tokens: tuple[str, ...] = ()
    for sub_index, (label, seed_kwargs) in enumerate(specs):
        sub_fixture = _fixture(index * 10 + sub_index)
        _seed_base(engine, sub_fixture, **seed_kwargs)
        before = _snapshot(engine, sub_fixture)
        invocation = _invoke_tx(engine, sub_fixture, signed_generation=1)
        after = _snapshot(engine, sub_fixture)
        if invocation.outcome != "target_unavailable":
            raise RehearsalFailure("transaction", f"TX-S05_{label}_outcome_mismatch")
        if invocation.response_digest is not None:
            raise RehearsalFailure("transaction", "TX-S05_disclosed_bytes")
        if after != before:
            raise RehearsalFailure("transaction", f"TX-S05_{label}_effect_mismatch")
        subcases.append(
            {
                "id": f"TX-S05-{sub_index + 1}",
                "label": label,
                "outcome": invocation.outcome,
                "authority_calls": invocation.authority_calls,
            }
        )
        total_authority += invocation.authority_calls
        total_tokens += invocation.statement_tokens
    invocation = Invocation("target_unavailable", None, total_authority, total_tokens)
    before = _snapshot(engine, _fixture(index * 10))
    _assert_tx_outcome(group, before, before, invocation, 0)
    return _case_result(group, invocation, before, before, 0, subcases=tuple(subcases))


def _tx_authority_revoked(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    specs = (
        ("missing_grant", dict(with_grant=False, signed_generation=1)),
        ("stale_generation", dict(with_grant=True, signed_generation=1)),
        ("role_mismatch", dict(with_grant=True, signed_generation=2, actor_role="GP")),
    )
    subcases = []
    total_authority = 0
    total_tokens: tuple[str, ...] = ()
    for sub_index, (label, invoke_kwargs) in enumerate(specs):
        sub_fixture = _fixture(index * 10 + sub_index)
        _seed_base(engine, sub_fixture, with_grant=invoke_kwargs["with_grant"])
        before = _snapshot(engine, sub_fixture)
        invocation = _invoke_tx(
            engine,
            sub_fixture,
            signed_generation=invoke_kwargs["signed_generation"],
            actor_role=invoke_kwargs.get("actor_role", "Receptionist"),
        )
        after = _snapshot(engine, sub_fixture)
        if invocation.outcome != "authority_revoked":
            raise RehearsalFailure("transaction", f"TX-S06_{label}_outcome_mismatch")
        if invocation.response_digest is not None:
            raise RehearsalFailure("transaction", "TX-S06_disclosed_bytes")
        if after != before:
            raise RehearsalFailure("transaction", f"TX-S06_{label}_effect_mismatch")
        subcases.append(
            {
                "id": f"TX-S06-{sub_index + 1}",
                "label": label,
                "outcome": invocation.outcome,
                "authority_calls": invocation.authority_calls,
            }
        )
        total_authority += invocation.authority_calls
        total_tokens += invocation.statement_tokens
    invocation = Invocation("authority_revoked", None, total_authority, total_tokens)
    before = _snapshot(engine, _fixture(index * 10))
    _assert_tx_outcome(group, before, before, invocation, 0)
    return _case_result(group, invocation, before, before, 0, subcases=tuple(subcases))


def _tx_second_check_revocation(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    _seed_base(engine, fixture, with_grant=True)
    before = _snapshot(engine, fixture)
    invocation = _invoke_tx(
        engine, fixture, revoke_second_check=True, signed_generation=2
    )
    after = _snapshot(engine, fixture)
    _assert_tx_outcome(group, before, after, invocation, 0)
    return _case_result(group, invocation, before, after, 0)


def _tx_replay_after_revocation(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    _seed_base(engine, fixture, with_grant=True)
    before = _snapshot(engine, fixture)
    first = _invoke_tx(engine, fixture, action="complete", signed_generation=2)
    with engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM user_capability_grants WHERE practice_id=:p AND user_id=:u "
                "AND capability_code='appointment.cancel.confirm'"
            ),
            {"p": fixture.practice_id, "u": fixture.actor_id},
        )
    revoked = _invoke_tx(engine, fixture, signed_generation=2)
    if revoked.outcome != "authority_revoked":
        raise RehearsalFailure("transaction", "TX-S08_revoked_outcome_mismatch")
    if revoked.response_digest is not None:
        raise RehearsalFailure("transaction", "TX-S08_disclosed_after_revocation")
    invocation = Invocation(
        revoked.outcome,
        None,
        first.authority_calls + revoked.authority_calls,
        first.statement_tokens + revoked.statement_tokens,
    )
    after = _snapshot(engine, fixture)
    _assert_tx_outcome(group, before, after, invocation, 1)
    return _case_result(group, invocation, before, after, 1)


def _tx_incomplete_write_set(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    specs = (
        ("empty", "none"),
        ("appointment_only", "appointment"),
        ("appointment_audit_only", "appointment_audit"),
        ("cross_artifact_mismatched", "mismatched"),
    )
    subcases = []
    total_authority = 0
    total_tokens: tuple[str, ...] = ()
    for sub_index, (label, action) in enumerate(specs):
        sub_fixture = _fixture(index * 10 + sub_index)
        _seed_base(engine, sub_fixture, with_grant=True)
        before = _snapshot(engine, sub_fixture)
        invocation = _invoke_tx(engine, sub_fixture, action=action, signed_generation=2)
        after = _snapshot(engine, sub_fixture)
        if invocation.outcome != "scaffold_incomplete":
            raise RehearsalFailure("transaction", f"TX-S09_{label}_outcome_mismatch")
        if invocation.response_digest is not None:
            raise RehearsalFailure("transaction", "TX-S09_disclosed_bytes")
        if after != before:
            raise RehearsalFailure("transaction", f"TX-S09_{label}_digest_mismatch")
        subcases.append(
            {
                "id": f"TX-S09-{sub_index + 1}",
                "label": label,
                "outcome": invocation.outcome,
                "authority_calls": invocation.authority_calls,
            }
        )
        total_authority += invocation.authority_calls
        total_tokens += invocation.statement_tokens
    invocation = Invocation("scaffold_incomplete", None, total_authority, total_tokens)
    before = _snapshot(engine, _fixture(index * 10))
    _assert_tx_outcome(group, before, before, invocation, 0)
    return _case_result(group, invocation, before, before, 0, subcases=tuple(subcases))


def _tx_outer_abort(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    _seed_base(engine, fixture, with_grant=True)
    before = _snapshot(engine, fixture)
    invocation = _invoke_tx(engine, fixture, action="abort_complete", signed_generation=2)
    after = _snapshot(engine, fixture)
    _assert_tx_outcome(group, before, after, invocation, 0)
    return _case_result(group, invocation, before, after, 0)


def _tx_deadline_exhaustion(engine: Engine, group: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    _seed_base(engine, fixture, with_grant=True)
    before = _snapshot(engine, fixture)
    invocation = _invoke_tx(engine, fixture, clock_exhaust=True, signed_generation=2)
    after = _snapshot(engine, fixture)
    _assert_tx_outcome(group, before, after, invocation, 0)
    return _case_result(group, invocation, before, after, 0)


def _failure_evidence(
    error: RehearsalFailure,
    *,
    lifecycle: list[str],
    cleanup: dict[str, Any],
) -> dict[str, Any]:
    detail = error.detail if isinstance(error.detail, bytes) else str(error.detail).encode()
    return {
        "schema_version": "raisa.delete_confirm_behavior_transaction_evidence.v1",
        "result": "rehearsal_failed",
        "evidence_label": "authored_synthetic_provider_free_disposable_postgresql_behavior_transaction",
        "source_head": SOURCE_HEAD,
        "lifecycle": lifecycle,
        "failure": {
            "stage": error.stage,
            "code": error.code,
            "detail_sha256": _sha256(detail),
        },
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
    engine: Engine | None = None
    relay: status_btr.DockerExecRelay | None = None
    evidence: dict[str, Any] | None = None
    error: RehearsalFailure | None = None
    started = time.monotonic()
    try:
        contract, source_hashes = verify_contract()
        lifecycle.append("contract_and_sources_verified")
        profile = contract["docker_profile"]
        docker = shutil.which(profile["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        image_id = status_btr._image_id(docker, profile)  # noqa: SLF001
        lifecycle.append("local_image_verified")
        suffix = secrets.token_hex(8)
        network_name = profile["network_name_prefix"] + suffix
        container_name = profile["container_name_prefix"] + suffix
        network_result = catalogue._run(  # noqa: SLF001
            status_btr.build_network_argv(docker, network_name, nonce, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        network_id = network_result.stdout.decode("utf-8").strip()
        if network_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", network_id):
            raise RehearsalFailure("environment", "network_create_failed", network_result.stderr)
        inspected_result, inspected_network = status_btr._inspect_one(  # noqa: SLF001
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if (
            inspected_result.returncode != 0
            or inspected_network is None
            or not status_btr._network_owned(  # noqa: SLF001
                inspected_network,
                network_id=network_id,
                name=network_name,
                nonce=nonce,
                profile=profile,
                require_empty=True,
            )
        ):
            raise RehearsalFailure("environment", "network_profile_mismatch")
        lifecycle.append("owned_internal_network_verified")
        container_result = catalogue._run(  # noqa: SLF001
            status_btr.build_container_argv(docker, container_name, nonce, network_id, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        container_id = container_result.stdout.decode("utf-8").strip()
        if container_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise RehearsalFailure("environment", "container_create_failed", container_result.stderr)
        inspected_result, inspected_container = status_btr._inspect_one(  # noqa: SLF001
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        owned = (
            status_btr._container_profile(  # noqa: SLF001
                inspected_container,
                container_id=container_id,
                name=container_name,
                nonce=nonce,
                image_id=image_id,
                network_id=network_id,
                profile=profile,
            )
            if inspected_container is not None
            else False
        )
        if inspected_result.returncode != 0 or not owned:
            raise RehearsalFailure("environment", "container_profile_mismatch")
        lifecycle.append("internal_container_profile_verified")
        status_btr._wait_ready(docker, container_id, profile)  # noqa: SLF001
        lifecycle.append("postgresql_16_ready")
        offline_sql = _install_database(docker, container_id, contract)
        lifecycle.append("transaction_schema_installed")
        relay = status_btr.DockerExecRelay(docker, container_id, profile)
        host_port = relay.start()
        lifecycle.append("fixed_loopback_relay_started")
        engine = _engine(host_port, profile)
        catalogue_facts = _catalogue_check(engine)
        lifecycle.append("host_sqlalchemy_catalogue_verified")
        auth_results = [
            _run_auth_case(engine, group, index)
            for index, group in enumerate(contract["authority_groups"], start=1)
        ]
        lifecycle.append("nine_authority_groups_verified")
        tx_results = [
            _run_tx_case(engine, group, index)
            for index, group in enumerate(contract["transaction_groups"], start=20)
        ]
        lifecycle.append("eleven_transaction_groups_verified")
        if time.monotonic() - started > profile["total_timeout_seconds"]:
            raise RehearsalFailure("environment", "total_timeout_exceeded")
        evidence = {
            "schema_version": "raisa.delete_confirm_behavior_transaction_evidence.v1",
            "result": PASS_RESULT,
            "evidence_label": contract["evidence_label"],
            "source_head": contract["source_head"],
            "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
            "source_hashes": source_hashes,
            "hostile_mutations_rejected": HOSTILE_MUTATION_TARGET,
            "environment": {
                "postgresql_major": 16,
                "image_reference": profile["image_reference"],
                "image_id_sha256": _sha256(image_id),
                "network_internal": True,
                "docker_published_ports": False,
                "host_transport": "fixed_in_process_ipv4_loopback_relay",
                "storage": "container_local_tmpfs",
            },
            "offline_sql": {
                "range": contract["alembic"]["offline_range"],
                "body_sha256": _sha256(offline_sql),
                "body_bytes": len(offline_sql),
            },
            "catalogue": catalogue_facts,
            "authority_groups": [
                {
                    "id": result.id,
                    "status": "passed",
                    "generation": result.generation,
                    "grant_count": result.grant_count,
                    "subcases": list(result.subcases),
                }
                for result in auth_results
            ],
            "transaction_groups": tx_results,
            "lifecycle": lifecycle,
            "cleanup": {"status": "pending"},
            "claim_boundary": CLAIM_BOUNDARY,
        }
    except RehearsalFailure as caught:
        error = caught
    except Exception as caught:  # fail closed without persisting raw exception text
        error = RehearsalFailure("harness", "unexpected_exception", type(caught).__name__)
    finally:
        if engine is not None:
            engine.dispose()
        if relay is not None:
            relay.stop()
            lifecycle.append("fixed_loopback_relay_stopped")
        if contract is not None and docker:
            cleanup = status_btr._cleanup(  # noqa: SLF001
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
            error = RehearsalFailure("cleanup", cleanup.get("status", "cleanup_failed"))
        if error is not None:
            evidence = _failure_evidence(error, lifecycle=lifecycle, cleanup=cleanup)
        else:
            assert evidence is not None
            evidence["lifecycle"] = lifecycle
            evidence["cleanup"] = cleanup
    assert evidence is not None
    Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence


def write_evidence(evidence: dict[str, Any]) -> Path:
    target = EVIDENCE_PATH if evidence["result"] == PASS_RESULT else FAILURE_EVIDENCE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target


def main() -> int:
    if len(sys.argv) != 1:
        print('{"result":"rehearsal_failed","code":"caller_arguments_forbidden"}')
        return 2
    evidence = run_rehearsal()
    path = write_evidence(evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "cleanup": evidence["cleanup"]["status"],
                "evidence": str(path.relative_to(ROOT)).replace("\\", "/"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
