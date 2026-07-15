"""Content-blind LC4V4Q1 recovery tests using temporary synthetic data only."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from app.services.bernie.lc4v4_authoring_quality import (
    AUTHORING_RECEIPT_SCHEMA,
    REQUIRED_RECEIPT_CATEGORIES,
    REQUIRED_CATEGORY_MIN_TOTALS,
    AuthorityToken,
    AuthoringQualityFinding,
    CanonicalFactBundle,
    RenderedTurn,
    authoring_receipt_to_dict,
    build_authoring_receipt,
    canonical_json_bytes,
    derive_expected_contract,
    stable_hash,
    validate_authoring_receipt,
    validate_entity_relation_evidence,
    validate_expected_contract_derivation,
    validate_lattice_coverage,
    validate_lc4v4_authoring_quality_isolation,
    validate_rendered_surface,
)
from app.services.bernie.lc4v4_certification import (
    ALL_ACTIONS,
    ALL_DIALOGUE_FORMS,
    ALL_DIARY_STATES,
    ALL_ENTITY_SEMANTICS,
    ALL_LANGUAGE_FORMS,
    ALL_TEMPORAL_RELATIONS,
    LC4V4_EVALUATION_ID,
    LC4V4_EVALUATOR_VERSION,
    LC4V4_GROUP_COUNT,
    LC4V4_REPORT_SCHEMA,
    LC4V4_TOTAL_SAMPLES,
    build_manifest,
    check_aggregate_report,
    check_forbidden_aggregate_keys,
    create_seal,
    reconstruct_manifest,
    run_baseline_once,
    validate_lc4v4_isolation,
    verify_manifest_against_corpus,
    verify_seal,
)


ROOT = Path(__file__).resolve().parents[1]


def _facts(**changes: Any) -> CanonicalFactBundle:
    values: dict[str, Any] = {
        "scenario_id": "temporary-synthetic-case",
        "intended_action": "create",
        "action_semantics": "intended",
        "temporal_relation": "exact",
        "normalized_values": {
            "appointment_date": "2030-01-02",
            "earliest_time": "15:00",
            "latest_time": "15:00",
            "duration_minutes": 15,
        },
        "entity_relations": {
            "patient": "exact",
            "practitioner": "exact",
            "location": "exact",
            "appointment_type": "exact",
            "duration": "exact",
        },
        "requires_clarification": False,
        "clarification_choices": (),
        "action_negated": False,
        "diary_state": "empty",
    }
    values.update(changes)
    return CanonicalFactBundle(**values)


def _rendered() -> tuple[list[RenderedTurn], list[AuthorityToken]]:
    core = "Book Margaret Thompson with Dr Shera tomorrow at 3pm"
    prefix = "Please "
    suffix = "."
    text = prefix + core + suffix
    patient_start = text.index("Margaret Thompson")
    practitioner_start = text.index("Dr Shera")
    return [
        RenderedTurn(
            turn_index=0,
            prefix=prefix,
            canonical_core=core,
            rendered_core=core,
            suffix=suffix,
            rendered_text=text,
            language_form="plain",
        )
    ], [
        AuthorityToken(
            "patient", "Margaret Thompson", True, 0,
            patient_start, patient_start + len("Margaret Thompson"),
            "Margaret Thompson",
        ),
        AuthorityToken(
            "practitioner", "Dr Shera", True, 0,
            practitioner_start, practitioner_start + len("Dr Shera"),
            "Dr Shera",
        ),
    ]


def _all_pass(findings: list[AuthoringQualityFinding]) -> bool:
    return all(finding.passed for finding in findings)


def test_rendering_and_case_sensitive_evidence_pass() -> None:
    turns, tokens = _rendered()
    findings = validate_rendered_surface(
        turns,
        tokens,
        required_field_counts={"patient": (1, 1), "practitioner": (1, 1)},
    )
    assert _all_pass(findings)


@pytest.mark.parametrize(
    "mutation,failed_category",
    [
        ("lower_core", "canonical_core_preservation"),
        ("upper_core", "canonical_core_preservation"),
        ("rendered_text", "rendered_text_composition"),
        ("patient_case", "authority_token_value"),
        ("span_drift", "source_span_value"),
        ("out_of_range", "authority_span_range"),
        ("missing_turn", "authority_turn_missing"),
        ("duplicate", "authority_token_duplicate"),
        ("overlap", "authority_span_overlap"),
    ],
)
def test_rendering_mutations_fail(mutation: str, failed_category: str) -> None:
    turns, tokens = _rendered()
    turn = turns[0]
    if mutation == "lower_core":
        turns[0] = replace(
            turn,
            rendered_core=turn.rendered_core.lower(),
            rendered_text=turn.prefix + turn.rendered_core.lower() + turn.suffix,
        )
    elif mutation == "upper_core":
        turns[0] = replace(
            turn,
            rendered_core=turn.rendered_core.upper(),
            rendered_text=turn.prefix + turn.rendered_core.upper() + turn.suffix,
        )
    elif mutation == "rendered_text":
        turns[0] = replace(turn, rendered_text=turn.rendered_text + "!")
    elif mutation == "patient_case":
        token = tokens[0]
        lowered = turn.rendered_text.replace("Margaret Thompson", "margaret thompson")
        turns[0] = replace(turn, rendered_text=lowered, rendered_core=turn.rendered_core.replace("Margaret Thompson", "margaret thompson"))
    elif mutation == "span_drift":
        tokens[0] = replace(tokens[0], source_text="Margaret Thompsom")
    elif mutation == "out_of_range":
        tokens[0] = replace(tokens[0], source_end=999)
    elif mutation == "missing_turn":
        tokens[0] = replace(tokens[0], turn_index=1)
    elif mutation == "duplicate":
        tokens.append(tokens[0])
    else:
        tokens[1] = replace(
            tokens[1], source_start=tokens[0].source_start + 2,
            source_end=tokens[0].source_end + 2,
        )
    findings = validate_rendered_surface(turns, tokens)
    assert any(not finding.passed and finding.category == failed_category for finding in findings)


def test_multi_turn_coordinates_use_the_addressed_turn() -> None:
    turns, _ = _rendered()
    second = RenderedTurn(1, "", "Actually Dr Chen", "Actually Dr Chen", ".", "Actually Dr Chen.", "plain")
    token = AuthorityToken("practitioner", "Dr Chen", True, 1, 9, 16, "Dr Chen")
    assert _all_pass(validate_rendered_surface([turns[0], second], [token]))


def test_missing_required_authority_evidence_fails() -> None:
    turns, tokens = _rendered()
    findings = validate_rendered_surface(
        turns,
        tokens,
        required_field_counts={"duration": (1, 1)},
    )
    assert any(
        finding.category == "required_authority_evidence" and not finding.passed
        for finding in findings
    )


@pytest.mark.parametrize(
    "relation,count,case_sensitive,texts,expected",
    [
        ("exact", 1, True, ["Margaret Thompson"], True),
        ("exact", 1, False, ["Margaret Thompson"], False),
        ("corrected", 2, True, ["Margaret Thompson", "Margaret Thomson"], True),
        ("corrected", 1, True, ["Margaret Thompson"], False),
        ("omitted", 0, True, [], True),
        ("omitted", 1, True, ["Margaret Thompson"], False),
        ("ambiguous", 1, False, ["the patient"], True),
        ("negated", 1, False, ["not Margaret Thompson"], True),
        ("mismatched", 1, False, ["does not match"], True),
    ],
)
def test_entity_relation_evidence(
    relation: str, count: int, case_sensitive: bool, texts: list[str], expected: bool,
) -> None:
    relations = {field: "omitted" for field in ("patient", "practitioner", "location", "appointment_type", "duration")}
    relations["patient"] = relation
    tokens = [
        AuthorityToken("patient", text, case_sensitive, 0, index * 20, index * 20 + len(text), text)
        for index, text in enumerate(texts[:count])
    ]
    findings = validate_entity_relation_evidence(relations, tokens)
    patient = [finding for finding in findings if "patient" in finding.detail]
    assert bool(patient) and all(finding.passed for finding in patient) is expected


@pytest.mark.parametrize(
    "changes,outcome,tools,authority",
    [
        ({}, "appointment_created", ("search_patients", "find_slots", "create_booking"), "read"),
        ({"diary_state": "exact_duplicate"}, "existing_booking_found", ("search_patients", "find_slots", "create_booking"), "read"),
        ({"diary_state": "overlap"}, "candidate_selection_required", ("search_patients", "find_slots", "create_booking"), "read"),
        ({"action_semantics": "ambiguous", "requires_clarification": True}, "clarification_required", ("request_clarification",), "clarify"),
        ({"action_semantics": "prohibited"}, "instruction_refused", ("search_patients", "find_slots", "create_booking", "refuse_instruction"), "refuse"),
        ({"action_negated": True}, None, ("search_patients",), "read"),
        ({"intended_action": "move"}, "appointment_moved", ("search_patients", "update_appointment"), "read"),
        ({"intended_action": "resize"}, "appointment_resized", ("search_patients", "update_appointment"), "read"),
        ({"intended_action": "cancel"}, "appointment_cancelled", ("search_patients", "update_appointment"), "read"),
        ({"intended_action": "status_change"}, "appointment_status_changed", ("search_patients", "change_appointment_status"), "read"),
        ({"intended_action": "explain_schedule"}, "schedule_explained", ("search_patients", "find_slots"), "read"),
    ],
)
def test_policy_is_derived_from_facts(
    changes: dict[str, Any], outcome: str | None, tools: tuple[str, ...], authority: str,
) -> None:
    expected = derive_expected_contract(_facts(**changes))
    assert expected.expected_outcome_kind == outcome
    assert expected.expected_tool_sequence == tools
    assert expected.expected_authority == authority


def test_expected_contract_mutations_fail_independent_derivation() -> None:
    facts = _facts()
    expected = derive_expected_contract(facts)
    mutations = [
        replace(expected, expected_tool_sequence=("wrong_tool",)),
        replace(expected, expected_outcome_kind="wrong_outcome"),
        replace(expected, expected_authority="write"),
        replace(expected, normalized_values={"duration_minutes": 999}),
        replace(expected, expected_appointment_deltas=()),
        replace(expected, expected_audit_deltas=()),
    ]
    for mutation in mutations:
        assert not _all_pass(validate_expected_contract_derivation(facts, mutation))


def _cells(count: int = 288) -> list[dict[str, str]]:
    cells: list[dict[str, str]] = []
    for index in range(count):
        quotient = index // 66
        entity_index = quotient if quotient < 4 else 4 + (index % 2)
        cells.append({
            "scenario_id": f"temporary-{index:03d}",
            "intended_action": ALL_ACTIONS[index % 6],
            "diary_state": ALL_DIARY_STATES[(index // 6) % 11],
            "entity_state": ALL_ENTITY_SEMANTICS[entity_index],
            "temporal_relation": ALL_TEMPORAL_RELATIONS[(index * 5 + index // 6) % 6],
            "dialogue_form": ALL_DIALOGUE_FORMS[(index * 3 + index // 11) % 8],
            "language_form": ALL_LANGUAGE_FORMS[(index * 5 + index // 7) % 8],
            "trajectory_type": "trajectory" if index % 4 == 3 else "single_turn",
        })
    return cells


def test_lattice_coverage_is_complete_and_distinct() -> None:
    assert _all_pass(validate_lattice_coverage(_cells()))


@pytest.mark.parametrize("mutation", ["duplicate_id", "short", "missing_category"])
def test_lattice_mutations_fail(mutation: str) -> None:
    cells = _cells()
    if mutation == "duplicate_id":
        cells[1]["scenario_id"] = cells[0]["scenario_id"]
    elif mutation == "short":
        cells.pop()
    else:
        for cell in cells:
            if cell["language_form"] == "adversarial":
                cell["language_form"] = "plain"
    assert not _all_pass(validate_lattice_coverage(cells))


def _quality_receipt(coverage: int = 288) -> dict[str, Any]:
    receipt = build_authoring_receipt(
        [
            AuthoringQualityFinding(category, True)
            for category in sorted(REQUIRED_RECEIPT_CATEGORIES)
            for _ in range(REQUIRED_CATEGORY_MIN_TOTALS[category])
        ],
        total_surfaces=288,
        surfaces_passed=288,
        surfaces_failed=0,
        distinct_coverage_cells=coverage,
    )
    return authoring_receipt_to_dict(receipt)


def test_authoring_receipt_is_aggregate_only_and_hash_bound() -> None:
    value = _quality_receipt()
    assert value["schema_version"] == AUTHORING_RECEIPT_SCHEMA
    assert "findings" not in value
    assert "detail" not in json.dumps(value)
    assert validate_authoring_receipt(value) == value
    changed = json.loads(json.dumps(value))
    changed["surfaces_passed"] = 287
    with pytest.raises(ValueError):
        validate_authoring_receipt(changed)


def test_json_bytes_are_lf_and_hash_stable() -> None:
    left = canonical_json_bytes({"b": "line1\r\nline2", "a": 1})
    right = canonical_json_bytes({"a": 1, "b": "line1\nline2"})
    assert left == right
    assert b"\r" not in left
    assert stable_hash({"b": "line1\r\nline2", "a": 1}) == stable_hash({"a": 1, "b": "line1\nline2"})


def _temporal(relation: str) -> tuple[str | None, str | None]:
    return {
        "exact": ("15:00", "15:00"),
        "not_before": ("15:00", None),
        "not_after": (None, "16:00"),
        "interval": ("14:00", "16:00"),
        "approximate": ("14:30", "15:30"),
        "unspecified": (None, None),
    }[relation]


def _scenario(index: int, group: int, position: int, multi: bool) -> dict[str, Any]:
    cell = _cells()[index]
    relation = cell["temporal_relation"]
    earliest, latest = _temporal(relation)
    utterance = "Book an appointment for Margaret Thompson with Dr Shera tomorrow at 3pm for 15 minutes."
    turns = [{"speaker": "receptionist", "utterance": utterance}]
    if multi:
        turns.append({"speaker": "receptionist", "utterance": "retain the preceding synthetic request."})
    normalized: dict[str, Any] = {"appointment_date": "2030-01-02", "duration_minutes": 15}
    if earliest is not None:
        normalized["earliest_time"] = earliest
    if latest is not None:
        normalized["latest_time"] = latest
    return {
        "spec_version": "lc1.v1",
        "scenario_id": f"lc4v4_{'mt' if multi else 'var'}_{group:03d}_{position:02d}",
        "provenance": "gold",
        "adjudication": "adjudicated",
        "family": "temporary_content_blind_test",
        "description": "Temporary synthetic framework fixture.",
        "dialogue_turns": turns,
        "reference_date": "2030-01-01",
        "clinic_clock": "2030-01-01T10:00:00+10:00",
        "intended_action": cell["intended_action"],
        "action_semantics": "intended",
        "temporal_relation": relation,
        "earliest_time": earliest,
        "latest_time": latest,
        "normalized_values": normalized,
        "source_spans": {"instruction": [{"turn_index": 0, "start": 0, "end": len(utterance), "text": utterance}]},
        "duration_minutes": 15,
        "practitioner_semantics": "exact",
        "patient_semantics": "exact",
        "location_semantics": "omitted",
        "appointment_type_semantics": "omitted",
        "duration_semantics": "exact",
        "diary_state": cell["diary_state"],
        "entity_state": cell["entity_state"],
        "dialogue_form": cell["dialogue_form"],
        "language_form": cell["language_form"],
        "initial_diary_state": {"synthetic": True},
        "expected_outcome_kind": None,
        "expected_tool_sequence": [],
        "expected_appointment_deltas": [],
        "expected_audit_deltas": [],
        "forbidden_outcomes": [],
        "forbidden_tool_calls": [],
        "expected_clarification": None,
        "clarification_choices": [],
    }


def _write_corpus(root: Path) -> Path:
    corpus = root / "temporary-v4-framework-corpus"
    corpus.mkdir()
    index = 0
    for group in range(1, LC4V4_GROUP_COUNT + 1):
        surfaces = []
        trajectories = []
        for position in range(1, 10):
            surfaces.append(_scenario(index, group, position, False))
            index += 1
        for position in range(1, 4):
            trajectories.append(_scenario(index, group, position, True))
            index += 1
        value = {
            "group_id": f"lc4v4_group_{group:03d}",
            "surface_variants": surfaces,
            "multi_turn_variants": trajectories,
        }
        (corpus / f"lc4v4_group_{group:03d}.json").write_text(
            json.dumps(value), encoding="utf-8", newline="\n"
        )
    return corpus


def test_manifest_binds_quality_receipt_and_corpus(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    quality = _quality_receipt()
    manifest = build_manifest(corpus, quality)
    assert manifest["authoring_quality_receipt_hash"] == quality["receipt_hash"]
    assert reconstruct_manifest(manifest) == manifest
    assert verify_manifest_against_corpus(corpus, manifest, quality) == manifest
    changed = json.loads(json.dumps(quality))
    changed["receipt_hash"] = "sha256:" + "0" * 64
    with pytest.raises(ValueError):
        verify_manifest_against_corpus(corpus, manifest, changed)


def test_seal_and_one_shot_lifecycle(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    quality = _quality_receipt()
    manifest = build_manifest(corpus, quality)
    seal = create_seal(manifest)
    assert verify_seal(seal, manifest) == seal
    report_path = tmp_path / "aggregate.json"
    consumed_path = tmp_path / "consumed.json"
    report, consumed = run_baseline_once(
        corpus,
        manifest,
        quality,
        seal,
        report_path=report_path,
        consumed_seal_path=consumed_path,
    )
    assert report_path.is_file() and consumed_path.is_file()
    assert consumed["consumed"] is True
    assert report["manifest_hash"] == seal["manifest_hash"]
    assert check_aggregate_report(report)["valid"] is True
    with pytest.raises(FileExistsError):
        run_baseline_once(
            corpus,
            manifest,
            quality,
            seal,
            report_path=report_path,
            consumed_seal_path=tmp_path / "other-consumed.json",
        )


def test_one_shot_rejects_alias_and_output_inside_corpus(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    quality = _quality_receipt()
    manifest = build_manifest(corpus, quality)
    seal = create_seal(manifest)
    with pytest.raises(ValueError, match="distinct"):
        run_baseline_once(corpus, manifest, quality, seal, report_path=tmp_path / "same.json", consumed_seal_path=tmp_path / "same.json")
    with pytest.raises(ValueError, match="outside"):
        run_baseline_once(corpus, manifest, quality, seal, report_path=corpus / "report.json", consumed_seal_path=tmp_path / "consumed.json")


def test_aggregate_lint_rejects_case_level_structure() -> None:
    with pytest.raises(ValueError):
        check_forbidden_aggregate_keys({"scenario_id": "temporary"})


def test_framework_identity_and_isolation() -> None:
    assert LC4V4_EVALUATION_ID == "lc4-holdout-v4-baseline-001"
    assert LC4V4_EVALUATOR_VERSION == "lc4v4.aggregate_evaluator.v1"
    assert LC4V4_REPORT_SCHEMA == "lc4v4.aggregate_evaluation.v1"
    assert LC4V4_TOTAL_SAMPLES == 576
    validate_lc4v4_isolation()
    validate_lc4v4_authoring_quality_isolation()


def test_cli_has_no_default_artifact_paths() -> None:
    tree = ast.parse((ROOT / "scripts/bernie_lc4v4_certification.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument":
            assert all(keyword.arg != "default" for keyword in node.keywords)


def test_no_actual_v4_artifact_exists_before_content() -> None:
    for path in (
        ROOT / "tests" / "fixtures" / "bernie_lc4_holdout_v4",
        ROOT / "tests" / "fixtures" / "bernie_lc4_holdout_v4_manifest.json",
        ROOT / "docs" / "bernie-lc4v4-seal.json",
        ROOT / "docs" / "bernie-lc4v4-aggregate-report.json",
        ROOT / "scripts" / "bernie_lc4v4_authoring.py",
    ):
        assert not path.exists()


def test_cli_manifest_seal_baseline_and_postcheck(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    quality_path = tmp_path / "quality.json"
    quality_path.write_text(json.dumps(_quality_receipt()), encoding="utf-8", newline="\n")
    manifest = tmp_path / "manifest.json"
    seal = tmp_path / "seal.json"
    report = tmp_path / "report.json"
    consumed = tmp_path / "consumed.json"
    commands = [
        ["build-manifest", str(corpus), str(quality_path), "--write", str(manifest)],
        ["check-manifest", str(corpus), str(quality_path), str(manifest)],
        ["create-seal", str(corpus), str(quality_path), str(manifest), "--write", str(seal)],
        ["baseline-once", str(corpus), str(quality_path), str(manifest), str(seal), "--write", str(report), str(consumed)],
        ["check-aggregate", str(report)],
    ]
    for command in commands:
        completed = subprocess.run(
            [sys.executable, "-m", "scripts.bernie_lc4v4_certification", *command],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
