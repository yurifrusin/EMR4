from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_check_in_attempt_007_redaction_cleanup_projection_diagnosis
    as diagnosis,
)


def _contract() -> dict[str, object]:
    return json.loads(diagnosis.CONTRACT_PATH.read_text(encoding="utf-8"))


def test_contract_and_exact_source_bindings_pass() -> None:
    head = diagnosis._git_head()
    diagnosis._validate_contract(_contract(), head)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(plan_source=diagnosis.PLAN_SOURCE[:7]),
        lambda value: value["expected_conflict_paths"].append("closed_boundaries.invented"),
        lambda value: value["repair_gears"].reverse(),
        lambda value: value["closed_boundaries"].update(docker_object_created=True),
        lambda value: value["source_bindings"][0].update(sha256="0" * 64),
    ],
)
def test_contract_mutations_fail_closed(mutation) -> None:  # type: ignore[no-untyped-def]
    value = copy.deepcopy(_contract())
    mutation(value)
    with pytest.raises(diagnosis.DiagnosisError):
        diagnosis._validate_contract(value, diagnosis._git_head())


def test_complete_prospective_result_key_paths_have_one_exact_conflict() -> None:
    base_contract = diagnosis._load_json(diagnosis.BASE_CONTRACT)
    paths = diagnosis.prospective_result_key_paths(
        diagnosis.BASE_SOURCE.read_text(encoding="utf-8"), base_contract
    )
    assert len(paths) >= 50
    assert diagnosis.conflict_paths(paths) == (diagnosis.EXPECTED_CONFLICT,)
    assert "cleanup.status" in paths
    assert "scenarios[].id" in paths
    assert diagnosis.EXPECTED_CONFLICT in paths


@pytest.mark.parametrize(
    ("key", "conflicts"),
    [
        ("secret", True),
        ("secret_value", True),
        ("live_secret", True),
        ("secretary", False),
        ("secrecy", False),
        ("existing_hosted_database_used", False),
    ],
)
def test_forbidden_key_predicate_exact_edges(key: str, conflicts: bool) -> None:
    assert diagnosis._key_conflicts(key) is conflicts


def test_source_owned_redactor_reproduces_exact_terminal() -> None:
    assert diagnosis.reproduce_redaction(diagnosis._load_json(diagnosis.BASE_CONTRACT)) == {
        "stage": "redaction",
        "code": "forbidden_field",
    }


def test_base_control_flow_proves_post_cleanup_escape() -> None:
    facts = diagnosis.base_control_flow(diagnosis.BASE_SOURCE.read_text(encoding="utf-8"))
    assert facts["result_constructed_inside_lifecycle_try"] is True
    assert facts["cleanup_finalized_in_finally"] is True
    assert facts["final_result_redaction_after_finally"] is True
    assert facts["base_handler_covers_final_result_redaction"] is False
    assert facts["final_result_redaction_statement_index"] > facts["lifecycle_try_statement_index"]


def test_base_control_flow_rejects_missing_final_redaction() -> None:
    source = diagnosis.BASE_SOURCE.read_text(encoding="utf-8")
    altered = source.replace(
        "    _assert_redacted(result, forbidden_values=forbidden_values)\n",
        "    pass\n",
        1,
    )
    with pytest.raises(diagnosis.DiagnosisError):
        diagnosis.base_control_flow(altered)


def test_wrapper_projection_proves_not_started_collapse() -> None:
    facts = diagnosis.wrapper_projection(
        diagnosis.WRAPPER_SOURCE.read_text(encoding="utf-8")
    )
    assert facts == {
        "caught_base_failure_forwarded_to_writer": True,
        "writer_calls_sanitizer": True,
        "sanitizer_cleanup_status": "not_started",
        "fake_stage": "redaction",
        "fake_code": "forbidden_field",
    }


def test_wrapper_projection_rejects_invented_cleanup() -> None:
    source = diagnosis.WRAPPER_SOURCE.read_text(encoding="utf-8")
    altered = source.replace('{"status": "not_started"}', '{"status": "cleanup_verified"}', 1)
    with pytest.raises(diagnosis.DiagnosisError):
        diagnosis.wrapper_projection(altered)


def test_build_evidence_is_closed_and_schema_valid() -> None:
    value = diagnosis.build_evidence(_contract(), diagnosis._git_head())
    schema = diagnosis._load_json(diagnosis.SCHEMA_PATH)
    assert list(Draft202012Validator(schema).iter_errors(value)) == []
    assert value["prospective_projection"]["conflict_count"] == 1
    assert value["repair_boundary"]["attempt_008_authorized"] is False
    assert all(count == 0 for count in value["activity"].values())


def test_execute_writes_exclusively_and_check_reads_canonically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "diagnosis-evidence.json"
    monkeypatch.setattr(diagnosis, "EVIDENCE_PATH", output)
    assert diagnosis.main(["--execute"]) == 0
    first = output.read_bytes()
    assert diagnosis.main(["--check"]) == 0
    assert output.read_bytes() == first
    assert diagnosis.main(["--execute"]) == 1
    assert output.read_bytes() == first


def test_existing_evidence_binding_must_be_full_ancestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "diagnosis-evidence.json"
    output.write_text('{"source_head":"3240c0a"}', encoding="utf-8")
    monkeypatch.setattr(diagnosis, "EVIDENCE_PATH", output)
    with pytest.raises(diagnosis.DiagnosisError):
        diagnosis._evidence_binding_head(diagnosis._git_head())


def test_module_has_no_external_runtime_subprocess_surface() -> None:
    tree = ast.parse(Path(diagnosis.__file__).read_text(encoding="utf-8"))
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
