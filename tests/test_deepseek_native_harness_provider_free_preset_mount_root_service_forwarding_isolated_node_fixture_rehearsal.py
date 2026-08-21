from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_isolated_node_fixture_rehearsal
    as subject,
)


def completed_for(value: dict | None = None, *, returncode: int = 0, stderr: str = ""):
    payload = subject.exact_fixture_outcome() if value is None else value
    return subprocess.CompletedProcess(
        args=["node", "fixture.mjs"],
        returncode=returncode,
        stdout=json.dumps(payload, separators=(",", ":")) + "\n",
        stderr=stderr,
    )


def test_contract_is_schema_valid_and_contains_no_git_object_identity():
    contract = json.loads(subject.CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(subject.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    assert subject.FULL_OID.search(json.dumps(contract, sort_keys=True)) is None
    assert contract["git_binding_policy"]["caller_authored_object_id_count"] == 0
    assert subject.load_contract() == contract


def test_exact_accepted_bridge_and_sanitizer_bindings_are_recomputed():
    contract = subject.load_contract()
    sources, inventory = subject.accepted_fixture_sources()
    assert inventory == contract["accepted_source_inventory"]
    assert inventory == {
        "derived_bridge": {
            "bytes": 1661,
            "sha256": "3a49b28174eeefd77d7efe0a00498901ac6636b637ed9dfe60aba46980df1d0b",
        },
        "accepted_sanitizer": {
            "bytes": 2439,
            "sha256": "12552925a600dc951afc30b9a738746499c7e2f4cefc9962bc05fb06780f158f",
        },
    }
    assert b"await mount.call(presetService, agentCtx, presetId);" in sources[
        "derived_bridge"
    ]
    assert b'code, detail: null' in sources["accepted_sanitizer"]
    assert b'PRESET_MOUNT_UNCLASSIFIED' in sources["accepted_sanitizer"]


def test_fixture_source_is_exact_bound_and_contains_no_broader_runtime_api():
    contract = subject.load_contract()
    fixture = subject.fixture_source()
    assert subject.source_entry(fixture) == contract["fixture_source_inventory"]
    text = fixture.decode("utf-8")
    assert text.count("mountWithSanitizedTerminal") == 4
    assert text.count("process.stdout.write") == 1
    for forbidden in (
        "process.env",
        "node:fs",
        "node:child_process",
        "node:http",
        "node:https",
        "fetch(",
        ".message",
        ".stack",
        ".cause",
    ):
        assert forbidden not in text


def test_exact_fixture_outcome_has_closed_order_and_values():
    outcome = subject.exact_fixture_outcome()
    assert list(outcome) == ["schema_version", "result", "cases"]
    assert [row["case_id"] for row in outcome["cases"]] == [
        "success",
        "missing_service",
        "missing_mount",
    ]
    assert list(outcome["cases"][0]) == [
        "case_id",
        "passed",
        "terminal",
        "mount_call_count",
        "receiver_bound",
        "context_forwarded",
        "preset_id_forwarded",
    ]
    for row in outcome["cases"][1:]:
        assert list(row) == ["case_id", "passed", "terminal"]
        assert list(row["terminal"]) == ["stage", "code", "detail"]
        assert row["terminal"] == {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_UNCLASSIFIED",
            "detail": None,
        }


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (lambda value: value.update(extra=True), "fixture_result_rejected"),
        (
            lambda value: value["cases"].reverse(),
            "fixture_result_rejected",
        ),
        (
            lambda value: value["cases"][0].update(mount_call_count=2),
            "fixture_result_rejected",
        ),
        (
            lambda value: value["cases"][0].update(receiver_bound=False),
            "fixture_result_rejected",
        ),
        (
            lambda value: value["cases"][0].update(context_forwarded=False),
            "fixture_result_rejected",
        ),
        (
            lambda value: value["cases"][0].update(preset_id_forwarded=False),
            "fixture_result_rejected",
        ),
        (
            lambda value: value["cases"][1]["terminal"].update(code="DESCRIPTIVE"),
            "fixture_result_rejected",
        ),
        (
            lambda value: value["cases"][2]["terminal"].update(detail="raw"),
            "fixture_result_rejected",
        ),
    ],
)
def test_fixture_result_hostile_value_drift_fails_closed(mutator, expected_code):
    value = deepcopy(subject.exact_fixture_outcome())
    mutator(value)
    with pytest.raises(subject.IsolatedNodeFixtureError, match=expected_code):
        subject.validate_fixture_result(
            completed=completed_for(value),
            contract=subject.load_contract(),
        )


def test_fixture_result_reordered_keys_fail_closed():
    expected = subject.exact_fixture_outcome()
    reordered = {
        "result": expected["result"],
        "schema_version": expected["schema_version"],
        "cases": expected["cases"],
    }
    with pytest.raises(
        subject.IsolatedNodeFixtureError, match="fixture_result_rejected"
    ):
        subject.validate_fixture_result(
            completed=completed_for(reordered),
            contract=subject.load_contract(),
        )


@pytest.mark.parametrize(
    "completed",
    [
        completed_for(returncode=7),
        completed_for(stderr="content deliberately not admitted"),
        subprocess.CompletedProcess(
            args=["node"], returncode=0, stdout="{}\n{}\n", stderr=""
        ),
        subprocess.CompletedProcess(
            args=["node"], returncode=0, stdout="{}\r\n", stderr=""
        ),
    ],
)
def test_process_terminal_shapes_fail_before_result_admission(completed):
    with pytest.raises(
        subject.IsolatedNodeFixtureError, match="fixture_process_terminal"
    ):
        subject.validate_fixture_result(
            completed=completed,
            contract=subject.load_contract(),
        )


def test_minimum_windows_environment_is_exact_and_excludes_preload_keys():
    source = {
        "SystemRoot": "a",
        "WINDIR": "b",
        "ComSpec": "c",
        "TEMP": "d",
        "TMP": "e",
        "PATH": "not-forwarded",
        "NODE_OPTIONS": "not-forwarded",
        "EXTRA": "not-forwarded",
    }
    observed = subject.minimum_windows_environment(source)
    assert list(observed) == list(subject.WINDOWS_ENVIRONMENT_KEYS)
    assert set(observed).isdisjoint(subject.FORBIDDEN_ENVIRONMENT_KEYS)
    assert len(observed) == 5


def test_missing_minimum_environment_key_fails_before_process():
    source = {key: key for key in subject.WINDOWS_ENVIRONMENT_KEYS[:-1]}
    with pytest.raises(
        subject.IsolatedNodeFixtureError, match="fixture_preflight_rejected"
    ):
        subject.minimum_windows_environment(source)


def test_one_mocked_node_process_materializes_only_three_files_and_cleans_root(
    monkeypatch, tmp_path: Path
):
    contract = subject.load_contract()
    sources, _ = subject.accepted_fixture_sources()
    fixture = subject.fixture_source()
    environment = {
        key: f"synthetic-{index}"
        for index, key in enumerate(subject.WINDOWS_ENVIRONMENT_KEYS)
    }
    calls: list[dict] = []

    def fake_run(args, **kwargs):
        root = Path(kwargs["cwd"])
        calls.append({"args": args, "kwargs": kwargs, "root": root})
        assert Path(args[0]).is_absolute()
        assert Path(args[1]).name == subject.FIXTURE_FILENAME
        assert sorted(path.name for path in root.iterdir()) == sorted(
            [
                subject.BRIDGE_FILENAME,
                subject.SANITIZER_FILENAME,
                subject.FIXTURE_FILENAME,
            ]
        )
        assert (root / subject.BRIDGE_FILENAME).read_bytes() == sources[
            "derived_bridge"
        ]
        assert (root / subject.SANITIZER_FILENAME).read_bytes() == sources[
            "accepted_sanitizer"
        ]
        assert (root / subject.FIXTURE_FILENAME).read_bytes() == fixture
        assert kwargs["env"] == environment
        assert "shell" not in kwargs
        return completed_for()

    monkeypatch.setattr(subject.subprocess, "run", fake_run)
    envelope_path = tmp_path / "process-envelope.json"
    completed, envelope = subject.run_fixture_once(
        node=tmp_path / "node.exe",
        environment=environment,
        sources=sources,
        fixture=fixture,
        candidate_source="a" * 40,
        envelope_path=envelope_path,
    )
    assert len(calls) == 1
    assert not calls[0]["root"].exists()
    assert envelope["node_process_count"] == 1
    assert envelope["fixture_root_absent"] is True
    assert envelope["stream_content_retained"] is False
    assert envelope_path.read_bytes() == subject.canonical_bytes(envelope)
    assert (
        subject.validate_fixture_result(completed=completed, contract=contract)
        == contract["expected_result"]
    )


def test_process_envelope_retains_only_stream_metrics():
    completed = completed_for()
    envelope = subject.build_process_envelope(
        candidate_source="b" * 40,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        fixture_root_absent=True,
    )
    serialized = subject.canonical_bytes(envelope)
    assert completed.stdout.encode("utf-8") not in serialized
    assert b"authored-synthetic" not in serialized
    assert envelope["stdout_sha256"] == subject.sha256_bytes(
        completed.stdout.encode("utf-8")
    )
    assert envelope["stderr_bytes"] == 0
    assert envelope["raw_runtime_detail_retained"] is False


def test_failure_terminal_is_closed_and_contains_no_detail():
    terminal = subject.build_failure_terminal(
        candidate_source="c" * 40,
        result="fixture_result_rejected",
        code="fixture_result_rejected",
        envelope_sha256="d" * 64,
    )
    assert terminal["terminal"] == {
        "stage": "isolated_node_fixture",
        "code": "fixture_result_rejected",
        "detail": None,
    }
    assert terminal["further_process_authorized"] is False


def test_evidence_schema_admits_only_the_exact_closed_boundary():
    contract = subject.load_contract()
    sources, inventory = subject.accepted_fixture_sources()
    del sources
    envelope = subject.build_process_envelope(
        candidate_source="e" * 40,
        returncode=0,
        stdout=json.dumps(contract["expected_result"], separators=(",", ":"))
        + "\n",
        stderr="",
        fixture_root_absent=True,
    )
    evidence = subject.build_evidence(
        contract=contract,
        git_binding={
            "policy": "machine_resolved_only",
            "caller_authored_object_id_count": 0,
            "planning_source_commit": "f" * 40,
            "candidate_source_commit": "e" * 40,
            "planning_source_is_ancestor_of_candidate": True,
            "branch": "codex/ariadne-bernie-davida-parallel-seam",
            "branch_origin_aligned": True,
            "protected_refs_aligned": True,
            "tracked_worktree_clean": True,
            "docs_branding_preserved": True,
        },
        source_inventory=inventory,
        fixture_inventory=subject.source_entry(subject.fixture_source()),
        outcome=contract["expected_result"],
        process_envelope=envelope,
    )
    assert evidence["result"] == "isolated_node_fixture_pass"
    assert evidence["process_boundary"]["node_process_count"] == 1
    assert all(
        evidence["process_boundary"][name] == 0
        for name in contract["required_zero_counters"]
    )
    assert evidence["cleanup"]["materialized_javascript_retained"] is False
    assert evidence["claim_boundary"]["native_harness_proved"] is False


def test_plan_and_threat_freeze_one_process_and_closed_successor_boundary():
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    threat = subject.THREAT_PATH.read_text(encoding="utf-8")
    assert "exactly one Node process" in plan
    assert "No second Node process" in plan
    assert "AER-0920" in plan
    assert "No generated JavaScript survives cleanup." in plan
    assert "The runner, guard, package seed, native Harness" in threat
    assert "A native attempt is not authorised by this" in plan
