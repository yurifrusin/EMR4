from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from scripts import ariadne_bounded_cognitive_work_cell as work_cell
from scripts import ariadne_scripted_cognitive_work_cell_rehearsal as rehearsal


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = (
    REPO_ROOT
    / "orchestration/continuity/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-example.json"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "orchestration/continuity/"
    "ariadne-scripted-cognitive-work-cell-rehearsal.schema.json"
)
EVIDENCE_PATH = (
    REPO_ROOT
    / "orchestration/continuity/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-evidence.json"
)
PROTOCOL_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-bounded-cognitive-work-cell-example.json"
)
SCRIPT_PATH = REPO_ROOT / "scripts/ariadne_scripted_cognitive_work_cell_rehearsal.py"
GRAPH_PATH = REPO_ROOT / "orchestration/continuity/emr4-continuity-graph.json"
NODE_PATH = (
    REPO_ROOT
    / "orchestration/agent_inbox/codex/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-node.json"
)


def load_document() -> dict:
    return json.loads(DOCUMENT_PATH.read_text(encoding="utf-8"))


def load_protocol() -> dict:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def errors(document: dict | None = None, protocol: dict | None = None) -> list[str]:
    return rehearsal.validate_document(
        document or load_document(),
        protocol=protocol or load_protocol(),
        repo_root=REPO_ROOT,
    )


def build(document: dict | None = None, protocol: dict | None = None) -> dict:
    return rehearsal.build_rehearsal(
        document or load_document(),
        protocol=protocol or load_protocol(),
        repo_root=REPO_ROOT,
    )


def scenario(document: dict, scenario_id: str) -> dict:
    return next(item for item in document["scenarios"] if item["id"] == scenario_id)


def step_by_action(item: dict, action: str, occurrence: int = 0) -> dict:
    matches = [step for step in item["steps"] if step["action"] == action]
    return matches[occurrence]


def result_by_scenario(evidence: dict, scenario_id: str) -> dict:
    return next(
        item
        for item in evidence["scenario_results"]
        if item["scenario_id"] == scenario_id
    )


def test_canonical_tape_passes_schema_and_semantic_validation() -> None:
    document = load_document()

    assert errors(document) == []

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(document)


def test_source_protocol_is_exact_frozen_accepted_predecessor() -> None:
    document = load_document()
    protocol = load_protocol()

    assert work_cell.validate_document(protocol, repo_root=REPO_ROOT) == []
    assert document["source_protocol"] == {
        "path": PROTOCOL_PATH.relative_to(REPO_ROOT).as_posix(),
        "canonical_sha256": work_cell.canonical_sha256(protocol),
        "required_result": "ariadne_bounded_cognitive_work_cell_protocol_pass",
    }


def test_continuity_node_is_exact_metadata_only_descendant() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    node = json.loads(NODE_PATH.read_text(encoding="utf-8"))
    graph_node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "ariadne-scripted-cognitive-work-cell-rehearsal"
    )

    assert graph["graph_revision"] == 20
    assert graph_node == node
    assert node["relationships"] == [
        {
            "node_id": "ariadne-bounded-cognitive-work-cell-protocol",
            "relation": "builds_on",
        }
    ]
    assert node["authority"]["authorized_openings"] == []


def test_rehearsal_is_byte_deterministic_and_matches_committed_evidence() -> None:
    first = build()
    second = build()
    expected = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))

    assert rehearsal.canonical_json(first) == rehearsal.canonical_json(second)
    assert rehearsal.build_evidence_projection(first) == expected
    assert first["result"] == "ariadne_scripted_cognitive_work_cell_rehearsal_pass"


def test_transition_chain_is_forward_only_and_hash_complete() -> None:
    evidence = build()
    transitions = evidence["transitions"]
    seed = rehearsal.canonical_sha256(
        {
            "script_sha256": evidence["script_sha256"],
            "protocol_sha256": evidence["source_protocol_sha256"],
        }
    )

    previous = seed
    for index, transition in enumerate(transitions, start=1):
        assert transition["sequence"] == index
        assert transition["previous_transition_sha256"] == previous
        unhashed = {
            key: value
            for key, value in transition.items()
            if key != "transition_sha256"
        }
        assert transition["transition_sha256"] == rehearsal.canonical_sha256(
            unhashed
        )
        previous = transition["transition_sha256"]
    assert evidence["transition_chain_sha256"] == previous


def test_primary_scenario_releases_five_ports_and_routes_only_human_edges() -> None:
    evidence = build()
    primary = result_by_scenario(evidence, "scenario-primary-five-port-release")

    assert primary["released_edge_count"] == 5
    assert primary["human_gate_delivery_count"] == 2
    assert primary["terminal_state"] == "awaiting-human-authority"
    assert evidence["execution_posture"]["human_action_performed"] is False
    assert evidence["execution_posture"]["command_authority"] is False


def test_both_allowlisted_repair_paths_are_observed_without_new_rules() -> None:
    evidence = build()
    downstream = result_by_scenario(evidence, "scenario-repair-downstream")
    human = result_by_scenario(evidence, "scenario-repair-human-gate")

    assert downstream["repair_receipt_count"] == 1
    assert human["repair_receipt_count"] == 1
    assert evidence["totals"]["repair_receipt_count"] == 2
    verification = work_cell.build_verification(load_protocol(), repo_root=REPO_ROOT)
    rules = {
        rule
        for receipt in verification["repair_receipts"]
        for rule in receipt["repair_rules"]
    }
    assert rules == set(work_cell.REPAIR_ALLOWLIST)


def test_schema_retry_uses_exact_declared_later_attempt_then_human_route() -> None:
    document = load_document()
    item = scenario(document, "scenario-schema-retry-success")
    correction = step_by_action(item, "record-bounded-correction-request")
    submits = [step["attempt_id"] for step in item["steps"] if step["action"] == "submit-attempt"]

    assert submits == ["work-cell-attempt4", "work-cell-attempt5"]
    assert correction["retry_trace_id"] == "retry-schema-correction"
    assert correction["expected_to_attempt_id"] == "work-cell-attempt5"
    result = result_by_scenario(build(), item["id"])
    assert result["correction_request_count"] == 1
    assert result["released_edge_count"] == 1
    assert result["human_gate_delivery_count"] == 1


def test_grounding_retry_exhausts_budget_and_aborts_only_declared_edge() -> None:
    result = result_by_scenario(build(), "scenario-grounding-budget-abort")

    assert result["correction_request_count"] == 1
    assert result["released_edge_count"] == 0
    assert result["aborted_edge_count"] == 1
    assert result["terminal_state"] == "aborted"


def test_stale_context_binds_only_inert_grant_and_rejects_stale_completion() -> None:
    document = load_document()
    item = scenario(document, "scenario-stale-context-supersession")
    actions = [step["action"] for step in item["steps"]]

    assert actions == [
        "submit-attempt",
        "verify-drafts",
        "apply-verdict-disposition",
        "bind-inert-fresh-read-grant",
        "supersede-declared-attempt",
        "reject-stale-completion",
        "finish-scenario",
    ]
    result = result_by_scenario(build(), item["id"])
    assert result["supersession_count"] == 1
    assert result["stale_completion_rejection_count"] == 1
    assert result["terminal_state"] == "awaiting-fresh-context"


def test_authority_rejection_aborts_without_release_or_human_route() -> None:
    result = result_by_scenario(build(), "scenario-authority-abort")

    assert result["aborted_edge_count"] == 1
    assert result["released_edge_count"] == 0
    assert result["human_gate_delivery_count"] == 0
    assert result["terminal_state"] == "aborted"


def test_atomic_inconsistency_records_only_bounded_correction_request() -> None:
    result = result_by_scenario(build(), "scenario-atomic-correction-request")

    assert result["correction_request_count"] == 1
    assert result["released_edge_count"] == 0
    assert result["human_gate_delivery_count"] == 0
    assert result["terminal_state"] == "correction-requested"


def test_source_hash_and_step_vocabulary_drift_fail_closed() -> None:
    bad_hash = load_document()
    bad_hash["source_protocol"]["canonical_sha256"] = "sha256:" + "0" * 64
    bad_vocabulary = load_document()
    bad_vocabulary["step_vocabulary"][-1] = "execute-command"

    assert "source_protocol_hash_mismatch" in errors(bad_hash)
    vocabulary_errors = errors(bad_vocabulary)
    assert "step_vocabulary_not_frozen" in vocabulary_errors


def test_disposition_override_and_release_set_mutation_fail_closed() -> None:
    bad_disposition = load_document()
    item = scenario(bad_disposition, "scenario-authority-abort")
    step_by_action(item, "verify-drafts")["expected_disposition"] = (
        "release-verified-outputs"
    )
    bad_release = load_document()
    item = scenario(bad_release, "scenario-primary-five-port-release")
    step_by_action(item, "record-verified-release")["draft_ids"].pop()

    assert any(
        error.startswith("proofreader_disposition_override:")
        for error in errors(bad_disposition)
    )
    assert any(
        error.startswith("release_set_mismatch:") for error in errors(bad_release)
    )


def test_reordered_skipped_or_repeated_attempts_fail_closed() -> None:
    reordered = load_document()
    item = scenario(reordered, "scenario-repair-downstream")
    item["steps"][1], item["steps"][2] = item["steps"][2], item["steps"][1]
    skipped = load_document()
    item = scenario(skipped, "scenario-repair-downstream")
    item["steps"].pop(1)
    repeated = load_document()
    item = scenario(repeated, "scenario-schema-retry-success")
    submit_steps = [step for step in item["steps"] if step["action"] == "submit-attempt"]
    submit_steps[1]["attempt_id"] = "work-cell-attempt4"

    assert any("step_sequence_invalid:" in error for error in errors(reordered))
    assert any("step_sequence_invalid:" in error for error in errors(skipped))
    repeated_errors = errors(repeated)
    assert any("attempt_repeated:" in error for error in repeated_errors)
    assert any("retry_target_mismatch:" in error for error in repeated_errors)


def test_retry_and_supersession_lineage_mutations_fail_closed() -> None:
    bad_retry = load_document()
    item = scenario(bad_retry, "scenario-schema-retry-success")
    correction = step_by_action(item, "record-bounded-correction-request")
    correction["expected_to_attempt_id"] = "work-cell-attempt7"
    bad_supersession = load_document()
    item = scenario(bad_supersession, "scenario-stale-context-supersession")
    step_by_action(item, "supersede-declared-attempt")["retry_trace_id"] = (
        "retry-schema-correction"
    )

    assert any(
        "retry_trace_lineage_mismatch:" in error for error in errors(bad_retry)
    )
    assert any(
        "supersession_lineage_mismatch:" in error
        for error in errors(bad_supersession)
    )


def test_activated_fresh_read_grant_fails_source_protocol_validation() -> None:
    protocol = load_protocol()
    grant = next(
        item
        for item in protocol["fresh_read_grants"]
        if item["id"] == "grant-booking-context-v2"
    )
    grant["returns_data"] = True

    assert any(
        error.startswith("source_protocol_invalid:")
        for error in errors(protocol=protocol)
    )


def test_limits_unknown_fields_and_active_actuator_language_fail_closed() -> None:
    too_many = load_document()
    too_many["limits"]["max_scenarios"] = 9
    unknown = load_document()
    item = scenario(unknown, "scenario-repair-downstream")
    item["steps"][0]["callback"] = "run-later"

    assert "limit_out_of_bounds:max_scenarios" in errors(too_many)
    unknown_errors = errors(unknown)
    assert any(
        error.startswith("active_actuator_field_forbidden:")
        for error in unknown_errors
    )
    assert any("step_field_unknown:" in error for error in unknown_errors)


def test_evidence_references_are_repository_local_and_existing() -> None:
    unsafe = load_document()
    unsafe["evidence"].append("../outside.json")
    missing = load_document()
    missing["evidence"].append("docs/not-present-rehearsal-evidence.md")

    assert any("evidence_reference_unsafe:" in error for error in errors(unsafe))
    assert any("evidence_reference_invalid:" in error for error in errors(missing))


def test_runner_has_no_external_actuator_imports_or_file_writes() -> None:
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    attributes: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Attribute):
            attributes.add(node.attr)

    assert imported_roots.isdisjoint(
        {
            "app",
            "asyncio",
            "docker",
            "fastapi",
            "httpx",
            "psycopg",
            "requests",
            "socket",
            "sqlalchemy",
            "subprocess",
            "threading",
            "time",
            "urllib",
        }
    )
    assert attributes.isdisjoint(
        {
            "mkdir",
            "open",
            "rename",
            "replace",
            "unlink",
            "write_bytes",
            "write_text",
        }
    )


def test_cli_exposes_only_validate_rehearse_trace_and_sanitized_output(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    parser = rehearsal.build_parser()
    subparsers = next(
        action
        for action in parser._actions  # noqa: SLF001 - parser contract inspection
        if isinstance(action, __import__("argparse")._SubParsersAction)
    )
    assert set(subparsers.choices) == {"validate", "rehearse", "trace"}

    custom = load_document()
    custom["rehearsal_id"] = "caller-selected-private-label"
    custom["title"] = "caller-selected-private-title"
    protocol = load_protocol()
    original_load = rehearsal.load_json

    def fake_load(path: Path) -> dict:
        if path.name == DOCUMENT_PATH.name:
            return copy.deepcopy(custom)
        if path.name == PROTOCOL_PATH.name:
            return copy.deepcopy(protocol)
        return original_load(path)

    monkeypatch.setattr(rehearsal, "load_json", fake_load)
    assert rehearsal.main(["rehearse"]) == 0
    output = capsys.readouterr().out
    assert "caller-selected-private-label" not in output
    assert "caller-selected-private-title" not in output
    assert json.loads(output)["external_effects_enabled"] is False


def test_trace_is_fixed_aggregate_and_does_not_echo_scenario_identifiers() -> None:
    evidence = build()
    rendered = rehearsal.render_markdown(evidence)

    assert "finite in-memory tape only" in rendered
    assert "External effects enabled: **no**" in rendered
    assert "Scenarios: **8**" in rendered
    for item in evidence["scenario_results"]:
        assert item["scenario_id"] not in rendered
        assert item["purpose_code"] not in rendered


def test_api_spine_boundary_remains_read_context_only_and_unused() -> None:
    document = load_document()
    serialized = rehearsal.canonical_json(document)

    assert "graphql" not in serialized.lower()
    assert "openapi" not in serialized.lower()
    assert "fastapi" not in serialized.lower()
    assert document["authority"]["external_effects_enabled"] is False
    assert document["authority"]["command_authority"] is False
    assert document["authority"]["persistence_enabled"] is False
