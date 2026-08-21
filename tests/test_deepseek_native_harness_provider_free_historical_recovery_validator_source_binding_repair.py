from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts import (
    deepseek_native_harness_provider_free_historical_recovery_validator_source_binding_repair
    as repair,
)


def _contract() -> dict[str, object]:
    return repair.validate_contract(repair._load_json(repair.CONTRACT_PATH))


def test_plan_freezes_scope_parallelism_and_full_git_binding() -> None:
    plan = (
        Path(repair.REPO_ROOT)
        / "docs"
        / (
            "deepseek-native-harness-provider-free-historical-recovery-"
            "validator-source-binding-repair-plan.md"
        )
    ).read_text(encoding="utf-8")
    assert "Status: `frozen`" in plan
    assert "12d8758fee2504435ca2b4ccf6225b9d7a86a6a1" in plan
    assert "**DeepSeek:** `not_applicable`" in plan
    assert "**Gemini:** `not_applicable`" in plan
    assert "**Native subagents:** `declined`" in plan
    assert "no_ordinary_practice_enablement_feature_flag_allowlist" in plan


def test_contract_and_evidence_are_closed_and_current() -> None:
    contract = _contract()
    assert len(contract["historical_source_commit"]) == 40
    value = repair.validate_artifacts()
    assert value["result"] == "pass"
    assert value["source_blob_count"] == 7
    assert value["historical_artifact_count"] == 8
    assert value["boundary"]["local_git_subprocess_count"] == 9
    assert value["boundary"]["provider_request_count"] == 0


@pytest.mark.parametrize(
    "mutation",
    ["abbreviated_commit", "wrong_hash", "wrong_path", "extra_field"],
)
def test_hostile_contract_mutations_fail_closed(mutation: str) -> None:
    value = deepcopy(repair._load_json(repair.CONTRACT_PATH))
    if mutation == "abbreviated_commit":
        value["historical_source_commit"] = value["historical_source_commit"][:7]
    elif mutation == "wrong_hash":
        path = next(iter(value["historical_source_sha256"]))
        value["historical_source_sha256"][path] = "0" * 64
    elif mutation == "wrong_path":
        path, digest = next(iter(value["historical_source_sha256"].items()))
        del value["historical_source_sha256"][path]
        value["historical_source_sha256"]["docs/not-reviewed.md"] = digest
    else:
        value["unreviewed"] = True
    with pytest.raises(repair.SourceBindingRepairError):
        repair.validate_contract(value)


def test_exact_historical_git_blobs_match_and_are_ancestral() -> None:
    result = repair.verify_historical_sources(_contract())
    assert result == {
        "historical_source_commit": (
            "12d8758fee2504435ca2b4ccf6225b9d7a86a6a1"
        ),
        "source_blob_count": 7,
        "source_blob_sha256_exact": True,
    }


def test_helper_rejects_commit_or_source_map_substitution() -> None:
    contract = _contract()
    with pytest.raises(
        repair.SourceBindingRepairError,
        match="historical_source_commit_substituted",
    ):
        repair.verify_historical_sources(contract, source_commit="0" * 40)
    hostile = deepcopy(contract["historical_source_sha256"])
    hostile[next(iter(hostile))] = "0" * 64
    with pytest.raises(
        repair.SourceBindingRepairError,
        match="historical_source_map_substituted",
    ):
        repair.verify_historical_sources(contract, source_sha256=hostile)


def test_historical_projection_does_not_hash_mutable_current_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> str:
        del args, kwargs
        raise AssertionError("mutable_source_hash_forbidden")

    monkeypatch.setattr(repair.recovery, "file_sha256", forbidden)
    assert (
        repair.recovery.historical_source_sha256()
        == _contract()["historical_source_sha256"]
    )


def test_old_validator_passes_with_subprocess_entrypoints_forbidden() -> None:
    result = repair.verify_old_validator_without_subprocess(_contract())
    assert result == {
        "contract_and_evidence_current_check": True,
        "subprocess_forbidden_check": True,
        "old_validator_subprocess_count": 0,
    }


def test_named_historical_artifacts_remain_byte_identical() -> None:
    result = repair.verify_immutable_historical_artifacts(_contract())
    assert result == {
        "historical_artifact_count": 8,
        "historical_artifacts_unchanged": True,
    }


def test_evidence_schema_denies_extra_or_false_success() -> None:
    value = repair._load_json(repair.EVIDENCE_PATH)
    hostile = json.loads(json.dumps(value))
    hostile["boundary"]["provider_request_count"] = 1
    with pytest.raises(repair.SourceBindingRepairError, match="evidence_schema_invalid"):
        repair.validate_evidence(hostile)
    hostile = json.loads(json.dumps(value))
    hostile["raw_git_output"] = True
    with pytest.raises(repair.SourceBindingRepairError, match="evidence_schema_invalid"):
        repair.validate_evidence(hostile)
