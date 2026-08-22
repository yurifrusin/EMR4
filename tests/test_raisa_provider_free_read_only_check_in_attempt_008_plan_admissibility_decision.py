from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_read_only_check_in_attempt_008_plan_admissibility_decision
    as decision,
)


def _contract() -> dict[str, object]:
    return json.loads(decision.CONTRACT_PATH.read_text(encoding="utf-8"))


def test_contract_sources_and_closed_prerequisite_population_pass() -> None:
    contract = _contract()
    decision._validate_contract(contract, decision._git_head())
    assert len(contract["prerequisites"]) == 14  # type: ignore[arg-type]
    assert [row["id"] for row in contract["prerequisites"]] == [  # type: ignore[index]
        f"P{index:02d}" for index in range(1, 15)
    ]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(plan_source=decision.PLAN_SOURCE[:7]),
        lambda value: value["accepted_git_sources"][0].update(source="0" * 40),
        lambda value: value["prerequisites"][5].update(expected_state="satisfied"),
        lambda value: value["source_bindings"][0].update(sha256="0" * 64),
        lambda value: value["target_absent_paths"].pop(),
        lambda value: value["closed_boundaries"].update(attempt_008_plan_created=True),
    ],
)
def test_contract_mutations_fail_closed(mutation) -> None:  # type: ignore[no-untyped-def]
    value = copy.deepcopy(_contract())
    mutation(value)
    with pytest.raises(decision.DecisionError):
        decision._validate_contract(value, decision._git_head())


def test_all_accepted_evidence_signals_pass_without_runtime_action() -> None:
    decision._validate_accepted_evidence()


def test_attempt_008_exact_target_absence_is_fail_closed(tmp_path: Path) -> None:
    decision._assert_absent(["occupied"], root=tmp_path)
    (tmp_path / "occupied").mkdir()
    with pytest.raises(decision.DecisionError, match="artifact_already_exists"):
        decision._assert_absent(["occupied"], root=tmp_path)


def test_built_decision_is_schema_valid_and_not_execution_ready() -> None:
    evidence = decision.build_evidence(_contract(), decision._git_head())
    schema = decision._load_json(decision.SCHEMA_PATH)
    assert list(Draft202012Validator(schema).iter_errors(evidence)) == []
    assert evidence["verdict"] == "admissible_for_separate_plan_freeze"
    assert evidence["counts"] == {
        "prerequisite_count": 14,
        "satisfied_count": 5,
        "plan_required_count": 6,
        "preexecution_required_count": 3,
        "blocking_count": 0,
    }
    assert evidence["attempt_008"] == {
        "plan_exists": False,
        "continuity_namespace_exists": False,
        "plan_freeze_admissible": True,
        "ready_to_execute": False,
    }
    assert all(value == 0 for value in evidence["activity"].values())


def test_write_is_exclusive_and_check_is_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence = tmp_path / "decision-evidence.json"
    report = tmp_path / "decision-report.md"
    monkeypatch.setattr(decision, "EVIDENCE_PATH", evidence)
    monkeypatch.setattr(decision, "REPORT_PATH", report)
    head = decision._git_head()
    assert decision.main(["--write", "--source", head]) == 0
    first_evidence = evidence.read_bytes()
    first_report = report.read_bytes()
    assert decision.main(["--check"]) == 0
    assert evidence.read_bytes() == first_evidence
    assert report.read_bytes() == first_report
    assert decision.main(["--write", "--source", head]) == 1


def test_cli_rejects_abbreviated_or_free_form_source() -> None:
    assert decision.main(["--write", "--source", decision._git_head()[:7]]) == 1
    assert decision.main(["--check", "--source", decision._git_head()]) == 1


def test_subprocess_surface_is_git_resolution_only() -> None:
    tree = ast.parse(Path(decision.__file__).read_text(encoding="utf-8"))
    enclosing: dict[ast.AST, str] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for child in ast.walk(node):
                enclosing[child] = node.name
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert {enclosing[node] for node in calls} == {"_git_head", "_assert_ancestor"}
