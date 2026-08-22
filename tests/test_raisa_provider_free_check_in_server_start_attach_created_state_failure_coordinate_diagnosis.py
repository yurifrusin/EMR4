from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    raisa_provider_free_check_in_server_start_attach_created_state_failure_coordinate_diagnosis
    as diagnosis,
)


ROOT = Path(__file__).resolve().parents[1]
HARNESS_REPOSITORY_PATH = (
    "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_"
    "relay_free_rollback_unknown_commit_recovery_rehearsal.py"
)


def _contract() -> dict[str, object]:
    return json.loads(diagnosis.CONTRACT_PATH.read_text(encoding="utf-8"))


def _failure() -> dict[str, object]:
    return json.loads(
        (
            ROOT
            / "orchestration"
            / "continuity"
            / "raisa-provider-free-check-in-relay-free-recovery-attempt-006"
            / "rehearsal-failure-evidence.json"
        ).read_text(encoding="utf-8")
    )


def _runner(command: list[str] | tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    if tuple(command) == diagnosis.CLI_MANIFEST["docker_version"]:
        return subprocess.CompletedProcess(command, 0, "29.5.3|29.5.3\n", "")
    if tuple(command) == diagnosis.CLI_MANIFEST["docker_start_help"]:
        return subprocess.CompletedProcess(
            command,
            0,
            "Usage: docker start [OPTIONS] CONTAINER\n"
            "  -a, --attach  Attach STDOUT/STDERR\n"
            "  -i, --interactive  Attach STDIN\n",
            "",
        )
    raise AssertionError(f"unadmitted command: {command!r}")


def _historical_harness_source() -> str:
    result = subprocess.run(
        [
            "git",
            "show",
            f"7cd4d8069fc3983cdb4d2e80384e0f663e917c4e:{HARNESS_REPOSITORY_PATH}",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def _bind_historical_harness(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    historical = tmp_path / "historical_harness.py"
    historical.write_text(_historical_harness_source(), encoding="utf-8")
    monkeypatch.setattr(diagnosis, "HARNESS_PATH", historical)


def test_closed_contract_refuses_repaired_live_source_and_history_remains_exact() -> None:
    head = diagnosis._git_head()
    with pytest.raises(diagnosis.DiagnosisError, match="source binding drift"):
        diagnosis._validate_contract(_contract(), head)
    assert diagnosis.extract_start_argv(_historical_harness_source()) == (
        diagnosis.EXPECTED_ARGV
    )


def test_cli_manifest_is_read_only_and_object_free() -> None:
    assert diagnosis.CLI_MANIFEST == {
        "docker_version": (
            "docker.exe",
            "version",
            "--format",
            "{{.Client.Version}}|{{.Server.Version}}",
        ),
        "docker_start_help": ("docker.exe", "start", "--help"),
    }
    flattened = [token for command in diagnosis.CLI_MANIFEST.values() for token in command]
    for prohibited in (
        "create",
        "run",
        "attach",
        "exec",
        "inspect",
        "stop",
        "kill",
        "rm",
        "prune",
        "pull",
        "push",
        "login",
        "build",
    ):
        assert prohibited not in flattened


def test_deterministic_evidence_selects_exact_cli_surface_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _bind_historical_harness(monkeypatch, tmp_path)
    evidence = diagnosis.build_evidence(
        contract=_contract(),
        head=diagnosis._git_head(),
        runner=_runner,
    )
    assert evidence["coordinate"] == "cli_option_surface_mismatch"
    assert evidence["cli_evidence"]["advertised_options"] == {
        "attach": True,
        "interactive": True,
        "sig_proxy": False,
    }
    assert evidence["source_coordinate"]["unsupported_options"] == ["--sig-proxy"]
    assert evidence["repair"] == {
        "surface": "remove_unsupported_sig_proxy_option_from_docker_start_argv",
        "implemented": False,
        "attempt_007_authorized": False,
    }
    assert evidence["closed_boundaries"] == {
        "docker_object_commands": 0,
        "postgresql_processes": 0,
        "sql_or_database_attempts": 0,
        "provider_requests": 0,
        "product_effects": 0,
        "ordinary_admission_releases": 0,
    }


def test_classifier_uses_only_closed_coordinates() -> None:
    failure = _failure()
    assert diagnosis.classify_coordinate(
        advertised_options={"attach": True, "interactive": True, "sig_proxy": False},
        source_argv=diagnosis.EXPECTED_ARGV,
        failure=failure,
    ) == "cli_option_surface_mismatch"
    assert diagnosis.classify_coordinate(
        advertised_options={"attach": True, "interactive": True, "sig_proxy": True},
        source_argv=diagnosis.EXPECTED_ARGV,
        failure=failure,
    ) == "composite_start_attach_exited_while_oci_created"
    contradictory = copy.deepcopy(failure)
    contradictory["server_post_readiness"]["running"] = True
    assert diagnosis.classify_coordinate(
        advertised_options={"attach": True, "interactive": True, "sig_proxy": False},
        source_argv=diagnosis.EXPECTED_ARGV,
        failure=contradictory,
    ) == "insufficient_closed_evidence"


def test_schema_rejects_free_form_coordinate_and_raw_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _bind_historical_harness(monkeypatch, tmp_path)
    evidence = diagnosis.build_evidence(
        contract=_contract(),
        head=diagnosis._git_head(),
        runner=_runner,
    )
    schema = json.loads(diagnosis.SCHEMA_PATH.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(evidence)
    mutated["coordinate"] = "docker probably disliked the command"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(mutated)
    mutated = copy.deepcopy(evidence)
    mutated["cli_evidence"]["raw_stderr"] = "dynamic text"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(mutated)


def test_contract_rejects_command_and_digest_mutation() -> None:
    head = diagnosis._git_head()
    contract = _contract()
    mutated = copy.deepcopy(contract)
    mutated["cli_manifest"]["docker_start_help"] = ["docker.exe", "start", "container-id"]
    with pytest.raises(diagnosis.DiagnosisError, match="CLI manifest mismatch"):
        diagnosis._validate_contract(mutated, head)
    mutated = copy.deepcopy(contract)
    mutated["source_bindings"][0]["sha256"] = "0" * 64
    with pytest.raises(diagnosis.DiagnosisError, match="source binding drift"):
        diagnosis._validate_contract(mutated, head)


def test_read_only_runner_rejects_any_unlisted_command() -> None:
    with pytest.raises(diagnosis.DiagnosisError, match="outside the read-only CLI manifest"):
        diagnosis._run_read_only(("docker.exe", "start", "container-id"))
