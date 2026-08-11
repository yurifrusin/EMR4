from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(rehearsal.CONTRACT_PATH.read_text(encoding="utf-8"))
SCHEMA = json.loads(rehearsal.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
DIGEST = "sha256:" + "0" * 64
CHANGED = "sha256:" + "1" * 64


def _member(count: int = 0, digest: str = DIGEST) -> dict[str, Any]:
    return {"count": count, "digest": digest}


def _packet() -> dict[str, dict[str, Any]]:
    return {
        "admission": _member(1),
        "receipt": _member(),
        "checkpoint": _member(1),
        "lifecycle": _member(),
        "audit": _member(),
        "watermark": _member(2),
        "frame": _member(2),
        "obligation": _member(),
        "anchor": _member(1),
    }


def _committed_packet() -> dict[str, dict[str, Any]]:
    result = copy.deepcopy(_packet())
    for label in rehearsal.TRANSITION_INSERTS:
        result[label] = _member(result[label]["count"] + 1, CHANGED)
    for label in rehearsal.TRANSITION_UPDATES:
        result[label]["digest"] = CHANGED
    return result


def _snapshot() -> dict[str, dict[str, Any]]:
    return {relation: _member() for relation in rehearsal.serial.SNAPSHOT_RELATIONS}


def _identity(isolation: str = "serializable") -> dict[str, Any]:
    return {
        "session_user_matches_expected": True,
        "current_user_matches_expected": True,
        "isolation": isolation,
        "read_only": False,
    }


def _terminal(
    *,
    outcome: str = "commit",
    sqlstate: str | None = None,
    lines: list[str] | None = None,
    isolation: str = "serializable",
) -> dict[str, Any]:
    return {
        "outcome": outcome,
        "sqlstate": sqlstate,
        "result_lines": lines or [],
        "identity": _identity(isolation),
    }


def _indeterminate() -> dict[str, Any]:
    return {
        "outcome": "indeterminate",
        "client_observation": "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT",
        "wait_event_type": "Timeout",
        "wait_event": "PgSleep",
        "cutpoint_observed_ms": 25,
        "normal_process_exit": False,
        "partial_output_parsed_or_retained": False,
    }


def _durability() -> dict[str, Any]:
    return {
        "postgresql_major": 16,
        "fsync": "on",
        "synchronous_commit": "on",
        "full_page_writes": "on",
        "data_checksums": "on",
        "cluster_identity_digest": DIGEST,
    }


def _restart() -> dict[str, Any]:
    return {
        "crash_method": "docker_kill_sigkill_exact_captured_container",
        "stopped_state": "stopped_after_sigkill",
        "started_state": "running",
        "same_container": True,
        "same_cluster": True,
        "startup_ms": 100,
        "durability": _durability(),
    }


def _passing_evidence() -> dict[str, Any]:
    packets = [
        _committed_packet(),
        _packet(),
        _committed_packet(),
        _packet(),
    ]
    packets[0]["anchor"] = _member(2, CHANGED)
    observations = [
        "COMMIT_ACKNOWLEDGED",
        "ROLLBACK_SQLSTATE_P0001_ACKNOWLEDGED",
        "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT",
        "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT",
    ]
    classifications = [
        "COMMITTED_CONFIRMED",
        "ROLLED_BACK_CONFIRMED",
        "COMMITTED_RECOVERED",
        "ROLLED_BACK_RECOVERED",
    ]
    cutpoints = [
        "after_confirmed_anchor_commit",
        "after_confirmed_rollback",
        "observed_post_commit_pg_sleep_then_sigkill",
        "observed_pre_commit_pg_sleep_then_sigkill",
    ]
    scenarios = []
    for index, spec in enumerate(CONTRACT["scenarios"]):
        if index == 0:
            actions = [
                _terminal(lines=["RECEIPT_APPLIED"]),
                _terminal(lines=["2"]),
                _terminal(lines=["RECEIPT_REPLAYED"]),
                _terminal(lines=["PRIMARY"], isolation="read committed"),
                _terminal(lines=["RECEIPT_APPLIED"]),
            ]
        elif index == 1:
            actions = [
                _terminal(outcome="rollback", sqlstate="P0001"),
                _terminal(lines=["RECEIPT_APPLIED"]),
                _terminal(lines=["2"]),
                _terminal(lines=["RECEIPT_REPLAYED"]),
            ]
        elif index == 2:
            actions = [
                _indeterminate(),
                _terminal(lines=["RECEIPT_REPLAYED"]),
                _terminal(lines=["PRIMARY"], isolation="read committed"),
                _terminal(outcome="rollback", sqlstate="CF303"),
                _terminal(lines=["2"]),
                _terminal(lines=["RECEIPT_APPLIED"]),
            ]
        else:
            actions = [
                _indeterminate(),
                _terminal(lines=["RECEIPT_APPLIED"]),
                _terminal(lines=["2"]),
                _terminal(lines=["RECEIPT_REPLAYED"]),
            ]
        scenarios.append(
            {
                "scenario_id": spec["id"],
                "category": spec["category"],
                "client_observation": observations[index],
                "cutpoint": cutpoints[index],
                "recovery_classification": classifications[index],
                "pre_transition_packet": _packet(),
                "post_restart_packet": packets[index],
                "pre_crash_snapshot": _snapshot(),
                "post_restart_snapshot": _snapshot(),
                "restart_exact_match": True,
                "restart": _restart(),
                "actions": actions,
                "readback_checks": {name: True for name in spec["readback"]},
                "forbidden_effects_absent": {
                    name: True for name in spec["forbidden_effects"]
                },
                "passed": True,
            }
        )
    preconditions = [
        *(
            {
                "name": f"register_observer_r0{number}",
                "outcome": _terminal(),
            }
            for number in range(1, 5)
        ),
        {
            "name": "produce_position_one",
            "outcome": _terminal(lines=["1"], isolation="read committed"),
        },
        {
            "name": "produce_position_two",
            "outcome": _terminal(lines=["2"], isolation="read committed"),
        },
        *(
            {
                "name": f"admit_observer_r0{number}_position_1",
                "outcome": _terminal(lines=["PRIMARY"], isolation="read committed"),
            }
            for number in range(1, 5)
        ),
    ]
    return {
        "schema_version": "emr4.raisa-context-fabric-disposable-postgresql-durability-restart-unknown-commit-evidence.v1",
        "result": rehearsal.PASS_RESULT,
        "evidence_mode": rehearsal.EVIDENCE_MODE,
        "attempt_id": "0" * 24,
        "parent": {
            "source_head": "0" * 40,
            "contract_sha256": rehearsal.EXPECTED_CONTRACT_SHA256,
            "artifact_sha256": DIGEST,
            "manifest_sha256": DIGEST,
            "statement_count": 424,
        },
        "environment": {
            "docker_client": "resolved_exact_docker_exe",
            "image": {
                "reference": "postgres:16-bookworm",
                "identity_digest": DIGEST,
                "pull_attempted": False,
            },
            "container": {
                "identity_digest": DIGEST,
                "network_mode": "none",
                "published_ports": 0,
                "bind_mounts": 0,
                "named_volumes": 0,
                "anonymous_volumes": 0,
                "declared_volume_shield": "tmpfs",
                "actual_pgdata_storage": "owned_container_writable_layer",
            },
            "durability": _durability(),
            "elapsed_ms": 1000,
        },
        "lifecycle": [
            "eight_parent_bindings_verified",
            "container_owned_and_storage_closed",
            "postgres16_artifact_and_durability_reconciled",
            "four_disjoint_generations_prepared",
            "four_sigkill_same_cluster_restarts_matched",
            "catalogue_reconciled",
            "cleanup_verified",
            "passed",
        ],
        "preconditions": preconditions,
        "restarts": [row["restart"] for row in scenarios],
        "scenarios": scenarios,
        "scenario_reconciliation": {"expected": 4, "observed": 4, "passed": 4},
        "operation_counters": {
            "sigkill": 4,
            "participant_retry": 0,
            "provider_calls": 0,
            "product_reads": 0,
            "product_commands": 0,
            "external_network_operations": 0,
        },
        "cleanup": {
            "status": "cleanup_verified",
            "removed": True,
            "absence_verified": True,
        },
        "claim_boundary": rehearsal.CLAIM_BOUNDARY,
    }


def test_contract_and_all_parent_bindings_are_exact() -> None:
    contract, _, _, manifest, artifact = rehearsal._validate_contract()
    assert rehearsal._canonical_sha(contract) == rehearsal.EXPECTED_CONTRACT_SHA256
    assert manifest["statement_count"] == 424
    assert (
        artifact
        == (
            ROOT
            / "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert"
        ).read_bytes()
    )


def test_fixture_ordering_admits_successors_only_after_predecessor_progress() -> None:
    setup_source = inspect.getsource(rehearsal._setup_fixtures)
    scenario_source = inspect.getsource(rehearsal._run_scenarios)

    assert "_admission_statements(facts, observer, 1)" in setup_source
    assert "_admission_statements(facts, observer, 2)" not in setup_source
    assert scenario_source.count("_admission_statements(facts, observer, 2)") == 2
    assert rehearsal.EVIDENCE_PATH.name.endswith("attempt-002.json")


def test_storage_and_command_topology_is_exact_and_volume_free() -> None:
    profile = rehearsal._profile()
    default_pgdata = profile["tmpfs"].split(":", 1)[0]
    assert profile["image_reference"] == "postgres:16-bookworm"
    assert profile["network_mode"] == "none"
    assert profile["pgdata"] != default_pgdata
    assert not profile["pgdata"].startswith(default_pgdata + "/")
    argv = rehearsal._run_argv(
        "docker.exe", profile, name="emr4-cf-pg16-restart-00000000", nonce="0" * 32
    )
    assert "--pull=never" in argv
    assert "--network=none" in argv
    assert "--tmpfs" in argv
    assert not set(argv).intersection({"--volume", "-v", "--mount", "--publish", "-p"})
    init = rehearsal._init_argvs("docker.exe", "a" * 64, profile)
    assert sum("--data-checksums" in row for _, row, _ in init) == 1
    assert rehearsal._kill_argv("docker.exe", "a" * 64) == [
        "docker.exe",
        "container",
        "kill",
        "--signal=KILL",
        "a" * 64,
    ]
    assert rehearsal._start_argv("docker.exe", "a" * 64) == [
        "docker.exe",
        "container",
        "start",
        "a" * 64,
    ]
    assert rehearsal._label_absence_argv("docker.exe", profile, "0" * 32) == [
        "docker.exe",
        "container",
        "ls",
        "--all",
        "--no-trunc",
        "--quiet",
        "--filter",
        "label=com.emr4.harness=disposable-postgresql-durability-restart-v1",
        "--filter",
        "label=com.emr4.cleanup-nonce=" + "0" * 32,
    ]


def test_none_network_metadata_is_accepted_only_without_an_endpoint() -> None:
    profile = rehearsal._profile()
    container_id = "a" * 64
    image_id = DIGEST
    name = "emr4-cf-pg16-restart-00000000"
    nonce = "0" * 32
    tmpfs_path, tmpfs_options = profile["tmpfs"].split(":", 1)
    inspected = {
        "Id": container_id,
        "Name": "/" + name,
        "Image": image_id,
        "RestartCount": 0,
        "Config": {
            "Image": profile["image_reference"],
            "Entrypoint": ["/usr/bin/tail"],
            "Cmd": ["--follow", "/dev/null"],
            "Labels": {
                "com.emr4.harness": profile["ownership_labels"]["com.emr4.harness"],
                "com.emr4.cleanup-nonce": nonce,
            },
            "Env": [],
        },
        "HostConfig": {
            "NetworkMode": "none",
            "Binds": None,
            "Privileged": False,
            "PortBindings": {},
            "Memory": 768 * 1024 * 1024,
            "NanoCpus": 1_000_000_000,
            "PidsLimit": profile["pids_limit"],
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {tmpfs_path: tmpfs_options},
        },
        "Mounts": [
            {"Type": "tmpfs", "Destination": tmpfs_path},
        ],
        "State": {"Running": True, "OOMKilled": False},
        "NetworkSettings": {
            "Ports": {},
            "Networks": {
                "none": {
                    "IPAddress": "",
                    "GlobalIPv6Address": "",
                    "Gateway": "",
                    "MacAddress": "",
                }
            },
        },
    }
    assert (
        rehearsal._assert_owned_container(
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            image_id=image_id,
            profile=profile,
            running=True,
        )
        == "running"
    )
    inspected["NetworkSettings"]["Networks"]["none"]["IPAddress"] = "172.1.2.3"
    with pytest.raises(rehearsal.RestartFailure):
        rehearsal._assert_owned_container(
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            image_id=image_id,
            profile=profile,
            running=True,
        )


def test_unknown_client_cutpoints_are_fixed_but_not_classifier_inputs() -> None:
    post_commit = rehearsal._participant_script(
        CONTRACT,
        scenario_id="CFD2-R03",
        participant="u",
        principal="context_coordinator",
        isolation="serializable",
        statements=["SELECT 'RECEIPT_APPLIED';"],
        hold="post_commit",
    ).decode("utf-8")
    pre_commit = rehearsal._participant_script(
        CONTRACT,
        scenario_id="CFD2-R04",
        participant="u",
        principal="context_coordinator",
        isolation="serializable",
        statements=["SELECT 'RECEIPT_APPLIED';"],
        hold="pre_commit",
    ).decode("utf-8")
    assert post_commit.index("COMMIT;") < post_commit.index("pg_catalog.pg_sleep")
    assert pre_commit.index("pg_catalog.pg_sleep") < pre_commit.index("COMMIT;")
    assert post_commit.count("SET SESSION AUTHORIZATION") == 1
    assert pre_commit.count("SET SESSION AUTHORIZATION") == 1
    assert "SET ROLE" not in post_commit + pre_commit
    assert list(inspect.signature(rehearsal.classify_recovery).parameters) == [
        "expected_pretransition",
        "postrestart",
    ]


def test_recovery_classifier_accepts_only_complete_durable_packets() -> None:
    before = _packet()
    assert rehearsal.classify_recovery(before, copy.deepcopy(before)) == (
        "ROLLED_BACK_RECOVERED"
    )
    committed = _committed_packet()
    assert rehearsal.classify_recovery(before, committed) == "COMMITTED_RECOVERED"
    for mutate in (
        lambda packet: packet["audit"].update(count=0),
        lambda packet: packet["anchor"].update(digest=CHANGED),
        lambda packet: packet["checkpoint"].update(count=2),
        lambda packet: packet["receipt"].update(count=2),
    ):
        candidate = copy.deepcopy(committed)
        mutate(candidate)
        with pytest.raises(rehearsal.RestartFailure) as failure:
            rehearsal.classify_recovery(before, candidate)
        assert failure.value.code == "recovery_unresolved"


def test_next_contiguous_transition_coalesces_without_reactivating_frame() -> None:
    before = _packet()
    before["obligation"] = _member(1, CHANGED)
    before["frame"] = _member(2, CHANGED)
    after = copy.deepcopy(before)
    for label in ("receipt", "lifecycle", "audit"):
        after[label] = _member(before[label]["count"] + 1, CHANGED)
    for index, label in enumerate(("checkpoint", "watermark", "obligation"), 2):
        after[label]["digest"] = "sha256:" + str(index) * 64
    rehearsal._assert_next_transition_delta(before, after)
    after["frame"]["digest"] = "sha256:" + "9" * 64
    with pytest.raises(rehearsal.RestartFailure):
        rehearsal._assert_next_transition_delta(before, after)


def test_recovery_packet_query_is_coordinate_scoped_and_complete() -> None:
    facts = rehearsal._facts(rehearsal.serial._json(rehearsal.serial.CONTRACT_PATH))
    sql = rehearsal._recovery_packet_sql(facts, "observer_r03", 1)
    for label in rehearsal.PACKET_RELATIONS:
        assert f"'{label}'" in sql
    assert "observer_id=" in sql
    assert "source_position=1::pg_catalog.int8" in sql
    for forbidden in ("CFD2-R03", "post_commit", "stdout", "stderr", "client_guess"):
        assert forbidden not in sql


def test_passing_evidence_validates_as_one_closed_document() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    payload = _passing_evidence()
    rehearsal.validate_evidence(payload)
    Draft202012Validator(SCHEMA).validate(payload)


Mutation = Callable[[dict[str, Any]], None]


def _set(path: tuple[Any, ...], value: Any) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        target: Any = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return mutate


HOSTILE_EVIDENCE_MUTATIONS: list[Mutation] = [
    _set(("operation_counters", "sigkill"), 3),
    _set(("operation_counters", "participant_retry"), 1),
    _set(("operation_counters", "provider_calls"), 1),
    _set(("cleanup", "absence_verified"), False),
    _set(("scenarios", 2, "recovery_classification"), "ROLLED_BACK_RECOVERED"),
    _set(("scenarios", 2, "post_restart_packet", "audit", "count"), 0),
    _set(("scenarios", 3, "post_restart_packet", "receipt", "count"), 1),
    _set(("scenarios", 3, "client_observation"), "COMMIT_ACKNOWLEDGED"),
    _set(("scenarios", 0, "restart_exact_match"), False),
    _set(("scenarios", 0, "actions", 0, "stdout"), "forbidden"),
    _set(("restarts", 0, "same_cluster"), False),
    _set(("preconditions", 0, "name"), "wrong_precondition"),
]


@pytest.mark.parametrize(
    "mutate", HOSTILE_EVIDENCE_MUTATIONS, ids=lambda value: value.__name__
)
def test_hostile_evidence_mutations_fail_closed(mutate: Mutation) -> None:
    candidate = _passing_evidence()
    mutate(candidate)
    with pytest.raises((rehearsal.RestartFailure, ValidationError)):
        rehearsal.validate_evidence(candidate)
        Draft202012Validator(SCHEMA).validate(candidate)


def test_source_contains_no_runtime_broadening_or_output_retention() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "--network=bridge",
        "--pull=always",
        "docker volume",
        "docker network",
        "pg_resetwal",
        "\nPREPARE TRANSACTION",
        "docker logs",
        "pg_waldump",
        "git add .",
        "git add -A",
    ):
        assert forbidden not in source
    assert "partial_output_parsed_or_retained" in source
    assert "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT" in source
