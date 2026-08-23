from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_read_only_check_in_environment_secret_posture_gap_decomposition
    as subject,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-read-only-canonical-check-in-environment-manifest-operational-secret-posture-evidence-gap-decomposition-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-read-only-canonical-check-in-environment-manifest-operational-secret-posture-evidence-gap-decomposition-threat-model-delta.md"
CONTRACT = ROOT / subject.CONTRACT_PATH
SCHEMA = ROOT / subject.SCHEMA_PATH
EVIDENCE = ROOT / subject.EVIDENCE_PATH
REPORT = ROOT / subject.REPORT_PATH


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "\r" not in text
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_contract_and_schema_are_closed_and_valid() -> None:
    contract = _json(CONTRACT)
    schema = _json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    assert schema["additionalProperties"] is False
    assert contract["schema_version"] == subject.SCHEMA_VERSION
    assert _sha(CONTRACT) == subject.CONTRACT_RAW_SHA256
    assert _sha(SCHEMA) == subject.CONTRACT_SCHEMA_SHA256


def test_reviewer_reproduces_released_evidence_and_report() -> None:
    observed = subject.run_review(ROOT, verify_outputs=True)
    assert observed == _json(EVIDENCE)
    assert subject.render_report(observed) == REPORT.read_text(encoding="utf-8")


def test_readiness_remains_11_0_1_and_not_ready() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["readiness_result"] == {
        "blocking_gap": 0,
        "operational_evidence_gap": 1,
        "result": "gap_decomposed_not_satisfied",
        "satisfied": 11,
        "verdict": subject.VERDICT,
    }
    assert evidence["source_findings"]["sole_gap_retained"] is True


def test_closed_taxonomy_has_exact_counts_and_statuses() -> None:
    contract = _json(CONTRACT)
    counts, edge_count = subject.validate_graph(contract)
    assert counts == subject.EXPECTED_CLASS_COUNTS
    assert edge_count == 39
    assert contract["node_classes"] == list(subject.NODE_CLASSES)
    for node in contract["nodes"]:
        status, repository_only = subject.EXPECTED_STATUS[node["class"]]
        assert node["status"] == status
        assert node["repository_only"] is repository_only


def test_dependency_graph_is_acyclic_and_references_known_nodes() -> None:
    nodes = _json(CONTRACT)["nodes"]
    graph = {node["id"]: tuple(node["depends_on"]) for node in nodes}
    known = set(graph)
    assert all(set(dependencies) <= known for dependencies in graph.values())
    subject.validate_graph(_json(CONTRACT))


def test_external_facts_are_exact_and_cannot_be_replaced_by_repository_evidence() -> None:
    contract = _json(CONTRACT)
    closure = contract["gap_closure_rule"]
    assert closure["required_external_fact_ids"] == list(subject.EXTERNAL_FACTS)
    assert closure["all_required"] is True
    assert closure["repository_documentation_or_synthetic_substitution_allowed"] is False
    assert closure["this_tranche_closes_gap"] is False
    by_id = {node["id"]: node for node in contract["nodes"]}
    assert all(by_id[node_id]["class"] == "external_operational_fact" for node_id in subject.EXTERNAL_FACTS)
    assert all(by_id[node_id]["status"] == "absent" for node_id in subject.EXTERNAL_FACTS)


def test_human_decisions_remain_unselected_and_attention_is_not_premature() -> None:
    contract = _json(CONTRACT)
    human = [node for node in contract["nodes"] if node["class"] == "human_owned_external_decision"]
    assert len(human) == 5
    assert all(node["status"] == "unselected" for node in human)
    assert contract["human_attention"] == {
        "required_now": False,
        "trigger": "immediately_before_required_external_selection_or_lasting_action",
        "ceremonial_pause_allowed": False,
    }


def test_next_tranche_owns_only_three_repository_nodes() -> None:
    contract = _json(CONTRACT)
    next_operation = contract["next_operation"]
    assert next_operation["owned_node_ids"] == list(subject.NEXT_OWNED_NODES)
    assert next_operation["product_admission_seam_in_scope"] is False
    assert next_operation["external_fact_or_human_decision_in_scope"] is False
    by_id = {node["id"]: node for node in contract["nodes"]}
    assert all(by_id[node_id]["class"] == "repository_engineering_prerequisite" for node_id in subject.NEXT_OWNED_NODES)


def test_architecture_still_contains_zero_operational_population() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["source_findings"]["architecture_population_zero"] is True
    assert evidence["source_findings"]["reference_only_secret_slots_retained"] is True
    assert evidence["source_findings"]["deny_only_break_glass_retained"] is True
    assert evidence["source_findings"]["evaluator_has_no_admission_or_runtime_capability"] is True


def test_every_source_binding_matches_strict_canonical_bytes() -> None:
    contract = _json(CONTRACT)
    observed = tuple((item["path"], item["sha256"]) for item in contract["inputs"])
    assert observed == subject.INPUT_BINDINGS
    for relative, digest in subject.INPUT_BINDINGS:
        assert subject.canonical_sha256(ROOT, relative) == digest


def test_every_git_binding_is_full_and_ancestral() -> None:
    contract = _json(CONTRACT)
    bindings = {"planning_source": contract["planning_source"], **contract["accepted_git_objects"]}
    assert len(bindings) == 5
    for object_id in bindings.values():
        assert len(object_id) == 40
        int(object_id, 16)
        assert subject.git_object_is_ancestor(ROOT, object_id)


def test_hostile_contract_mutations_reject_without_escape() -> None:
    rejected = subject.hostile_mutations(_json(CONTRACT), ROOT)
    assert rejected == 142
    assert rejected >= 128


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda value: value.update({"planning_source": value["planning_source"][:7]}), "planning source changed"),
        (lambda value: value["nodes"][8].update({"class": "human_owned_external_decision"}), "contract semantics changed"),
        (lambda value: value["gap_closure_rule"].update({"this_tranche_closes_gap": True}), "contract semantics changed"),
        (lambda value: value["human_attention"].update({"required_now": True}), "contract semantics changed"),
    ],
)
def test_semantic_authority_mutations_fail_closed(mutation, expected_error: str) -> None:
    candidate = copy.deepcopy(_json(CONTRACT))
    mutation(candidate)
    with pytest.raises(subject.ContractError, match=expected_error):
        subject.validate_contract(candidate, ROOT, check_sources=False)


def test_schema_rejects_unknown_fields_and_free_form_classes() -> None:
    schema = _json(SCHEMA)
    validator = Draft202012Validator(schema)
    unknown = copy.deepcopy(_json(CONTRACT))
    unknown["free_form"] = True
    assert list(validator.iter_errors(unknown))
    free_class = copy.deepcopy(_json(CONTRACT))
    free_class["nodes"][0]["class"] = "descriptive_stage"
    assert list(validator.iter_errors(free_class))


def test_plan_and_threat_freeze_exact_stopping_rule() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for token in (
        "gap_decomposed_not_satisfied",
        "not_ready_for_ordinary_practice_admission",
        "repository_engineering_prerequisite",
        "external_operational_fact",
        "human_owned_external_decision",
        "preflight receipt's existing `git_refs_snapshot`",
    ):
        assert token in plan
    assert "architecture or synthetic evidence closes the gap" in " ".join(plan.split())
    assert "Those are deliberately irreducible operational facts and decisions" in threat


def test_review_does_not_write_or_open_forbidden_surfaces() -> None:
    before = {path: _sha(path) for path in (CONTRACT, SCHEMA, EVIDENCE, REPORT)}
    evidence = subject.run_review(ROOT, verify_outputs=True)
    after = {path: _sha(path) for path in (CONTRACT, SCHEMA, EVIDENCE, REPORT)}
    assert before == after
    assert all(value is False for value in evidence["closed_boundaries"].values())
    assert all(".env" not in relative for relative, _ in subject.INPUT_BINDINGS)
    script = Path(subject.__file__).read_text(encoding="utf-8")
    assert "import app" not in script
    assert "os.environ" not in script


def test_only_authorised_unmounted_normalizer_changed_since_plan_freeze() -> None:
    paths = [
        "app",
        "docs/api-spine",
        "docs/diary",
        "EMR4 Sidebar",
        ".env.example",
    ]
    process = subprocess.run(
        ["git", "diff", "--name-only", f"{subject.PLAN_SOURCE}..HEAD", "--", *paths],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert process.returncode == 0
    assert process.stdout.splitlines() == [
        "app/services/appointment_check_in_environment_manifest.py"
    ]


def test_workflow_uses_existing_preflight_snapshot_not_new_summary_layer() -> None:
    workflow = _json(CONTRACT)["workflow_control"]
    assert workflow == {
        "git_acceptance_source": "preflight_git_refs_snapshot_only",
        "ad_hoc_composite_powershell_git_summary_is_acceptance_input": False,
        "new_git_summary_control_layer_added": False,
    }
