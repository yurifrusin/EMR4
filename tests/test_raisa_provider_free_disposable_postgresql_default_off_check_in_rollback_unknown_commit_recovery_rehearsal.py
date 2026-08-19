import copy
import json
import socket
import sys
import threading
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_rollback_unknown_commit_recovery_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "default-off-check-in-rollback-unknown-commit-recovery-rehearsal"
)


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def _valid_packet() -> dict:
    common = {
        "practice_id": "33333333-3333-4333-8333-333333333333",
        "command_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb20",
        "effect_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb21",
        "idempotency_identity": (
            "idem:authored-synthetic/check-in-ambiguous-response-v1"
        ),
        "request_sha256": (
            "88ac70cf6f8d19d247cb4eb676e1bac0dbdaaee42e8ae3332b98e4c619b802e8"
        ),
    }
    return {
        "effect": [{**common, "effect_kind": "check_in"}],
        "receipt": [{**common, "outcome": "committed"}],
        "audit": [
            {
                **common,
                "audit_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb22",
                "action": "check_in_committed",
            }
        ],
    }


def test_contract_and_all_seventeen_exact_sources_pass_before_environment_use() -> None:
    contract, source_hashes, mutations = rehearsal.verify_contract()

    assert contract["source_head"] == "26402cb8667c2dbf62e86c6eb4c0b000d274559e"
    assert contract["accepted_runtime_role_source"] == (
        "6a2832575e9b4df5c40a13984db7281e79814a94"
    )
    assert len(source_hashes) == 17
    assert mutations[0] >= 256
    assert mutations[0] == mutations[1]


def test_all_rehearsal_schemas_are_valid_and_contract_is_closed() -> None:
    for name in (
        "rehearsal-contract.schema.json",
        "transaction-manifest.schema.json",
        "transaction-attestation.schema.json",
        "rehearsal-evidence.schema.json",
    ):
        Draft202012Validator.check_schema(_load(name))

    validator = Draft202012Validator(
        _load("rehearsal-contract.schema.json"), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(_load("rehearsal-contract.json"))) == []


def test_manifest_is_declarative_closed_and_hostile_mutations_deny() -> None:
    contract = _load("rehearsal-contract.json")
    physical_role = "emr4_checkin_ruc_0123456789abcdef"
    manifest = rehearsal.build_manifest(contract, physical_role)

    rehearsal._validate_manifest(  # noqa: SLF001
        manifest, physical_role=physical_role, canonical=manifest
    )
    attempted, rejected = rehearsal.hostile_manifest_mutations_rejected(
        manifest,
        physical_role,
        contract["hostile_thresholds"]["manifest"],
    )

    assert attempted >= 96
    assert attempted == rejected
    assert manifest["authority_git_object"] == (
        "6a2832575e9b4df5c40a13984db7281e79814a94"
    )
    assert manifest["automatic_retry_allowed"] is False
    assert manifest["ordinary_admission_release_count"] == 0
    assert set(manifest) == set(
        _load("transaction-manifest.schema.json")["required"]
    )
    serialized = json.dumps(manifest).lower()
    for forbidden in ("password", "dsn", "endpoint", "execute", "policy_decision"):
        assert forbidden not in serialized


def test_classifier_accepts_only_empty_or_one_consistent_packet() -> None:
    packet = _valid_packet()
    expected_digest = packet["effect"][0]["request_sha256"]

    assert (
        rehearsal.classify_readback(
            {"effect": [], "receipt": [], "audit": []}, expected_digest
        )
        == "rolled_back_zero_effect"
    )
    assert (
        rehearsal.classify_readback(packet, expected_digest)
        == "committed_exactly_once"
    )
    assert rehearsal.classify_readback(packet, "0" * 64) == "unresolved_denied"


def test_hostile_partial_duplicate_identity_and_digest_packets_all_deny() -> None:
    packet = _valid_packet()
    expected_digest = packet["effect"][0]["request_sha256"]

    attempted, rejected = rehearsal.hostile_classifier_packets_rejected(
        packet, expected_digest, 24
    )

    assert attempted >= 24
    assert attempted == rejected
    partial = copy.deepcopy(packet)
    partial["audit"] = []
    assert rehearsal.classify_readback(partial, expected_digest) == (
        "unresolved_denied"
    )


@pytest.mark.parametrize(
    "field",
    [
        "password",
        "database_url",
        "connection_url",
        "raw_output",
        "raw_exception",
        "backend_pid",
        "server_log",
        "container_name",
        "network_name",
        "application_name",
    ],
)
def test_evidence_redaction_rejects_forbidden_fields(field: str) -> None:
    with pytest.raises(rehearsal.RehearsalFailure):
        rehearsal._assert_redacted({field: "authored-synthetic"})  # noqa: SLF001


def test_evidence_redaction_rejects_credentials_and_connection_urls() -> None:
    with pytest.raises(rehearsal.RehearsalFailure):
        rehearsal._assert_redacted(  # noqa: SLF001
            {"safe": "prefix-runtime-credential-suffix"},
            forbidden_values=("runtime-credential",),
        )
    with pytest.raises(rehearsal.RehearsalFailure):
        rehearsal._assert_redacted(  # noqa: SLF001
            {"safe": "postgresql://synthetic.invalid/db"}
        )


def test_contract_freezes_serial_no_retry_containment_and_claim_boundary() -> None:
    contract = _load("rehearsal-contract.json")

    assert [item["id"] for item in contract["scenarios"]] == list(
        rehearsal.EXPECTED_SCENARIOS
    )
    assert contract["transaction_profile"]["automatic_retry_allowed"] is False
    assert contract["transaction_profile"][
        "success_released_on_connection_loss"
    ] is False
    assert contract["transaction_profile"]["ordinary_admission_release_count"] == 0
    assert contract["role_profile"]["probe_privileges"] == ["INSERT", "SELECT"]
    containment = contract["containment_profile"]
    assert containment["pull_policy"] == "never"
    assert containment["network_internal"] is True
    assert containment["published_ports"] is False
    assert containment["restart_policy"] == "no"
    assert contract["closed_boundaries"] == {
        key: False for key in contract["closed_boundaries"]
    }


def test_harness_imports_no_product_configuration_or_provider_module() -> None:
    source = (
        ROOT
        / "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_rollback_unknown_commit_recovery_rehearsal.py"
    ).read_text(encoding="utf-8")

    assert "from app" not in source
    assert "import app" not in source
    assert ".env" not in source
    assert "appointment_check_in_product_adapter" not in source
    assert "vertex" not in source.lower()
    assert "openai" not in source.lower()


def test_result_channel_is_consumed_before_worker_join() -> None:
    source = (
        ROOT
        / "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_rollback_unknown_commit_recovery_rehearsal.py"
    ).read_text(encoding="utf-8")

    consume = source.index("caller_outcome = worker_queue.get")
    join = source.index("worker.join(5)", consume)
    exit_code = source.index("worker.exitcode != 0", join)
    assert consume < join < exit_code
    assert '"worker_join_timeout"' not in source


def test_rehearsal_local_relay_propagates_process_eof_to_client() -> None:
    relay = object.__new__(rehearsal.EOFPropagatingDockerExecRelay)
    relay._argv = [  # noqa: SLF001
        sys.executable,
        "-c",
        (
            "import sys; sys.stdin.buffer.read(1); "
            "sys.stdout.buffer.write(b'ack'); sys.stdout.buffer.flush()"
        ),
    ]
    relay._stopping = threading.Event()  # noqa: SLF001
    relay._lock = threading.Lock()  # noqa: SLF001
    relay._connections = set()  # noqa: SLF001
    relay._processes = set()  # noqa: SLF001
    relay_side, client_side = socket.socketpair()
    relay._connections.add(relay_side)  # noqa: SLF001
    bridge = threading.Thread(target=relay._bridge, args=(relay_side,), daemon=True)  # noqa: SLF001
    bridge.start()
    client_side.settimeout(3)
    client_side.sendall(b"x")

    assert client_side.recv(3) == b"ack"
    assert client_side.recv(1) == b""
    client_side.close()
    bridge.join(3)

    assert not bridge.is_alive()
    assert relay._connections == set()  # noqa: SLF001
    assert relay._processes == set()  # noqa: SLF001


def test_failure_writer_preserves_numbered_attempts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(rehearsal, "BASE", tmp_path)
    monkeypatch.setattr(rehearsal, "FAILURE_PATH", tmp_path / "latest.json")
    first = {"result": "rehearsal_failed", "attempt": 1}
    second = {"result": "rehearsal_failed", "attempt": 2}

    first_path = rehearsal.write_evidence(first, None)
    second_path = rehearsal.write_evidence(second, None)

    assert first_path.name == "rehearsal-failure-evidence-attempt-001.json"
    assert second_path.name == "rehearsal-failure-evidence-attempt-002.json"
    assert json.loads(first_path.read_text(encoding="utf-8")) == first
    assert json.loads(second_path.read_text(encoding="utf-8")) == second
    assert json.loads((tmp_path / "latest.json").read_text(encoding="utf-8")) == second


def test_released_attestation_and_parent_evidence_are_closed_and_digest_bound() -> None:
    if not (BASE / "transaction-attestation.json").exists():
        pytest.skip("single disposable rehearsal has not run yet")
    attestation = _load("transaction-attestation.json")
    evidence = _load("rehearsal-evidence.json")

    Draft202012Validator(_load("transaction-attestation.schema.json")).validate(
        attestation
    )
    Draft202012Validator(_load("rehearsal-evidence.schema.json")).validate(evidence)
    assert rehearsal._sha256(rehearsal._json_bytes(attestation)) == (  # noqa: SLF001
        evidence["attestation_sha256"]
    )
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["hostile_mutations"]["escapes"] == 0
    assert evidence["environment"]["automatic_retries"] == 0
    assert evidence["cleanup"]["role_absent_before_teardown"] is True
    assert attestation["ordinary_admission_release_count"] == 0
    assert [item["id"] for item in attestation["scenarios"]] == list(
        rehearsal.EXPECTED_SCENARIOS
    )
    serialized = json.dumps([attestation, evidence]).lower()
    for forbidden in (
        "password",
        "postgresql://",
        "connection_url",
        "raw_output",
        "raw_exception",
        "backend_pid",
        "container_name",
        "network_name",
        "docs/branding",
    ):
        assert forbidden not in serialized


def test_failure_evidence_is_sanitized() -> None:
    failure = rehearsal._failure_evidence(  # noqa: SLF001
        rehearsal.RehearsalFailure("readback", "bounded_code", "sensitive-detail"),
        ["contract_verified"],
        {"status": "cleanup_verified", "role_absent_before_teardown": True},
    )

    serialized = json.dumps(failure)
    assert "sensitive-detail" not in serialized
    assert failure["failure"]["detail_sha256"] == rehearsal._sha256(  # noqa: SLF001
        "sensitive-detail"
    )
