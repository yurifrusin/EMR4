from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal as harness,
)


ROOT = Path(__file__).resolve().parents[1]


class FakeAttachment:
    def __init__(self, *, terminate_completes: bool = True) -> None:
        self.running = True
        self.terminate_completes = terminate_completes
        self.terminate_count = 0
        self.kill_count = 0
        self.wait_count = 0

    def poll(self) -> int | None:
        return None if self.running else 0

    def terminate(self) -> None:
        self.terminate_count += 1
        if self.terminate_completes:
            self.running = False

    def kill(self) -> None:
        self.kill_count += 1
        self.running = False

    def wait(self, timeout: int) -> int:
        del timeout
        self.wait_count += 1
        if self.running:
            raise harness.subprocess.TimeoutExpired("fake-attachment", 5)
        return 0


@pytest.fixture
def contract() -> dict[str, object]:
    return json.loads(harness.CONTRACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def manifest(contract: dict[str, object]) -> dict[str, object]:
    return harness.build_manifest(
        contract, "emr4_checkin_rfr_0123456789abcdef"
    )


def test_static_admission_is_provider_free_and_exceeds_hostile_thresholds() -> None:
    result = harness.static_check()
    assert result["status"] == "passed"
    assert result["plan_source"] == harness.PLAN_SOURCE
    assert result["source_binding_count"] == 15
    assert result["contract_mutations"]["attempted"] >= 256
    assert result["contract_mutations"]["attempted"] == result[
        "contract_mutations"
    ]["rejected"]
    assert result["manifest_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["state_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["classifier_mutations"] == {"attempted": 24, "rejected": 24}


def test_contract_is_closed_and_binds_full_git_and_program_digests(
    contract: dict[str, object],
) -> None:
    schema = json.loads(harness.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(schema).iter_errors(contract))
    for key in (
        "plan_source",
        "accepted_relay_free_transport_source",
        "accepted_runtime_role_source",
        "protected_source",
    ):
        assert harness.HEX40.fullmatch(str(contract[key]))
    assert len(contract["program_sha256"]) == 11
    assert all(
        harness.HEX64.fullmatch(value)
        for value in contract["program_sha256"].values()
    )
    assert all(value is False for value in contract["closed_boundaries"].values())


def test_manifest_is_closed_disjoint_and_default_denied(
    contract: dict[str, object], manifest: dict[str, object]
) -> None:
    role = manifest["physical_role_identifier"]
    assert harness.validate_manifest(
        manifest, physical_role=role, canonical=manifest
    ) == manifest
    assert manifest["practice_id"] != manifest["other_practice_id"]
    assert manifest["commands"]["rollback"]["command_id"] != manifest[
        "commands"
    ]["ambiguous_response"]["command_id"]
    assert manifest["automatic_retry_count"] == 0
    assert manifest["ordinary_admission_release_count"] == 0
    assert manifest["product_record_count"] == 0
    attempted, rejected = harness.hostile_manifest_mutations_rejected(
        manifest,
        role,
        contract["hostile_thresholds"]["manifest_and_evidence_state"],
    )
    assert attempted == rejected == 96


def test_readback_classifier_accepts_only_closed_zero_or_exact_packet(
    manifest: dict[str, object],
) -> None:
    packet = harness._canonical_packet(manifest)
    digest = manifest["commands"]["ambiguous_response"]["request_sha256"]
    assert harness.classify_readback(packet, digest) == "committed_exactly_once"
    assert (
        harness.classify_readback(
            {"effect": [], "receipt": [], "audit": []}, digest
        )
        == "rolled_back_zero_effect"
    )
    for member in harness.PACKET_KEYS:
        candidate = copy.deepcopy(packet)
        candidate[member].append(copy.deepcopy(candidate[member][0]))
        assert harness.classify_readback(candidate, digest) == "unresolved_denied"
        candidate = copy.deepcopy(packet)
        candidate[member] = []
        assert harness.classify_readback(candidate, digest) == "unresolved_denied"
    candidate = copy.deepcopy(packet)
    candidate["receipt"][0]["request_sha256"] = "0" * 64
    assert harness.classify_readback(candidate, digest) == "unresolved_denied"


def test_caller_state_requires_exact_exit_42_and_prior_observer() -> None:
    exact = {
        "identity_match": True,
        "stopped": True,
        "exit_code": 42,
        "oom_killed": False,
        "state_error_empty": True,
        "restart_count": 0,
    }
    assert (
        harness.classify_caller_state(exact, observer_passed=True)
        == "connection_lost_without_complete_terminal_response"
    )
    assert (
        harness.classify_caller_state(exact, observer_passed=False)
        == "unresolved_denied"
    )
    for key, replacement in (
        ("identity_match", False),
        ("stopped", False),
        ("exit_code", 0),
        ("exit_code", 43),
        ("oom_killed", True),
        ("state_error_empty", False),
        ("restart_count", 1),
    ):
        candidate = copy.deepcopy(exact)
        candidate[key] = replacement
        assert (
            harness.classify_caller_state(candidate, observer_passed=True)
            == "unresolved_denied"
        )
    assert harness.hostile_states_rejected(96) == (96, 96)


def test_programs_are_fixed_and_credentials_are_not_arguments(
    contract: dict[str, object], manifest: dict[str, object]
) -> None:
    role = manifest["physical_role_identifier"]
    harness.verify_program_digests(contract, manifest, role)
    assert "IFS= read -r emr4_password" in harness.ACTION_WRAPPER
    assert "export PGPASSWORD" in harness.ACTION_WRAPPER
    assert "--command=\"$4\"" in harness.ACTION_WRAPPER
    assert "exit 42" in harness.ACTION_WRAPPER
    assert "docker-entrypoint.sh postgres" in harness._server_wrapper(contract)
    assert "POSTGRES_PASSWORD=$" not in harness._server_wrapper(contract)
    arguments = harness._action_arguments(
        contract,
        user=role,
        sql=harness._rollback_sql(contract, manifest),
        application_name="emr4_checkin_rfr_1111111111111111",
    )
    assert len(arguments) == 6
    assert not any("password" in value.lower() for value in arguments)


def test_sql_fixes_atomicity_rls_observer_and_no_retry(
    contract: dict[str, object], manifest: dict[str, object]
) -> None:
    role = manifest["physical_role_identifier"]
    setup = harness._setup_sql(contract, role)
    rollback = harness._rollback_sql(contract, manifest)
    ambiguous = harness._ambiguous_sql(contract, manifest)
    observer = harness._observer_sql(
        contract, role, "emr4_checkin_rfr_1111111111111111"
    )
    readback = harness._authoritative_readback_sql(contract, manifest)
    assert setup.count("FORCE ROW LEVEL SECURITY") == 3
    assert "NOBYPASSRLS" in setup
    assert "role ownership mismatch" in setup
    assert rollback.rstrip().endswith("ROLLBACK;")
    assert "COMMIT;" in ambiguous and "pg_sleep(30)" in ambiguous
    assert "wait_event_type='Timeout'" in observer
    assert "wait_event='PgSleep'" in observer
    assert "pg_terminate_backend(target_pid)" in observer
    assert manifest["other_practice_id"] in readback
    source = Path(harness.__file__).read_text(encoding="utf-8")
    assert "automatic_retry_count" in source
    assert "command reissue" not in source.lower()


def test_source_has_no_host_relay_process_queue_or_exec_bridge() -> None:
    source = Path(harness.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not imported.intersection({"socket", "multiprocessing", "queue"})
    assert "Docker" + "ExecRelay" not in {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    assert '"exec"' not in source
    assert "--publish" not in source
    assert "PortBindings" in source


def test_container_identity_predicates_separate_credentials_nonce_and_network_lifecycle(
    contract: dict[str, object],
) -> None:
    profile = contract["containment_profile"]
    network_id = "a" * 64
    network_name = "emr4-checkin-rfr-net-example"
    nonce = "b" * 32
    container_id = "c" * 64
    name = "emr4-checkin-rfr-action-example"
    row = {
        "Id": container_id,
        "Name": "/" + name,
        "Image": profile["image_id"],
        "Config": {
            "Image": profile["image_reference"],
            "Labels": {
                profile["harness_label_key"]: profile["harness_label_value"],
                profile["nonce_label_key"]: nonce,
                "emr4.action": "readiness",
            },
            "OpenStdin": True,
            "Env": [],
        },
        "HostConfig": {
            "NetworkMode": network_id,
            "PortBindings": {},
            "Binds": None,
            "LogConfig": {"Type": "none"},
            "RestartPolicy": {"Name": "no"},
            "ReadonlyRootfs": True,
            "Memory": profile["sidecar_memory_bytes"],
            "NanoCpus": profile["sidecar_nano_cpus"],
            "PidsLimit": profile["sidecar_pids_limit"],
            "CapDrop": ["ALL"],
            "SecurityOpt": ["no-new-privileges"],
            "Tmpfs": {
                profile["sidecar_tmpfs_destination"]: profile[
                    "sidecar_tmpfs_options"
                ]
            },
        },
        "NetworkSettings": {
            "Networks": {network_name: {"NetworkID": ""}}
        },
    }
    assert harness._container_matches(
        row,
        container_id=container_id,
        container_name=name,
        network_name=network_name,
        network_id=network_id,
        nonce=nonce,
        contract=contract,
        kind="readiness",
        forbidden_values=("f" * 64, nonce),
    )
    candidate = copy.deepcopy(row)
    candidate["Config"]["Env"] = ["PGPASSWORD=" + "f" * 64]
    assert not harness._container_matches(
        candidate,
        container_id=container_id,
        container_name=name,
        network_name=network_name,
        network_id=network_id,
        nonce=nonce,
        contract=contract,
        kind="readiness",
        forbidden_values=("f" * 64, nonce),
    )
    candidate = copy.deepcopy(row)
    candidate["Config"]["Env"] = ["UNRELATED=" + nonce]
    assert not harness._container_matches(
        candidate,
        container_id=container_id,
        container_name=name,
        network_name=network_name,
        network_id=network_id,
        nonce=nonce,
        contract=contract,
        kind="readiness",
        forbidden_values=("f" * 64, nonce),
    )
    for key, value in (
        ("network_key", "foreign-network"),
        ("network_mode", "foreign-network"),
        ("endpoint_network_id", "d" * 64),
    ):
        candidate = copy.deepcopy(row)
        if key == "network_key":
            candidate["NetworkSettings"]["Networks"] = {
                value: {"NetworkID": ""}
            }
        elif key == "network_mode":
            candidate["HostConfig"]["NetworkMode"] = value
        else:
            candidate["NetworkSettings"]["Networks"][network_name][
                "NetworkID"
            ] = value
        assert not harness._container_matches(
            candidate,
            container_id=container_id,
            container_name=name,
            network_name=network_name,
            network_id=network_id,
            nonce=nonce,
            contract=contract,
            kind="readiness",
            forbidden_values=("f" * 64, nonce),
        )


def test_failed_server_acquisition_cleans_exact_owned_id_before_raising(
    monkeypatch: pytest.MonkeyPatch, contract: dict[str, object]
) -> None:
    container_id = "c" * 64
    calls: list[tuple[str, ...]] = []
    removed = False

    def fake_docker(
        executable: str,
        *arguments: str,
        check: bool = True,
        timeout: int = 30,
    ) -> object:
        nonlocal removed
        del executable, check, timeout
        calls.append(arguments)
        if arguments[0] == "create":
            return type("Result", (), {"stdout": container_id, "returncode": 0})()
        if arguments[:2] == ("container", "inspect"):
            if removed:
                return type("Result", (), {"stdout": "", "returncode": 1})()
            return type(
                "Result", (), {"stdout": json.dumps([row]), "returncode": 0}
            )()
        if arguments[:2] == ("rm", "--force"):
            removed = True
        return type("Result", (), {"stdout": "", "returncode": 0})()

    row = {
        "Id": container_id,
        "Name": "/emr4-checkin-rfr-pg16-0123456789abcdef",
        "Image": contract["containment_profile"]["image_id"],
        "State": {"Status": "created", "Running": False},
        "Config": {
            "Image": contract["containment_profile"]["image_reference"],
            "Labels": {
                contract["containment_profile"]["harness_label_key"]: contract[
                    "containment_profile"
                ]["harness_label_value"],
                contract["containment_profile"]["nonce_label_key"]: "b" * 32,
            },
        },
    }
    monkeypatch.setattr(harness, "_docker", fake_docker)
    monkeypatch.setattr(harness, "_inspect_container", lambda *_: row)
    monkeypatch.setattr(
        harness,
        "_container_profile_predicates",
        lambda *_, **__: {"captured_network_name_key": False},
    )
    monkeypatch.setattr(harness.secrets, "token_hex", lambda _: "0123456789abcdef")
    with pytest.raises(harness.RehearsalFailure) as caught:
        harness._create_server(
            "docker.exe",
            contract,
            nonce="b" * 32,
            network_id="a" * 64,
            network_name="ignored-runtime-key",
            forbidden_values=("f" * 64,),
        )
    assert caught.value.code == "server_profile_mismatch_cleaned"
    assert caught.value.detail == "captured_network_name_key"
    assert ("rm", "--force", container_id) in calls


def test_cleanup_error_never_overwrites_primary_coordinate() -> None:
    lifecycle: list[str] = []
    primary = harness.RehearsalFailure(
        "environment", "server_profile_mismatch_cleaned", "server_tmpfs"
    )
    cleanup = harness.RehearsalFailure("cleanup", "exact_cleanup_unverified")
    assert harness._preserve_primary_error(primary, cleanup, lifecycle) is primary
    assert lifecycle == ["cleanup_exact_cleanup_unverified_after_primary_failure"]
    failure = harness._failure_evidence(primary, lifecycle, {"status": "failed"})
    assert failure["stage"] == "environment"
    assert failure["code"] == "server_profile_mismatch_cleaned"
    assert failure["failed_predicates"] == ["server_tmpfs"]


@pytest.mark.parametrize(
    "state",
    [
        {"Running": False},
        {},
        {"Running": "true"},
    ],
)
def test_post_readiness_running_failure_is_distinct_and_has_no_detail(
    monkeypatch: pytest.MonkeyPatch,
    contract: dict[str, object],
    state: dict[str, object],
) -> None:
    attachment = FakeAttachment()

    def inspect(*_: object) -> dict[str, object]:
        assert attachment.poll() is None
        return {"State": state}

    monkeypatch.setattr(harness, "_inspect_container", inspect)
    with pytest.raises(harness.RehearsalFailure) as caught:
        try:
            harness._verify_server_after_readiness(
                "docker.exe",
                container_id="c" * 64,
                container_name="server",
                network_name="network",
                network_id="a" * 64,
                nonce="b" * 32,
                contract=contract,
                forbidden_values=("f" * 64, "b" * 32),
            )
        finally:
            assert harness._stop_attachment(attachment)
    assert caught.value.stage == "environment"
    assert caught.value.code == "server_not_running_after_readiness"
    assert caught.value.detail is None
    assert attachment.terminate_count == 1
    assert attachment.kill_count == 0
    assert attachment.wait_count == 1


def test_post_readiness_identity_failure_retains_only_sorted_predicate_names(
    monkeypatch: pytest.MonkeyPatch, contract: dict[str, object]
) -> None:
    attachment = FakeAttachment()

    def inspect(*_: object) -> dict[str, object]:
        assert attachment.poll() is None
        return {"State": {"Running": True}}

    def predicates(*_: object, **__: object) -> dict[str, bool]:
        assert attachment.poll() is None
        return {"server_tmpfs": False, "captured_id": True, "server_cpu": False}

    monkeypatch.setattr(harness, "_inspect_container", inspect)
    monkeypatch.setattr(harness, "_container_profile_predicates", predicates)
    with pytest.raises(harness.RehearsalFailure) as caught:
        try:
            harness._verify_server_after_readiness(
                "docker.exe",
                container_id="c" * 64,
                container_name="server",
                network_name="network",
                network_id="a" * 64,
                nonce="b" * 32,
                contract=contract,
                forbidden_values=("f" * 64, "b" * 32),
            )
        finally:
            assert harness._stop_attachment(attachment)
    assert caught.value.code == "server_identity_mismatch_after_readiness"
    assert caught.value.detail == "server_cpu,server_tmpfs"
    failure = harness._failure_evidence(caught.value, [], {"status": "failed"})
    assert failure["failed_predicates"] == ["server_cpu", "server_tmpfs"]
    assert attachment.terminate_count == 1


def test_post_readiness_malformed_identity_retains_only_inspect_shape(
    monkeypatch: pytest.MonkeyPatch, contract: dict[str, object]
) -> None:
    attachment = FakeAttachment()
    monkeypatch.setattr(
        harness,
        "_inspect_container",
        lambda *_: {"State": {"Running": True}},
    )
    monkeypatch.setattr(
        harness,
        "_container_profile_predicates",
        lambda *_, **__: {"inspect_shape": False},
    )
    with pytest.raises(harness.RehearsalFailure) as caught:
        try:
            harness._verify_server_after_readiness(
                "docker.exe",
                container_id="c" * 64,
                container_name="server",
                network_name="network",
                network_id="a" * 64,
                nonce="b" * 32,
                contract=contract,
                forbidden_values=("f" * 64, "b" * 32),
            )
        finally:
            assert harness._stop_attachment(attachment)
    assert caught.value.code == "server_identity_mismatch_after_readiness"
    assert caught.value.detail == "inspect_shape"
    assert attachment.terminate_count == 1


def test_attachment_stays_live_through_post_readiness_and_next_sidecar_stage(
    monkeypatch: pytest.MonkeyPatch, contract: dict[str, object]
) -> None:
    attachment = FakeAttachment()
    sequence: list[str] = []

    def inspect(*_: object) -> dict[str, object]:
        assert attachment.poll() is None
        assert attachment.terminate_count == 0
        sequence.append("inspect")
        return {"State": {"Running": True}}

    def predicates(*_: object, **__: object) -> dict[str, bool]:
        assert attachment.poll() is None
        assert attachment.terminate_count == 0
        sequence.append("predicates")
        return {"captured_id": True, "server_tmpfs": True}

    monkeypatch.setattr(harness, "_inspect_container", inspect)
    monkeypatch.setattr(harness, "_container_profile_predicates", predicates)
    try:
        row = harness._verify_server_after_readiness(
            "docker.exe",
            container_id="c" * 64,
            container_name="server",
            network_name="network",
            network_id="a" * 64,
            nonce="b" * 32,
            contract=contract,
            forbidden_values=("f" * 64, "b" * 32),
        )
        sequence.append("readiness_verified")
        assert row["State"]["Running"] is True
        assert attachment.poll() is None
        assert attachment.terminate_count == 0
        sequence.append("next_sidecar_started")
    finally:
        assert harness._stop_attachment(attachment)
    assert sequence == [
        "inspect",
        "predicates",
        "readiness_verified",
        "next_sidecar_started",
    ]
    assert attachment.terminate_count == 1
    assert attachment.kill_count == 0
    assert attachment.wait_count == 1


def test_run_rehearsal_has_no_early_server_attachment_teardown() -> None:
    source = Path(harness.__file__).read_text(encoding="utf-8")
    readiness = source.index('action="readiness"')
    setup = source.index('action="setup_and_catalogue"', readiness)
    post_readiness = source[readiness:setup]
    assert "_verify_server_after_readiness(" in post_readiness
    assert "_stop_attachment(server_attachment)" not in post_readiness
    assert "server_attachment = None" not in post_readiness


def test_success_schemas_accept_only_closed_sanitized_shapes(
    contract: dict[str, object], manifest: dict[str, object]
) -> None:
    state0 = {
        "stopped": True,
        "exit_code": 0,
        "oom_killed": False,
        "state_error_empty": True,
        "restart_count": 0,
    }
    state42 = {**state0, "exit_code": 42}
    attestation = {
        "schema_version": "emr4.check-in-relay-free-rollback-unknown-response-transaction-attestation.v1",
        "evidence_reference": "evidence-ref:authored-synthetic/check-in-relay-free-rollback-unknown-response-transaction-attestation",
        "source_head": harness.PLAN_SOURCE,
        "plan_source": harness.PLAN_SOURCE,
        "contract_sha256": "a" * 64,
        "manifest_sha256": "b" * 64,
        "role_catalogue": {
            "login": True,
            "superuser": False,
            "create_database": False,
            "create_role": False,
            "inherit": False,
            "replication": False,
            "bypass_rls": False,
            "memberships": 0,
            "owned_objects": 0,
            "product_privileges": 0,
        },
        "relation_catalogue": {
            "relation_count": 3,
            "admin_owned_count": 3,
            "rls_enabled_count": 3,
            "rls_forced_count": 3,
            "policy_count": 3,
            "constraint_count": 21,
            "grants_exact": True,
        },
        "explicit_rollback": {
            "action_state": state0,
            "staged_counts": {"effect": 1, "receipt": 1, "audit": 1},
            "readback_state": state0,
            "readback_counts": {"effect": 0, "receipt": 0, "audit": 0},
            "classification": "rolled_back_zero_effect",
        },
        "ambiguous_response": {
            "observer_state": state0,
            "exact_backend_observed": True,
            "exact_backend_terminated": True,
            "caller_state": state42,
            "classification": "connection_lost_without_complete_terminal_response",
            "complete_terminal_response": False,
            "success_released": False,
            "retry_count": 0,
        },
        "authoritative_readback": {
            "state": state0,
            "counts": {"effect": 1, "receipt": 1, "audit": 1},
            "classification": "committed_exactly_once",
            "other_practice_visible_count": 0,
            "duplicate_effect_count": 0,
        },
        "hostile_classifier": {"attempted": 24, "rejected": 24, "escapes": 0},
        "ordinary_admission_release_count": 0,
        "product_record_count": 0,
        "redaction": {
            "forbidden_fields": 0,
            "forbidden_values": 0,
            "status": "passed",
        },
    }
    schema = json.loads(harness.ATTESTATION_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(schema).iter_errors(attestation))
    hostile = copy.deepcopy(attestation)
    hostile["ambiguous_response"]["retry_count"] = 1
    assert list(Draft202012Validator(schema).iter_errors(hostile))
    harness._assert_redacted(attestation, forbidden_values=("f" * 64,))
