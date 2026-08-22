from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-"
    "decision"
)
TOPIC = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = TOPIC / "contract.json"
SCHEMA_PATH = TOPIC / "decision-evidence.schema.json"
EVIDENCE_PATH = TOPIC / "decision-evidence.json"
REPORT_PATH = TOPIC / "decision-report.md"

SCHEMA_VERSION = (
    "emr4.check-in-attempt-008-plan-admissibility-decision-evidence.v1"
)
PASS_RESULT = (
    "raisa_provider_free_read_only_check_in_attempt_008_plan_admissibility_"
    "decision_pass"
)
POSITIVE_VERDICT = "admissible_for_separate_plan_freeze"
PLAN_SOURCE = "26a27eb95b39028995b0803bcea6aaf486e5ebbe"
PROTECTED_SOURCE = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
RECORDED_AT = "2026-08-23T06:16:44.7811918+10:00"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

ACCEPTED_GIT_SOURCES = [
    {"label": "attempt_007_plan", "source": "e3da4d993c8daec9973aed59ca4052e8a8429747"},
    {"label": "attempt_007_terminal", "source": "6657ee5061265d732096e9987f327d82feed800c"},
    {"label": "diagnosis_closeout", "source": "5d93380060f31bab21bddc9ffdd5580754eb4fc6"},
    {
        "label": "deterministic_repair_closeout",
        "source": "a33a4ccc7619fcae5cdd45a48a2312ab0c0384a4",
    },
    {
        "label": "verification_envelope_closeout",
        "source": "d01ef2f3afe16ccdb9a8f2077d5e76688397adb6",
    },
]

PREREQUISITES = [
    ("P01", "accepted_evidence", "satisfied", "Attempt 007 is consumed once, immutable, failed closed and retried zero times."),
    ("P02", "accepted_evidence", "satisfied", "The exact failure and cleanup-collapse coordinates are deterministically diagnosed."),
    ("P03", "accepted_evidence", "satisfied", "The complete prospective-success projection passes unchanged redaction/schema admission and hostile mutations reject before occupied work."),
    ("P04", "accepted_evidence", "satisfied", "A base-owned typed post-finalization terminal preserves finalized cleanup and prevents late success release."),
    ("P05", "accepted_evidence", "satisfied", "Closed database authority rejects ordinary/serial pytest and verification phases are typed before child launch."),
    ("P06", "future_plan", "plan_required", "Attempt 008 receives a fresh identity, collision-free namespace and no-retry/no-resume/no-fallback rule."),
    ("P07", "future_plan", "plan_required", "A new wrapper and closed terminal schema bind current repaired base source and immutable attempt-007 lineage without altering either."),
    ("P08", "future_plan", "plan_required", "Every source digest and Git ancestry binding is regenerated mechanically at the exact clean candidate."),
    ("P09", "future_plan", "plan_required", "The one authorized command, invocation count one and terminal consumption semantics are frozen exactly."),
    ("P10", "future_plan", "plan_required", "Rollback-zero, unknown-response no-success/no-retry, authoritative exactly-once readback, isolation and cleanup acceptance remain exact."),
    ("P11", "future_plan", "plan_required", "Product, API, ordinary-practice, provider, data, production and protected boundaries remain closed."),
    ("P12", "preexecution", "preexecution_required", "Complete deterministic provider-free tests, static admission, Ruff, compilation, schema and diff gates pass on one committed candidate."),
    ("P13", "preexecution", "preexecution_required", "Read-only Docker inspection proves exact cached image and zero matching resources, then a fresh five-source receipt repeats lane dispositions."),
    ("P14", "preexecution", "preexecution_required", "A distinct clockwork checkpoint check/publish advances the latch to exactly one occupied execution only after all earlier rows pass."),
]

SOURCE_BINDINGS = [
    ("docs/raisa-provider-free-check-in-relay-free-recovery-attempt-007-plan.md", "d0f692aa2d8afabbb29a9cac0aaceb77382dde60bcbfb4f1e3128bb3629ae18c"),
    ("orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/attempt-007-execution-envelope.json", "3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5"),
    ("orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/rehearsal-failure-evidence.json", "86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422"),
    ("orchestration/continuity/raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis/diagnosis-evidence.json", "b6d473d20fa64757fc25fbd2eb4f1792d86ebc91e3f0a8bf5bb3c9bdcc62d8e4"),
    ("orchestration/continuity/raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis/diagnosis-report.md", "74739c1cddeb0345e793da6a1059d020b595f09852ed64c76db87a67ad885674"),
    ("docs/raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis-closeout.md", "94451fa5f3e6a09001b9fdce21a2ded6d66a51a93e4429529c12528668531d65"),
    ("orchestration/continuity/raisa-provider-free-check-in-prospective-success-redaction-and-typed-cleanup-projection-conformance-repair/repair-contract.json", "662e055f9011aa5574127503b46dd3ca9c6c3113ce6dad3b6e3ca35728930658"),
    ("orchestration/continuity/raisa-provider-free-check-in-prospective-success-redaction-and-typed-cleanup-projection-conformance-repair/repair-evidence.json", "47f422e7b8ad072c9f4912fe6269cfc85f44eb75808419182c75e19d41157eaa"),
    ("docs/raisa-provider-free-check-in-prospective-success-redaction-and-typed-cleanup-projection-conformance-repair-closeout.md", "5efae848109d632e3a9c858269995205a9ef94e2ab26fb9de9ffa365ec5b2492"),
    ("orchestration/continuity/ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair/contract.json", "ee7ce96d2561c0b9c8f73e01e2ffb25d3154239bd22b0d0a19dba6d87a28119e"),
    ("orchestration/continuity/ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair/evidence.json", "47e6fd567e773c69fd7867e30a56f69e0d9346f1f6216fd37aebbdbaec96aa0d"),
    ("docs/ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair-closeout.md", "32a7d2059d4c8d39a5480f05f7ac00d51e65396ae9c71a7cd40b9a9bcbc7eb10"),
]

TARGET_ABSENT_PATHS = [
    "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-008-plan.md",
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-008",
]

BASIS = {
    "P01": [SOURCE_BINDINGS[1][0], SOURCE_BINDINGS[2][0]],
    "P02": [SOURCE_BINDINGS[3][0], SOURCE_BINDINGS[4][0]],
    "P03": [SOURCE_BINDINGS[6][0], SOURCE_BINDINGS[7][0]],
    "P04": [SOURCE_BINDINGS[7][0], SOURCE_BINDINGS[8][0]],
    "P05": [SOURCE_BINDINGS[9][0], SOURCE_BINDINGS[10][0]],
    "P06": ["docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md"],
    "P07": ["docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md"],
    "P08": ["docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md"],
    "P09": [SOURCE_BINDINGS[0][0]],
    "P10": [SOURCE_BINDINGS[0][0]],
    "P11": ["docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md"],
    "P12": ["docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md", SOURCE_BINDINGS[10][0]],
    "P13": ["docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md"],
    "P14": ["docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md"],
}


class DecisionError(RuntimeError):
    pass


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DecisionError(f"expected_object_{path.name}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if path == ROOT or ROOT not in path.parents or path.is_symlink():
        raise DecisionError("path_invalid")
    return path


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    head = result.stdout.strip()
    if HEX40.fullmatch(head) is None:
        raise DecisionError("head_not_full_git_object")
    return head


def _assert_ancestor(source: str, head: str) -> None:
    if HEX40.fullmatch(source) is None or HEX40.fullmatch(head) is None:
        raise DecisionError("git_object_not_full")
    relation = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, head],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if relation.returncode != 0:
        raise DecisionError("accepted_source_not_ancestor")


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise DecisionError(code)


def _contract_prerequisites() -> list[dict[str, str]]:
    return [
        {"id": item_id, "stage": stage, "expected_state": state, "summary": summary}
        for item_id, stage, state, summary in PREREQUISITES
    ]


def _validate_contract(contract: Mapping[str, Any], candidate: str) -> None:
    _require(
        set(contract)
        == {
            "schema_version", "operation_id", "result", "positive_verdict",
            "plan_source", "protected_source", "accepted_git_sources",
            "prerequisites", "source_bindings", "target_absent_paths",
            "expected_signals", "closed_boundaries",
        },
        "contract_keys_invalid",
    )
    _require(contract["schema_version"] == "emr4.check-in-attempt-008-plan-admissibility-contract.v1", "contract_version_invalid")
    _require(contract["operation_id"] == OPERATION_ID, "contract_operation_invalid")
    _require(contract["result"] == PASS_RESULT, "contract_result_invalid")
    _require(contract["positive_verdict"] == POSITIVE_VERDICT, "contract_verdict_invalid")
    _require(contract["plan_source"] == PLAN_SOURCE, "contract_plan_source_invalid")
    _require(contract["protected_source"] == PROTECTED_SOURCE, "contract_protected_source_invalid")
    _require(contract["accepted_git_sources"] == ACCEPTED_GIT_SOURCES, "contract_git_sources_invalid")
    _require(contract["prerequisites"] == _contract_prerequisites(), "contract_prerequisites_invalid")
    _require(
        contract["source_bindings"]
        == [{"path": path, "sha256": digest} for path, digest in SOURCE_BINDINGS],
        "contract_source_bindings_invalid",
    )
    _require(contract["target_absent_paths"] == TARGET_ABSENT_PATHS, "contract_target_paths_invalid")
    _require(
        contract["expected_signals"]
        == {
            "prerequisite_count": 14,
            "satisfied_count": 5,
            "plan_required_count": 6,
            "preexecution_required_count": 3,
            "blocking_count": 0,
            "prospective_path_count": 67,
            "hostile_projection_rejections": 66,
            "verification_envelope_rejections": 8,
        },
        "contract_signals_invalid",
    )
    _require(
        isinstance(contract["closed_boundaries"], dict)
        and len(contract["closed_boundaries"]) == 9
        and not any(contract["closed_boundaries"].values()),
        "contract_boundary_open",
    )
    for path, digest in SOURCE_BINDINGS:
        resolved = _safe_path(path)
        _require(resolved.is_file(), "source_binding_missing")
        _require(HEX64.fullmatch(digest) is not None and _sha256(resolved) == digest, "source_binding_drift")
    for source in [PLAN_SOURCE, PROTECTED_SOURCE, *[row["source"] for row in ACCEPTED_GIT_SOURCES]]:
        _assert_ancestor(source, candidate)


def _validate_accepted_evidence() -> None:
    envelope = _load_json(_safe_path(SOURCE_BINDINGS[1][0]))
    failure = _load_json(_safe_path(SOURCE_BINDINGS[2][0]))
    diagnosis = _load_json(_safe_path(SOURCE_BINDINGS[3][0]))
    repair_contract = _load_json(_safe_path(SOURCE_BINDINGS[6][0]))
    repair = _load_json(_safe_path(SOURCE_BINDINGS[7][0]))
    verification_contract = _load_json(_safe_path(SOURCE_BINDINGS[9][0]))
    verification = _load_json(_safe_path(SOURCE_BINDINGS[10][0]))

    _require(envelope.get("result") == "failed_closed", "attempt_007_result_invalid")
    _require(envelope.get("occupied_execution_count") == 1, "attempt_007_count_invalid")
    _require(envelope.get("automatic_retry_count") == 0, "attempt_007_retry_invalid")
    _require(envelope.get("ambiguous_success_released") is False, "attempt_007_success_invalid")
    _require(failure.get("stage") == "redaction" and failure.get("code") == "forbidden_field", "attempt_007_terminal_invalid")
    _require(failure.get("cleanup") == {"status": "not_started"}, "attempt_007_cleanup_invalid")
    _require(failure.get("retry_count") == 0 and failure.get("success_released") is False, "attempt_007_failure_release_invalid")

    _require(diagnosis.get("result") == "raisa_provider_free_read_only_check_in_attempt_007_redaction_cleanup_projection_coordinate_diagnosis_pass", "diagnosis_result_invalid")
    _require(diagnosis.get("input_bindings_verified") is True, "diagnosis_binding_invalid")
    prospective = diagnosis.get("prospective_projection", {})
    _require(prospective.get("coordinate") == "prospective_success_projection_forbidden_field", "diagnosis_projection_coordinate_invalid")
    _require(prospective.get("conflict_count") == 1 and prospective.get("key_path_count") == 67, "diagnosis_projection_count_invalid")
    _require(diagnosis.get("base_control_flow", {}).get("coordinate") == "post_cleanup_result_redaction_escape", "diagnosis_escape_coordinate_invalid")
    _require(diagnosis.get("wrapper_projection", {}).get("coordinate") == "wrapper_untyped_post_finalization_cleanup_collapse", "diagnosis_wrapper_coordinate_invalid")
    _require(diagnosis.get("repair_boundary", {}).get("attempt_008_authorized") is False, "diagnosis_attempt_authority_invalid")
    _require(all(value == 0 for value in diagnosis.get("activity", {}).values()), "diagnosis_activity_invalid")

    _require(repair_contract.get("repair_gears") == ["prospective_success_projection_static_gate", "typed_post_finalization_terminal_bridge"], "repair_gears_invalid")
    _require(repair_contract.get("safe_boundary_key") == "live_sensitive_material_existing_hosted_or_product_database_used", "repair_boundary_key_invalid")
    _require(repair.get("result") == "raisa_provider_free_check_in_prospective_success_redaction_and_typed_cleanup_projection_conformance_repair_pass", "repair_result_invalid")
    projection = repair.get("prospective_projection", {})
    _require(projection.get("path_count") == projection.get("runtime_path_count") == 67, "repair_projection_parity_invalid")
    _require(projection.get("hostile_attempted") == projection.get("hostile_rejected") == 66, "repair_hostile_count_invalid")
    _require(projection.get("redaction_status") == projection.get("schema_status") == "passed", "repair_projection_admission_invalid")
    terminal = repair.get("typed_terminal", {})
    _require(terminal.get("late_failure_escape_count") == 0 and terminal.get("success_release_after_late_failure_count") == 0, "repair_terminal_escape_invalid")
    _require(terminal.get("redaction_failure_cleanup") == terminal.get("schema_failure_cleanup") == terminal.get("wrapper_cleanup_projection") == "cleanup_verified", "repair_cleanup_projection_invalid")
    _require(all(value == 0 for value in repair.get("activity_counts", {}).values()), "repair_activity_invalid")
    _require(not any(repair.get("closed_boundaries", {}).values()), "repair_boundary_open")

    _require(verification_contract.get("database_closed_pytest_runner") == "scripts.ariadne_provider_free_pytest", "verification_runner_invalid")
    _require(verification_contract.get("database_closed_forbidden_runners") == ["ordinary_pytest", "serial_pytest"], "verification_forbidden_runners_invalid")
    _require(verification.get("result") == "ariadne_provider_free_verification_envelope_phase_and_runner_admission_repair_pass", "verification_result_invalid")
    _require(verification.get("database_authority") == "closed", "verification_authority_invalid")
    _require(verification.get("hostile_rejection_count") == 8 and verification.get("subprocess_launch_count") == 0, "verification_rejection_invalid")
    _require(verification.get("phase_partition", {}).get("cross_phase_execution_count") == 0, "verification_phase_escape_invalid")
    _require(verification.get("verification_phases") == ["prepublication", "postpublication"], "verification_phase_vocabulary_invalid")
    _require(not any(verification.get("closed_boundaries", {}).values()), "verification_boundary_open")


def _assert_absent(paths: Sequence[str], *, root: Path = ROOT) -> None:
    for relative in paths:
        target = (root / relative).resolve()
        if target == root or root not in target.parents or target.exists() or target.is_symlink():
            raise DecisionError("attempt_008_artifact_already_exists")


def build_evidence(contract: Mapping[str, Any], source_head: str) -> dict[str, Any]:
    _require(HEX40.fullmatch(source_head) is not None, "source_head_not_full")
    _validate_contract(contract, source_head)
    _validate_accepted_evidence()
    _assert_absent(TARGET_ABSENT_PATHS)
    rows = [
        {"id": item_id, "stage": stage, "state": state, "summary": summary, "basis": BASIS[item_id]}
        for item_id, stage, state, summary in PREREQUISITES
    ]
    counts = {
        "prerequisite_count": len(rows),
        "satisfied_count": sum(row["state"] == "satisfied" for row in rows),
        "plan_required_count": sum(row["state"] == "plan_required" for row in rows),
        "preexecution_required_count": sum(row["state"] == "preexecution_required" for row in rows),
        "blocking_count": sum(row["state"] == "blocking" for row in rows),
    }
    _require(counts == {key: contract["expected_signals"][key] for key in counts}, "decision_counts_invalid")
    value = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "result": PASS_RESULT,
        "verdict": POSITIVE_VERDICT,
        "source_head": source_head,
        "source_bindings_verified": True,
        "accepted_sources_ancestor_of_candidate": True,
        "prerequisites": rows,
        "counts": counts,
        "attempt_008": {
            "plan_exists": False,
            "continuity_namespace_exists": False,
            "plan_freeze_admissible": True,
            "ready_to_execute": False,
        },
        "activity": {
            "database_actions": 0,
            "docker_actions": 0,
            "postgresql_starts": 0,
            "sql_executions": 0,
            "provider_calls": 0,
            "worker_calls": 0,
            "network_calls": 0,
            "product_actions": 0,
        },
        "closed_boundaries": dict(contract["closed_boundaries"]),
    }
    schema = _load_json(SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.path))
    if errors:
        raise DecisionError("evidence_schema_invalid:" + errors[0].message)
    return value


def build_report(evidence: Mapping[str, Any]) -> str:
    counts = evidence["counts"]
    return f"""# Check-in attempt-008 plan-admissibility decision

Date: 2026-08-23

Timestamp: {RECORDED_AT} (Australia/Brisbane)

Status: `passed_read_only_decision`

Exact source: `{evidence['source_head']}`

## Verdict

`{evidence['verdict']}`

All {counts['prerequisite_count']} frozen prerequisites are accounted for: {counts['satisfied_count']} accepted-evidence rows are satisfied, {counts['plan_required_count']} remain mandatory future-plan obligations, {counts['preexecution_required_count']} remain mandatory preexecution obligations, and {counts['blocking_count']} are blocking.

This is not execution readiness. No attempt-008 plan or Continuity namespace exists, and `ready_to_execute` is false. A separately named plan may now freeze P06-P14 as exact fail-closed conditions.

## Evidence boundary

Attempt 007 remains consumed once and failed closed. Its exact redaction and cleanup-projection causes have accepted deterministic repairs. The typed verification envelope is accepted. No database, Docker, PostgreSQL, SQL, provider, worker, network, product, protected or attempt-008 action was used.
"""


def _check_existing(contract: Mapping[str, Any], current_head: str) -> None:
    evidence = _load_json(EVIDENCE_PATH)
    source = evidence.get("source_head")
    _require(isinstance(source, str) and HEX40.fullmatch(source) is not None, "evidence_source_invalid")
    _assert_ancestor(source, current_head)
    expected = build_evidence(contract, source)
    _require(EVIDENCE_PATH.read_bytes() == _canonical_bytes(expected), "evidence_not_canonical")
    _require(REPORT_PATH.read_text(encoding="utf-8") == build_report(expected), "report_drift")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    parser.add_argument("--source")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    contract = _load_json(CONTRACT_PATH)
    head = _git_head()
    try:
        if args.write:
            _require(args.source == head, "write_source_must_equal_head")
            _require(not EVIDENCE_PATH.exists() and not REPORT_PATH.exists(), "output_exists")
            evidence = build_evidence(contract, head)
            EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
            EVIDENCE_PATH.write_bytes(_canonical_bytes(evidence))
            REPORT_PATH.write_text(build_report(evidence), encoding="utf-8")
        else:
            _require(args.source is None, "check_source_forbidden")
            _check_existing(contract, head)
    except (DecisionError, OSError, ValueError, subprocess.SubprocessError):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
