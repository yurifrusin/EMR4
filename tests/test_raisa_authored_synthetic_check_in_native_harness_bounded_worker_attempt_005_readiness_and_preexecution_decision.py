from __future__ import annotations

import inspect
import subprocess

import pytest

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_005_readiness_and_preexecution_decision
    as subject,
)


def test_plan_and_threat_freeze_process_free_boundary() -> None:
    paths = (
        subject.REPO_ROOT / "docs" / f"{subject.OPERATION_ID}-plan.md",
        subject.REPO_ROOT
        / "docs"
        / "security"
        / f"{subject.OPERATION_ID}-threat-model-delta.md",
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-21" in text
        assert "Timestamp: 2026-08-21T" in text
        assert "+10:00" in text
        assert (
            "no_ordinary_practice_enablement_feature_flag_allowlist_or_"
            "command_mounting"
        ) in text


def test_attempt_identity_is_fifth_fresh_and_exact() -> None:
    value = subject.attempt_configuration()
    assert value["operation_id"].endswith("attempt-005")
    assert value["attempt_id"] == "deepseek-native-synthetic-window-worker-005"
    assert value["work_order_id"] == "wo-synthetic-native-window-worker-005"
    assert value["lease_id"] == "lease-synthetic-native-window-worker-005"
    assert len(value["paths"]) == 22
    assert all(path.parent == subject.ATTEMPT_EVIDENCE_ROOT for path in value["paths"])


def test_git_reader_only_launches_git(monkeypatch: pytest.MonkeyPatch) -> None:
    original = subprocess.run
    calls: list[list[str]] = []

    def guarded(
        argv: list[str], *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        assert argv[0] == "git"
        calls.append(argv)
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subject.subprocess, "run", guarded)
    assert len(subject.git("rev-parse", "HEAD")) == 40
    assert calls


def test_contract_fixes_one_execution_and_zero_recovery() -> None:
    contract = subject.load_contract()
    assert contract["limits"] == {
        "native_processes": 1,
        "sessions": 1,
        "turns": 1,
        "provider_requests": 1,
        "model_tool_calls": 1,
        "maximum_output_tokens": 4096,
        "upstream_timeout_seconds": 300,
        "native_deadline_seconds": 420,
        "automatic_retries": 0,
        "resumes": 0,
        "fallbacks": 0,
        "auxiliary_models": 0,
        "second_workers": 0,
    }
    assert len(contract["startup_lineage"]) == 15


def test_lineage_digest_mismatch_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = subject.load_contract()
    monkeypatch.setattr(subject, "file_sha256", lambda _path: "0" * 64)
    with pytest.raises(subject.ReadinessError, match="startup_lineage_digest_mismatch"):
        subject._lineage_by_role(contract)


def test_repaired_composition_is_exact_and_process_free() -> None:
    contract = subject.load_contract()
    value = subject.validate_components(contract)
    composition = value["composition"]
    assert composition["initial_sentinel_rows"] == 1
    assert composition["initial_runner_rows"] == 0
    assert composition["changed_sentinel_rows"] == 1
    assert composition["changed_runner_rows"] == 1
    assert composition["relative_sentinel"] is True
    assert composition["relative_runner"] is True
    assert value["package_version"] == "0.1.0-rc.7"
    assert value["materialization_process_count"] == 0


def test_terminal_projection_includes_wrong_identity_denial() -> None:
    value = subject.validate_terminal_projection()
    assert value["absent"] == "structured_diagnostic_absent"
    assert value["malformed"] == "structured_diagnostic_invalid"
    assert value["wrong_identity"] == "structured_diagnostic_invalid"
    assert value["valid_structured_accepted"] is True
    assert set(value["lifecycle_checks"].values()) == {True}


def test_readiness_source_has_no_native_or_provider_launcher() -> None:
    source = inspect.getsource(subject)
    assert "subprocess.Popen" not in source
    assert "api.deepseek.com" not in source
    assert "DEEPSEEK_API_KEY" not in source
    assert set(subject.validate_process_free_source().values()) == {True}


def test_stored_evidence_is_schema_bound_and_authorizes_no_execution() -> None:
    value = subject.validate_artifacts()
    fresh = subject.deterministic_evidence()
    for key in value:
        if key not in {"evaluated_source", "git_refs"}:
            assert value[key] == fresh[key]
    assert value["result"] == "pass"
    assert value["decision"] == (
        "ready_for_one_separately_checkpointed_occupied_attempt_005"
    )
    assert set(value["process_boundary"].values()) == {0}
    assert value["occupied_attempt_authorized"] is False
    assert value["readiness_clockwork_reusable_for_execution"] is False
    assert value["fresh_post_closeout_clockwork_reading_required"] is True
    assert value["fresh_attempt"]["output_path_count"] == 22
