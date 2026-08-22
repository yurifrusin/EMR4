from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestration_harness import check_in_rollout_runbook as runbook
from scripts.raisa_provider_free_read_only_post_check_in_admission_control_programme_orientation import (
    CLASSIFICATIONS,
    SUCCESSOR_ID,
    OrientationError,
    build_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-read-only-post-check-in-admission-control-programme-"
    "orientation"
)
EVIDENCE = CONTINUITY / "orientation-evidence.json"
CONTRACT = CONTINUITY / "contract.json"
SCHEMA = CONTINUITY / "contract.schema.json"
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
REPORT = ROOT / (
    "docs/raisa-provider-free-read-only-post-check-in-admission-control-"
    "programme-orientation.md"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_derived_evidence_is_byte_stable_and_current() -> None:
    expected = json.dumps(build_evidence(), indent=2, sort_keys=True) + "\n"
    assert EVIDENCE.read_text(encoding="utf-8") == expected


def test_contract_validates_against_closed_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(_json(SCHEMA)).validate(_json(CONTRACT))


def test_matrix_keeps_contract_and_operational_proof_distinct() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["classifications"] == CLASSIFICATIONS
    assert evidence["classification_counts"] == {
        "satisfied_accepted": 2,
        "satisfied_contract_only": 3,
        "operational_evidence_gap": 2,
        "closed_later_gate": 3,
    }
    by_dimension = {
        row["dimension"]: row["classification"]
        for row in evidence["classifications"]
    }
    assert (
        by_dimension["atomic_rollback_and_unknown_commit_recovery"]
        == "operational_evidence_gap"
    )
    assert (
        by_dimension["environment_manifest_and_operational_secret_posture"]
        == "operational_evidence_gap"
    )


def test_selected_successor_is_new_and_its_exact_target_is_absent() -> None:
    evidence = _json(EVIDENCE)
    graph = _json(GRAPH)
    assert SUCCESSOR_ID not in {node["id"] for node in graph["nodes"]}
    assert evidence["selected_successor"] == {
        "operation_id": SUCCESSOR_ID,
        "already_recorded": False,
        "owned_product_artifact": runbook.TARGET_RELATIVE_PATH,
        "product_source_change_authorized": False,
        "ordinary_enablement_authorized": False,
        "reason": "exact_default_off_closed_form_exists_and_its_canonical_api_spine_manifest_is_genuinely_absent",
    }
    assert not (ROOT / runbook.TARGET_RELATIVE_PATH).exists()


def test_closed_form_runbook_remains_default_off_and_exact() -> None:
    candidate = runbook.required_candidate_bytes()
    result = runbook.validate_candidate_bytes(candidate)
    assert result["ordinary_practice_enabled"] is False
    assert result["activation_authority"] is False
    assert result["claim"] == "runbook_contract_present_default_off"
    assert result["canonical_sha256"] == _json(EVIDENCE)["runbook_contract"][
        "closed_form_sha256"
    ]

    mutated = json.loads(candidate)
    mutated["default_posture"]["ordinary_practice_enabled"] = True
    with pytest.raises(runbook.RunbookValidationError):
        runbook.validate_candidate_bytes(runbook.canonical_bytes(mutated))


def test_missing_or_repeated_successor_fails_closed(tmp_path: Path) -> None:
    graph = _json(GRAPH)
    graph["nodes"].append(
        {
            "id": SUCCESSOR_ID,
            "status": "accepted",
            "coordinates": {"source_head": "0" * 40},
        }
    )
    graph_path = tmp_path / GRAPH.relative_to(ROOT)
    graph_path.parent.mkdir(parents=True)
    graph_path.write_text(json.dumps(graph), encoding="utf-8")

    for source in (
        ROOT / "docs/api-spine/openapi/appointment-commands.yaml",
        ROOT
        / (
            "orchestration/continuity/"
            "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
            "admission-control-architecture/contract.json"
        ),
    ):
        target = tmp_path / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())

    with pytest.raises(OrientationError, match="selected_successor_already_recorded"):
        build_evidence(tmp_path)


def test_report_states_forward_progress_and_closed_gates() -> None:
    report = " ".join(REPORT.read_text(encoding="utf-8").split())
    for phrase in (
        "The programme is moving forward",
        "The accepted clockwork prevented an actual circular successor",
        "This is a real completion step, not another diagnosis",
        "two `satisfied_accepted`",
        "three `satisfied_contract_only`",
        "two `operational_evidence_gap`",
        "three `closed_later_gate`",
        "It does not make check-in ready for ordinary practice",
    ):
        assert phrase in report
