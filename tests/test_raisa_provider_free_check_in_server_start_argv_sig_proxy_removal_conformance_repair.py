from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    raisa_provider_free_check_in_server_start_argv_sig_proxy_removal_conformance_repair
    as repair,
)


def _contract() -> dict[str, object]:
    return json.loads(repair.CONTRACT_PATH.read_text(encoding="utf-8"))


def test_contract_exact_diff_and_source_profile_pass() -> None:
    historical, current = repair._validate_contract(_contract(), repair._git_head())
    assert historical.count(b'            "--sig-proxy=false",\n') == 1
    assert b"--sig-proxy=false" not in current
    profile = repair.source_profile(current.decode("utf-8"))
    assert profile["argv"] == repair.EXPECTED_ARGV
    assert profile["popen_profile"] == {
        "cwd": "ROOT",
        "stdin": "subprocess.PIPE",
        "stdout": "subprocess.DEVNULL",
        "stderr": "subprocess.DEVNULL",
        "shell": False,
    }


def test_fake_lifecycle_preserves_stdin_and_bounded_teardown() -> None:
    row = repair._fake_lifecycle()
    assert row["captured"]["argv"] == [
        "docker.exe",
        "start",
        "--attach",
        "--interactive",
        "c" * 64,
    ]
    assert row["normal"] == {
        "writes": [b"first\nsecond\n"],
        "flush_count": 1,
        "closed": False,
        "close_count": 0,
        "terminate_count": 0,
        "kill_count": 0,
    }
    attachment = row["attachment"]
    assert attachment.stdin.close_count == 1
    assert attachment.terminate_count == 1
    assert attachment.wait_count == 1
    assert attachment.kill_count == 0


def test_attestation_is_closed_and_attempt_007_denied() -> None:
    attestation = repair.build_attestation(_contract(), repair._git_head())
    schema = json.loads(repair.SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(attestation)
    assert attestation["exact_diff"]["removed_tokens"] == ["--sig-proxy=false"]
    assert attestation["exact_diff"]["other_harness_changes"] == 0
    assert attestation["repair"]["implemented"] is True
    assert attestation["repair"]["attempt_007_authorized"] is False
    assert all(value == 0 for value in attestation["closed_boundaries"].values())


def test_schema_rejects_free_form_or_broader_repair() -> None:
    attestation = repair.build_attestation(_contract(), repair._git_head())
    schema = json.loads(repair.SCHEMA_PATH.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(attestation)
    mutated["repair"]["surface"] = "redesign Docker lifecycle"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(mutated)
    mutated = copy.deepcopy(attestation)
    mutated["repair"]["attempt_007_authorized"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(mutated)


def test_contract_rejects_short_git_diff_and_argv_mutations() -> None:
    head = repair._git_head()
    contract = _contract()
    mutated = copy.deepcopy(contract)
    mutated["plan_source"] = mutated["plan_source"][:7]
    with pytest.raises(repair.RepairError, match="full Git object"):
        repair._validate_contract(mutated, head)
    mutated = copy.deepcopy(contract)
    mutated["expected_argv"].insert(-1, "--sig-proxy=false")
    with pytest.raises(repair.RepairError, match="expected argv mismatch"):
        repair._validate_contract(mutated, head)
    mutated = copy.deepcopy(contract)
    mutated["post_repair_harness_sha256"] = "0" * 64
    with pytest.raises(repair.RepairError, match="post-repair harness drift"):
        repair._validate_contract(mutated, head)


def test_plan_and_threat_freeze_no_occupied_authority() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "docs" / (
        "raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-"
        "conformance-repair-plan.md"
    )).read_text(encoding="utf-8")
    threat = (root / "docs" / "security" / (
        "raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-"
        "conformance-repair-threat-model-delta.md"
    )).read_text(encoding="utf-8")
    assert "only executable harness edit is deletion" in plan
    assert "No Docker object command is authorised" in plan
    assert "Any attempt 007 requires a new operation" in plan
    assert "adds no Docker object" in threat
    assert "separately planned one-run attempt-007 question" in threat
