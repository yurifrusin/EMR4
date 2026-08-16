"""Focused worker tests for the delete-confirm HTTP/PostgreSQL integration harness.

These tests run provider-free with ``--noconftest``. They import the real
harness module and prove the frozen contract/source gates, the exact lifecycle,
all twelve serial scenarios, the evidence allowlist, cleanup refusal, the real
route/session seam and the absence of any caller override or shell surface.
No Docker, PostgreSQL, browser, external network or provider call is opened.
"""

from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from app.services.appointment_delete_composition import (
    canonical_delete_confirm_envelope_bytes,
    delete_confirm_envelope_projection,
)
from app.services.appointment_delete_physical import (
    canonical_delete_confirm_response_bytes,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal
    as rehearsal,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as foundation,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = rehearsal._load_json(rehearsal.CONTRACT_PATH)  # noqa: SLF001
SCHEMA = rehearsal._load_json(rehearsal.SCHEMA_PATH)  # noqa: SLF001
EVIDENCE_SCHEMA = rehearsal._load_json(rehearsal.EVIDENCE_SCHEMA_PATH)  # noqa: SLF001
PROFILE = CONTRACT["docker_profile"]


def test_contract_schema_sources_groups_and_hostile_gate_pass() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    Draft202012Validator(SCHEMA).validate(CONTRACT)
    rehearsal._validate_contract(CONTRACT, require_digest=True)  # noqa: SLF001
    assert rehearsal.hostile_mutations_rejected(CONTRACT) == rehearsal.HOSTILE_MUTATION_TARGET
    assert rehearsal.HOSTILE_MUTATION_TARGET >= 120
    assert len(CONTRACT["read_only_bindings"]) == 19
    assert len(CONTRACT["editable_preconditions"]) == 4
    assert len(CONTRACT["scenarios"]) == 12


def test_verify_contract_records_read_only_and_editable_present_hashes() -> None:
    verified, source_hashes, implementation_hashes = rehearsal.verify_contract()
    assert verified == CONTRACT
    for path, expected in CONTRACT["read_only_bindings"].items():
        assert source_hashes[path] == expected
    # The four editable preconditions are pre-edit evidence; the present hashes
    # are recorded separately and differ from the pre-edit hashes.
    for item in CONTRACT["editable_preconditions"]:
        assert item["path"] in source_hashes
        assert source_hashes[item["path"]] != item["sha256"]
        assert len(source_hashes[item["path"]]) == 64
    for path in (
        "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py",
        "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py",
        "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_plan.py",
    ):
        assert implementation_hashes[path] == rehearsal._source_text_sha256_bytes(  # noqa: SLF001
            (ROOT / path).read_bytes()
        )


def test_source_hash_rejects_bare_carriage_return() -> None:
    with pytest.raises(rehearsal.RehearsalFailure) as excinfo:
        rehearsal._source_text_sha256_bytes(b"left\rright")  # noqa: SLF001
    assert excinfo.value.code == "source_bare_carriage_return"


def test_repair_semantics_require_adapter_delegation_and_tenant_context_order() -> None:
    present = rehearsal._repair_semantics_ok()  # noqa: SLF001
    assert set(present) == {
        "app/routers/appointments.py",
        "app/services/appointment_delete_physical.py",
        "tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py",
        "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py",
    }


def test_internal_network_container_and_fixed_relay_argv_are_exact() -> None:
    network = foundation.build_network_argv(
        r"C:\Docker\docker.exe",
        PROFILE["network_name_prefix"] + "0123456789abcdef",
        "0" * 32,
        PROFILE,
    )
    container = foundation.build_container_argv(
        r"C:\Docker\docker.exe",
        PROFILE["container_name_prefix"] + "0123456789abcdef",
        "0" * 32,
        "a" * 64,
        PROFILE,
    )
    assert network[:3] == [r"C:\Docker\docker.exe", "network", "create"]
    assert "--internal" in network
    joined = " ".join(container)
    assert "--pull never" in joined
    assert "--tmpfs /var/lib/postgresql/data:" in joined
    assert "--memory 512m" in joined
    assert "--cpus 1" in joined
    assert "--pids-limit 128" in joined
    assert "--restart no" in joined
    assert "--publish" not in container
    for forbidden in ("0.0.0.0", "--volume", "--mount", "trust"):
        assert forbidden not in container
    relay = foundation.build_relay_argv(r"C:\Docker\docker.exe", "b" * 64, PROFILE)
    assert relay[:4] == [
        r"C:\Docker\docker.exe",
        "exec",
        "-i",
        "b" * 64,
    ]
    assert relay[4:6] == ["bash", "-c"]
    assert relay[6] == rehearsal.delete_btr.FIXED_RELAY_COMMAND

def test_harness_has_no_shell_or_broad_docker_discovery() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"run", "Popen"}:
                keywords = {item.arg: item.value for item in node.keywords}
                if "shell" in keywords:
                    assert isinstance(keywords["shell"], ast.Constant)
                    assert keywords["shell"].value is False
    for forbidden in (
        '"container", "ls"',
        '"network", "ls"',
        '"image", "ls"',
        '"volume", "ls"',
        '"prune"',
        '"login"',
    ):
        assert forbidden not in source


def test_main_rejects_caller_selected_arguments(monkeypatch) -> None:
    monkeypatch.setattr(rehearsal.sys, "argv", ["harness", "--port", "5432"])
    assert rehearsal.main() == 2


def test_exact_lifecycle_markers_are_wired_in_order() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    markers = (
        "contract_sources_and_135_mutations_verified",
        "cached_image_verified",
        "owned_internal_network_verified",
        "owned_tmpfs_container_verified",
        "delete_scaffold_projection_role_and_rls_installed",
        "fixed_loopback_relay_started",
        "restricted_application_role_catalogue_verified",
        "twelve_serial_http_postgresql_scenarios_verified",
        "fixed_loopback_relay_stopped",
        "cleanup_verified",
    )
    cursor = -1
    for marker in markers:
        cursor = source.index(marker, cursor + 1)


def test_all_twelve_scenarios_are_wired_serially() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    run = inspect.getsource(rehearsal._run_scenarios)  # noqa: SLF001
    for index in range(1, 13):
        assert f"DHI-S{index:02d}" in run
        assert f"# ── DHI-S{index:02d} " in run
    assert run.count('"id": "DHI-S') == 12
    # Results are appended in exact order.
    first = [run.index(f'"id": "DHI-S{i:02d}"') for i in range(1, 13)]
    assert first == sorted(first)


def test_scenario_outcomes_match_evidence_schema_enum() -> None:
    outcomes = {item[2] for item in rehearsal.EXPECTED_SCENARIOS}
    schema_outcomes = set(
        EVIDENCE_SCHEMA["properties"]["scenarios"]["items"]["properties"]["outcome"][
            "enum"
        ]
    )
    assert outcomes == schema_outcomes


def test_evidence_allowlist_and_forbidden_lists_are_closed() -> None:
    assert set(rehearsal.EXPECTED_EVIDENCE_ALLOWLIST) == set(CONTRACT["evidence_allowlist"])
    assert set(rehearsal.EXPECTED_EVIDENCE_FORBIDDEN) == set(CONTRACT["evidence_forbidden"])
    assert set(rehearsal.EXPECTED_FORBIDDEN_SURFACES) == set(CONTRACT["forbidden_surfaces"])
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    for token in CONTRACT["evidence_forbidden"]:
        # The forbidden categories must not be released as evidence values.
        assert f'"{token}":' not in source


def test_only_get_db_and_get_command_session_factory_are_overridden() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "dependency_overrides[get_db]" in source
    assert "dependency_overrides[get_command_session_factory]" in source
    assert "dependency_overrides[get_current_user]" not in source
    assert "dependency_overrides[" in source
    # Only the two named overrides are set.
    overrides = re_findall_overrides(source)
    assert overrides == {"get_db", "get_command_session_factory"}


def re_findall_overrides(source: str) -> set[str]:
    import re as _re
    return set(_re.findall(r"dependency_overrides\[(\w+)\]", source))


def test_real_route_adapter_and_physical_transaction_seam() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "from app.main import app" in source
    assert "from app.routers import appointments as appointment_router" in source
    assert "from app.services import appointment_delete_product_adapter as adapter" in source
    assert "from app.services.appointment_delete_composition import" in source
    assert "from app.services.appointment_delete_physical import" in source
    # The harness reuses the accepted delete scaffold and ownership/cleanup
    # helpers rather than implementing a substitute command seam.
    assert "delete_btr._install_database(" in source
    assert "foundation._cleanup(" in source
    assert "foundation.DockerExecRelay(" in source
    assert "delete_confirm_locked_transaction" in source
    assert "validate_delete_confirm_private_receipt_bytes" in source
    assert "delete_confirm_response_digest" in source

def test_projection_and_rls_sql_cover_exact_eight_tables() -> None:
    projection = rehearsal.PROJECTION_SQL
    for table in ("practitioners", "patients", "appointment_types"):
        assert f"CREATE TABLE public.{table}" in projection
    rls = rehearsal._role_and_rls_sql(PROFILE)  # noqa: SLF001
    assert f"CREATE ROLE {PROFILE['application_user']} LOGIN" in rls
    assert "NOSUPERUSER NOBYPASSRLS" in rls
    assert f"GRANT CONNECT ON DATABASE {PROFILE['postgres_database']}" in rls
    for table in (
        "appointments",
        "users",
        "practitioners",
        "patients",
        "appointment_types",
        "user_capability_grants",
        "appointment_command_idempotency",
        "appointment_audit_log",
    ):
        assert f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY" in rls
        assert f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY" in rls
        assert f"CREATE POLICY tenant_isolation_{table}" in rls
    assert rls.count("ENABLE ROW LEVEL SECURITY") == 8
    assert rls.count("FORCE ROW LEVEL SECURITY") == 8


def test_application_role_and_tenant_contract_are_fail_closed() -> None:
    assert PROFILE["application_user"] == "emr4_delete_http_app"
    assert PROFILE["network_internal"] is True
    assert PROFILE["published_ports"] is False
    assert PROFILE["pull_policy"] == "never"
    tenant = CONTRACT["tenant_contract"]
    assert tenant["application_role_superuser"] is False
    assert tenant["application_role_bypass_rls"] is False
    assert tenant["transaction_local"] is True
    assert tenant["context_after_isolation_before_reads"] is True


def test_public_private_byte_separation_helper() -> None:
    # Pure proof: the canonical public envelope bytes are distinct from the
    # canonical private receipt bytes and never equal in digest.
    private = canonical_delete_confirm_response_bytes(
        appointment_id="33333333-3333-4333-8333-333333333333",
        status_reason_code="PATIENT_CANCELLED",
        cancellation_reason=None,
        warning_codes=[],
    )
    envelope = delete_confirm_envelope_projection(private)
    public = canonical_delete_confirm_envelope_bytes(envelope)
    assert isinstance(private, bytes) and isinstance(public, bytes)
    assert public != private
    assert rehearsal.delete_confirm_response_digest(public) != rehearsal.delete_confirm_response_digest(
        private
    )
    assert rehearsal._sha256(public) != rehearsal._sha256(private)
    rehearsal.validate_delete_confirm_private_receipt_bytes(private)


def test_cleanup_uses_captured_ids_container_then_empty_network(monkeypatch) -> None:
    calls: list[list[str]] = []
    responses = [
        rehearsal.catalogue.ProcessResult(0, json.dumps([_owned_container()]).encode(), b""),
        rehearsal.catalogue.ProcessResult(0, b"b" * 64 + b"\n", b""),
        rehearsal.catalogue.ProcessResult(1, b"", b"Error: No such object: " + b"b" * 64),
        rehearsal.catalogue.ProcessResult(0, json.dumps([_owned_network()]).encode(), b""),
        rehearsal.catalogue.ProcessResult(0, b"a" * 64 + b"\n", b""),
        rehearsal.catalogue.ProcessResult(1, b"", b"Error: No such network: " + b"a" * 64),
    ]

    def runner(argv, stdin, timeout, cap):
        del stdin, timeout, cap
        calls.append(argv)
        return responses.pop(0)

    monkeypatch.setattr(foundation.catalogue, "_run", runner)
    result = foundation._cleanup(  # noqa: SLF001
        r"C:\Docker\docker.exe",
        container_id="b" * 64,
        container_name=PROFILE["container_name_prefix"] + "0123456789abcdef",
        network_id="a" * 64,
        network_name=PROFILE["network_name_prefix"] + "0123456789abcdef",
        nonce="0" * 32,
        image_id="sha256:" + "c" * 64,
        profile=PROFILE,
    )
    assert result["status"] == "cleanup_verified"
    assert calls[1][1:4] == ["container", "rm", "--force"]
    assert calls[4][1:3] == ["network", "rm"]


def _owned_network(*, empty: bool = True) -> dict:
    return {
        "Id": "a" * 64,
        "Name": PROFILE["network_name_prefix"] + "0123456789abcdef",
        "Driver": "bridge",
        "Internal": True,
        "Labels": {
            "com.emr4.harness": PROFILE["harness_label"],
            "com.emr4.cleanup-nonce": "0" * 32,
        },
        "Containers": {} if empty else {"b" * 64: {}},
    }


def _owned_container() -> dict:
    return {
        "Id": "b" * 64,
        "Name": "/" + PROFILE["container_name_prefix"] + "0123456789abcdef",
        "Image": "sha256:" + "c" * 64,
        "Config": {
            "Image": PROFILE["image_reference"],
            "Labels": {
                "com.emr4.harness": PROFILE["harness_label"],
                "com.emr4.cleanup-nonce": "0" * 32,
            },
            "Env": [
                f"POSTGRES_USER={PROFILE['postgres_user']}",
                f"POSTGRES_PASSWORD={PROFILE['postgres_password']}",
                f"POSTGRES_DB={PROFILE['postgres_database']}",
                f"PGDATA={PROFILE['pgdata']}",
            ],
        },
        "HostConfig": {
            "Binds": None,
            "Privileged": False,
            "Memory": PROFILE["memory_bytes"],
            "NanoCpus": PROFILE["nano_cpus"],
            "PidsLimit": PROFILE["pids_limit"],
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {PROFILE["data_destination"]: PROFILE["tmpfs_options"]},
            "PortBindings": {},
        },
        "NetworkSettings": {
            "Networks": {"owned": {"NetworkID": "a" * 64}},
            "Ports": {"5432/tcp": None},
        },
        "Mounts": [],
    }


def test_cleanup_ownership_uncertainty_refuses_removal(monkeypatch) -> None:
    calls: list[list[str]] = []
    # First inspect returns a foreign container (wrong labels).
    responses = [
        rehearsal.catalogue.ProcessResult(0, json.dumps([_foreign_container()]).encode(), b""),
    ]

    def runner(argv, stdin, timeout, cap):
        del stdin, timeout, cap
        calls.append(argv)
        return responses.pop(0)

    monkeypatch.setattr(foundation.catalogue, "_run", runner)
    result = foundation._cleanup(  # noqa: SLF001
        r"C:\Docker\docker.exe",
        container_id="b" * 64,
        container_name=PROFILE["container_name_prefix"] + "0123456789abcdef",
        network_id=None,
        network_name=PROFILE["network_name_prefix"] + "0123456789abcdef",
        nonce="0" * 32,
        image_id="sha256:" + "c" * 64,
        profile=PROFILE,
    )
    assert result["status"] == "cleanup_ownership_unverified"
    # No destructive rm command was issued.
    assert not any("rm" in argv for argv in calls)


def _foreign_container() -> dict:
    item = _owned_container()
    item["Config"]["Labels"]["com.emr4.cleanup-nonce"] = "f" * 32
    return item

def test_fixture_ids_are_disjoint_and_value_free() -> None:
    seen_practice: set[str] = set()
    seen_appointment: set[str] = set()
    seen_actor: set[str] = set()
    for index in range(101, 114):
        fixture = rehearsal._fixture(index)  # noqa: SLF001
        assert fixture.practice_id not in seen_practice
        assert fixture.appointment_id not in seen_appointment
        assert fixture.actor_id not in seen_actor
        seen_practice.add(fixture.practice_id)
        seen_appointment.add(fixture.appointment_id)
        seen_actor.add(fixture.actor_id)
        assert str(fixture.actor_id) == fixture.actor_text


def test_two_pool_tenant_context_absence_is_boolean_and_sanitized() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "def _two_pool_settings_absent(" in source
    assert "current_setting('app.current_practice_id', true)" in source
    assert "pooled_tenant_setting_leaked" in source


def test_dhi_s11_disables_and_restores_only_adjacent_version_trigger() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "DISABLE TRIGGER" in source
    assert "trg_appointments_advance_state_version" in source
    assert "ENABLE TRIGGER" in source
    assert "rollback_503_and_trigger_restored" in source
    assert "tgenabled='O'" in source
    # The restore is unconditional before continuation.
    assert "failed_trigger = client.post(" in source
    assert "ALTER TABLE public.appointments ENABLE TRIGGER" in source


def test_scenario_http_status_and_decision_codes_are_exact() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    for code in (
        "idempotency_key_conflict",
        "current_authority_unavailable",
        "appointment_not_found",
        "delete_confirm_transaction_unavailable",
    ):
        assert code in source
    # Missing/blank idempotency keys are the route-owned 400; the harness
    # asserts the status class without reimplementing the route error body.
    router_source = (ROOT / "app/routers/appointments.py").read_text(encoding="utf-8")
    assert "idempotency_key_required" in router_source
    for status in ("400", "401", "403", "404", "409", "422", "503"):
        assert f"status_code != {status}" in source or f"status_code == {status}" in source


def test_failure_evidence_is_schema_closed_and_sanitized() -> None:
    error = rehearsal.RehearsalFailure("scenario", "DHI-S02_commit_failed")
    evidence = rehearsal._failure_evidence(  # noqa: SLF001
        error,
        lifecycle=[
            "contract_sources_and_135_mutations_verified",
            "failed_scenario_dhi_s02_commit_failed",
        ],
        cleanup={"status": "cleanup_ownership_unverified", "object": "container"},
        source_hashes={"app/dependencies.py": "0" * 64},
        implementation_hashes={"scripts/owned.py": "0" * 64},
        contract_sha256="0" * 64,
    )
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert evidence["result"] == "rehearsal_failed"
    assert evidence["cleanup"]["status"] == "ownership_mismatch"
    assert evidence["cleanup"]["container_removed"] is False
    assert evidence["cleanup"]["container_absent"] is False
    # The failure is recorded only as a sanitized lifecycle label, never as raw
    # exception text or a closed-schema-violating failure object.
    assert "failed_scenario_dhi_s02_commit_failed" in evidence["lifecycle"]
    rendered = json.dumps(evidence).lower()
    for forbidden in (
        "jwt",
        "bearer",
        "postgresql://",
        "password",
        "response_body_canonical_bytes",
        "insert into",
        "select *",
    ):
        assert forbidden not in rendered


def test_pass_evidence_when_present_is_complete_and_minimized() -> None:
    if not rehearsal.EVIDENCE_PATH.exists():
        pytest.skip("occupied evidence not generated yet")
    evidence = rehearsal._load_json(rehearsal.EVIDENCE_PATH)  # noqa: SLF001
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["hostile_mutations"]["rejected"] == rehearsal.HOSTILE_MUTATION_TARGET
    assert len(evidence["scenarios"]) == 12
    assert all(item["status"] == "passed" for item in evidence["scenarios"])
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    rendered = json.dumps(evidence).lower()
    for forbidden in (
        "authorization: bearer",
        "postgresql://",
        "response_body_canonical_bytes",
        "synthetic-user-",
        "password_hash",
        "insert into",
        "select *",
    ):
        assert forbidden not in rendered


def test_dhi_s04_uses_public_private_proof_not_direct_stored_bytes_comparison() -> None:
    """Guard DHI-S04 against comparing public HTTP replay bytes directly with the private stored receipt."""
    run = inspect.getsource(rehearsal._run_scenarios)  # noqa: SLF001
    section = run[run.index("# ── DHI-S04"):run.index("# ── DHI-S05")]
    # The private/public proof must be invoked for the replay response.
    assert "_public_private_proof(admin, four, replay_four.content)" in section
    # Public HTTP bytes must never be compared directly against the private
    # stored receipt bytes; only the private/public proof may assert distinctness.
    for probe in ("replay_four.content", "first_four.content"):
        assert f"{probe} != _stored_bytes(" not in section
        assert f"{probe} == _stored_bytes(" not in section


def test_dhi_s05_conflict_targets_sibling_appointment_and_has_zero_effect() -> None:
    """Guard DHI-S05 idempotency conflict against asking the route for a new
    proposal on an already-Cancelled target."""
    run = inspect.getsource(rehearsal._run_scenarios)  # noqa: SLF001
    section = run[run.index("# ── DHI-S05"):run.index("# ── DHI-S06")]
    assert "five_sibling" in section
    assert "appointment_only=True" in section
    assert "practice_id=five.practice_id" in section
    assert "actor_id=five.actor_id" in section
    assert "practitioner_id=five.practitioner_id" in section
    # The same idempotency key is reused against the sibling target.
    assert 'headers=_headers(token_five, "shared-conflict")' in section
    assert 'conflict.json().get("detail", {}).get("code")' in section
    assert '!= "idempotency_key_conflict"' in section
    assert "_assert_unchanged(admin, five_sibling)" in section


def test_dhi_s08_absent_binding_returns_exact_422_and_tampered_malformed_block() -> None:
    """Guard DHI-S08 structural probes: absent binding is 422 before the
    handler; malformed/tampered bindings are 200 blocked with no session."""
    run = inspect.getsource(rehearsal._run_scenarios)  # noqa: SLF001
    section = run[run.index("# ── DHI-S08"):run.index("# ── DHI-S09")]
    assert '("absent", None)' in section
    assert '("malformed", {"source_version": 1})' in section
    assert '("tampered", tampered_binding)' in section
    assert "stopped.status_code != 422" in section
    assert "_assert_unchanged(admin, eight)" in section
    assert "command_sessions != 0" in section


def test_assert_unchanged_requires_complete_zero_effect_fields() -> None:
    """Guard the strengthened zero-effect proof fields."""
    source = inspect.getsource(rehearsal._assert_unchanged)  # noqa: SLF001
    assert 'snapshot["status"] != "Booked"' in source
    assert 'snapshot["version"] != 1' in source
    assert 'snapshot["audit_count"] != 0' in source
    assert 'snapshot["idempotency_rows"] != 0' in source
    assert 'snapshot["completed_v1_count"] != 0' in source


def test_dhi_s02_seeds_waiting_area_acknowledges_warning_and_requires_cleared() -> None:
    """Guard DHI-S02 waiting-area clearing through the actual proposal payload."""
    run = inspect.getsource(rehearsal._run_scenarios)  # noqa: SLF001
    section = run[run.index("# ── DHI-S02"):run.index("# ── DHI-S03")]
    assert "waiting_area=True" in section
    assert "DHI-S02_warning_missing" in section
    assert "DHI-S02_warning_not_acknowledged" in section
    assert 'after_two["waiting_area_id"] is not None' in section
    assert 'body_two.get("confirmed_warnings", [])' in section


def test_run_rehearsal_validates_failure_and_pass_evidence_unconditionally() -> None:
    """Guard unconditional final evidence schema validation for pass and failure."""
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    start = source.rindex("assert evidence is not None")
    end = source.index("return evidence", start)
    tail = source[start:end]
    assert "Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)" in tail
    assert 'if evidence["result"] == PASS_RESULT:' not in tail
