from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_proof_module_relative_specifier_repair
    as repair,
)


def test_real_repair_is_exact_and_provider_free() -> None:
    evidence = repair.build_evidence(repair.TARGET_PATH.read_bytes())
    assert evidence["status"] == "passed"
    assert all(evidence["source_checks"].values())
    assert all(evidence["profile_checks"].values())
    assert all(count == 0 for count in evidence["zero_activity"].values())


def test_duplicate_relative_row_fails_closed() -> None:
    source = repair.TARGET_PATH.read_bytes()
    duplicate = source.replace(
        f"name: {repair.SENTINEL}".encode(),
        f"name: {repair.SENTINEL}\n      name: {repair.SENTINEL}".encode(),
        1,
    )
    evidence = repair.build_evidence(duplicate)
    assert evidence["status"] == "failed_closed"
    assert evidence["source_checks"]["sentinel_relative_row_exactly_once"] is False


def test_former_absolute_author_fails_closed() -> None:
    source = repair.TARGET_PATH.read_bytes().replace(
        f"name: {repair.SENTINEL}".encode(), repair.OLD_SENTINEL.encode(), 1
    )
    evidence = repair.build_evidence(source)
    assert evidence["status"] == "failed_closed"
    assert evidence["source_checks"]["former_sentinel_absolute_author_absent"] is False


def test_initial_and_changed_profile_projection_are_exact() -> None:
    root = Path("C:/synthetic-native-worker")
    initial = repair.subject.profile_patch(root, 43123, changed=False).decode()
    changed = repair.subject.profile_patch(root, 43123, changed=True).decode()
    assert initial.count(f"name: {repair.SENTINEL}") == 1
    assert f"name: {repair.RUNNER}" not in initial
    assert changed.count(f"name: {repair.SENTINEL}") == 1
    assert changed.count(f"name: {repair.RUNNER}") == 1
    assert repair.ABSOLUTE_TARGET.search(initial) is None
    assert repair.ABSOLUTE_TARGET.search(changed) is None


def test_contract_and_generated_evidence_are_schema_valid() -> None:
    contract_schema = json.loads(
        (repair.CONTINUITY_ROOT / "contract.schema.json").read_text(
            encoding="utf-8"
        )
    )
    contract = json.loads(repair.CONTRACT_PATH.read_text(encoding="utf-8"))
    evidence_schema = json.loads(
        (repair.CONTINUITY_ROOT / "evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = json.loads(
        (repair.CONTINUITY_ROOT / "repair-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)


def test_runner_contains_no_execution_or_network_entry_point() -> None:
    source = Path(repair.__file__).read_text(encoding="utf-8")
    forbidden = (
        "subprocess",
        "Popen(",
        "requests.",
        "urllib.",
        "socket.",
        "http.client",
        "os.system",
        "node ",
        "dsh ",
    )
    assert all(token not in source for token in forbidden)


def test_plan_preserves_all_closed_boundaries() -> None:
    plan = (
        repair.REPO_ROOT
        / "docs"
        / "deepseek-native-harness-provider-free-proof-module-relative-"
        "specifier-repair-plan.md"
    ).read_text(encoding="utf-8")
    for token in (
        "provider-free two-row profile repair only",
        "no Node, Harness, broker, worker, model, provider or network process/request",
        "no ordinary-practice enablement or generic-status `Arrived` change",
        "no production runtime, deployment, release, Pages or protected-ref movement",
        "explicit-path staging only",
    ):
        assert token in plan
