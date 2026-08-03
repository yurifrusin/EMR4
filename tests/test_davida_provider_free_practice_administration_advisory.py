"""Deterministic regression suite for Davida's advisory proofreader."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.schemas.practice_administration_advisory import (
    ADVISORY_OPERATIONS,
    AdvisoryCandidateAdapter,
    AdvisoryDraftAdapter,
    OPERATION_EXPLAIN,
    PARENT_PROPOSAL_OPERATIONS,
    PracticeAdministrationAdvisoryResultAdapter,
    RELEASED_AUTHORITY_CEILING,
)
from app.services.practice.practice_administration_advisory_proofreader import (
    proofread_advisory_candidate,
)
from scripts.davida_provider_free_practice_administration_advisory_acceptance import (
    _candidate,
    _canonical,
    _json_clone,
    _rehash_context,
    _sample_context,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.json"
SCHEMA = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.schema.json"
PLAN = ROOT / "docs/davida-provider-free-practice-administration-advisory-plan.md"
DESIGN = ROOT / "docs/davida-provider-free-practice-administration-advisory-design.md"
THREAT = ROOT / "docs/security/davida-provider-free-practice-administration-advisory-threat-model-delta.md"
SCHEMA_SOURCE = ROOT / "app/schemas/practice_administration_advisory.py"
PROOFREADER_SOURCE = ROOT / "app/services/practice/practice_administration_advisory_proofreader.py"
ACCEPTANCE = ROOT / "scripts/davida_provider_free_practice_administration_advisory_acceptance.py"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _result(candidate: object, context: object) -> dict:
    result = proofread_advisory_candidate(
        candidate=candidate,  # type: ignore[arg-type]
        context_frame=context,  # type: ignore[arg-type]
    )
    PracticeAdministrationAdvisoryResultAdapter.validate_python(result)
    return result


def _mutated(value: object) -> object:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if value is None:
        return "tampered"
    return f"{value}__tampered"


def _leaf_paths(value: object, prefix: tuple[object, ...] = ()) -> list[tuple[tuple[object, ...], object]]:
    leaves: list[tuple[tuple[object, ...], object]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            leaves.extend(_leaf_paths(child, prefix + (key,)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            leaves.extend(_leaf_paths(child, prefix + (index,)))
    else:
        leaves.append((prefix, value))
    return leaves


def _set_path(value: object, path: tuple[object, ...], replacement: object) -> None:
    current = value
    for key in path[:-1]:
        current = current[key]  # type: ignore[index]
    current[path[-1]] = replacement  # type: ignore[index]


def test_machine_contract_validates_and_every_leaf_is_exact() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    contract = _json(CONTRACT)
    schema = _json(SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(contract)
    for path, value in _leaf_paths(contract):
        candidate = copy.deepcopy(contract)
        _set_path(candidate, path, _mutated(value))
        assert list(validator.iter_errors(candidate)), f"schema admitted mutation at {path}"


def test_machine_schema_closes_every_object_shape() -> None:
    schema = _json(SCHEMA)
    open_objects: list[str] = []

    def walk(value: object, path: str = "$") -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                open_objects.append(path)
            for key, child in value.items():
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(schema)
    assert not open_objects


def test_closed_operation_vocabulary_and_frozen_candidate_models() -> None:
    assert ADVISORY_OPERATIONS == {
        "ADVISORY_EXPLAIN_DIRECTORY",
        "ADVISORY_SUMMARIZE_DIRECTORY",
    }
    assert ADVISORY_OPERATIONS.isdisjoint(PARENT_PROPOSAL_OPERATIONS)
    context = _sample_context()
    parsed = AdvisoryCandidateAdapter.validate_python(_candidate(context))
    with pytest.raises(Exception):
        parsed.operation = OPERATION_EXPLAIN


def test_summary_and_explain_release_only_derived_structured_fields() -> None:
    context = _sample_context()
    summary = _result(_candidate(context), context)
    assert summary["verdict"] == "released"
    assert summary["draft"]["payload"] == {
        "practitioner_count": 2,
        "location_count": 2,
        "practitioners_with_role_count": 1,
        "practitioners_with_default_location_count": 1,
    }
    explain = _result(
        _candidate(
            context,
            operation=OPERATION_EXPLAIN,
            subject_kind="practitioner",
            subject_ref="prac_synth_0001",
        ),
        context,
    )
    draft = AdvisoryDraftAdapter.validate_python(explain["draft"])
    assert draft.authority_label == "model_interpretation"
    assert draft.evidence_mode == "provider_free_unoccupied_authored_synthetic"
    assert draft.presentation == "structured_fields_only_no_html_or_markdown"
    assert draft.authority_ceiling.model_dump() == RELEASED_AUTHORITY_CEILING
    assert "html" not in explain["draft"]["payload"]
    assert "markdown" not in explain["draft"]["payload"]
    assert "claim" not in explain["draft"]["payload"]


def test_grounding_digest_binds_context_paths_and_payload() -> None:
    context = _sample_context()
    candidate = _candidate(context)
    result = _result(candidate, context)
    draft = result["draft"]
    material = {
        "context_revision": context["content_revision"],
        "grounding_paths": sorted(draft["grounding"]["grounding_paths"]),
        "payload": draft["payload"],
    }
    expected = hashlib.sha256(_canonical(material).encode("utf-8")).hexdigest()
    assert draft["grounding"]["grounding_digest"] == expected
    changed = copy.deepcopy(material)
    changed["payload"]["practitioner_count"] += 1
    assert hashlib.sha256(_canonical(changed).encode("utf-8")).hexdigest() != expected


def test_rejection_is_atomic_and_coercion_fails_closed() -> None:
    context = _sample_context()
    for field in (
        "writes_authorized",
        "proposal_authorized",
        "confirmation_authorized",
    ):
        candidate = _candidate(context)
        candidate[field] = 0
        result = _result(candidate, context)
        assert result["verdict"] == "rejected"
        assert result["reason"] == "candidate_noncanonical"
        assert "draft" not in result
        assert result["repair_performed"] is False
        assert result["retry_authorized"] is False


def test_context_revision_and_recomputed_boundary_tampering_fail_closed() -> None:
    context = _sample_context()
    old_revision = _json_clone(context)
    old_revision["frames"]["locations"]["rows"][0]["name"] = "Tampered"
    result = _result(_candidate(context), old_revision)
    assert result["reason"] == "context_revision_mismatch"

    recomputed = _json_clone(context)
    recomputed["frames"]["locations"]["count"] = 1
    _rehash_context(recomputed)
    result = _result(_candidate(recomputed), recomputed)
    assert result["reason"] == "context_boundary_invalid"


def test_context_duplicate_and_dangling_refs_fail_closed() -> None:
    context = _sample_context()
    duplicate = _json_clone(context)
    duplicate["frames"]["practitioners"]["rows"].append(
        copy.deepcopy(duplicate["frames"]["practitioners"]["rows"][0])
    )
    duplicate["frames"]["practitioners"]["count"] = 3
    _rehash_context(duplicate)
    assert _result(_candidate(duplicate), duplicate)["verdict"] == "rejected"

    dangling = _json_clone(context)
    dangling["frames"]["practitioners"]["rows"][0][
        "default_location_ref"
    ] = "loc_synth_9999"
    _rehash_context(dangling)
    assert _result(_candidate(dangling), dangling)["verdict"] == "rejected"


def test_proofreader_and_schema_have_no_effectful_dependency_or_clock_read() -> None:
    forbidden_imports = {
        "sqlalchemy",
        "requests",
        "httpx",
        "socket",
        "urllib",
        "time",
        "psycopg",
        "openai",
        "google",
    }
    for path in (SCHEMA_SOURCE, PROOFREADER_SOURCE):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        dotted_calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    dotted_calls.add(f"{node.func.value.id}.{node.func.attr}")
        assert not imports & forbidden_imports
        assert not {"datetime.now", "datetime.utcnow", "time.time"} & dotted_calls


def test_acceptance_script_passes_and_persists_only_sanitized_evidence(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"
    completed = subprocess.run(
        [sys.executable, str(ACCEPTANCE), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    evidence = json.loads(completed.stdout)
    assert evidence == _json(output)
    assert evidence["result"] == (
        "provider_free_practice_administration_advisory_proofreader_pass"
    )
    assert evidence["evidence_label"] == (
        "provider_free_unoccupied_authored_synthetic"
    )
    assert evidence["case_count"] == evidence["passed_case_count"] == 57
    assert evidence["failed_case_count"] == 0
    assert evidence["verdict_counts"] == {"released": 5, "rejected": 49}
    serialized = output.read_text(encoding="utf-8")
    for forbidden in (
        "Avery",
        "Morgan",
        "Synthetic North",
        "prac_synth",
        "loc_synth",
        "practice_synth_advisory",
        "principal_synth_advisory",
    ):
        assert forbidden not in serialized


def test_plan_design_and_threat_preserve_api_spine_and_closed_gates() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT)
    )
    normalized = " ".join(text.split())
    assert "GraphQL remains read-only" in normalized
    assert "REST commands" in normalized
    assert "provider_free_unoccupied_authored_synthetic" in text
    assert "no model/provider call" in text.lower()
    for gate in (
        "memory/RAG",
        "real identity",
        "patient/clinical/document",
        "proposal",
        "apply",
        "write",
        "deployment",
        "production",
        "release",
    ):
        assert gate in normalized
