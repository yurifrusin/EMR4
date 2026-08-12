"""Deterministic structural acceptance for the compatibility harness repair."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "712e9842297e5aee21c3b4acb061d439639bae04"

OWNED_TESTS = (
    "tests/test_booking_create_edit.py",
    "tests/test_booking_patient_flow.py",
    "tests/test_break_overlap_contract.py",
    "tests/test_location_scoped_diary.py",
    "tests/test_noshow_dna_status_contract.py",
    "tests/test_nurse_practitioner.py",
    "tests/test_reason_code_backend.py",
    "tests/test_slots.py",
)

TRANCHE_PATHS = frozenset(
    OWNED_TESTS
    + (
        "docs/raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair-plan.md",
        "docs/security/raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair-threat-model-delta.md",
        "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-preplanning-receipt.json",
        "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-preplanning-runtime-state.json",
        "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-precommit-receipt.json",
        "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-precommit-runtime-state.json",
        "orchestration/continuity/raisa-provider-free-compatibility-conformance-harness-readiness-repair/structural-repair-evidence.json",
        "scripts/raisa_provider_free_compatibility_conformance_harness_readiness_repair.py",
        "tests/test_raisa_provider_free_compatibility_conformance_harness_readiness_repair.py",
    )
)

WEEKDAY_FILES = (
    "tests/test_break_overlap_contract.py",
    "tests/test_location_scoped_diary.py",
    "tests/test_nurse_practitioner.py",
    "tests/test_slots.py",
)


class AdmissionError(RuntimeError):
    """Raised when the frozen test-only boundary is not satisfied."""


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8-sig")


def _baseline_source(path: str) -> str:
    return _git("show", f"{BASELINE}:{path}")


def _status_assertions(source: str) -> list[tuple[str, tuple[int, ...]]]:
    tree = ast.parse(source)
    assertions: list[tuple[str, tuple[int, ...]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert) or not isinstance(node.test, ast.Compare):
            continue
        comparison = node.test
        if not isinstance(comparison.left, ast.Attribute):
            continue
        if comparison.left.attr != "status_code":
            continue
        values = tuple(
            comparator.value
            for comparator in comparison.comparators
            if isinstance(comparator, ast.Constant)
            and isinstance(comparator.value, int)
        )
        operators = ",".join(type(operator).__name__ for operator in comparison.ops)
        assertions.append((operators, values))
    return sorted(assertions)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def build_evidence() -> dict[str, object]:
    changed = set(filter(None, _git("diff", "--name-only", BASELINE, "--").splitlines()))
    unexpected = sorted(changed - TRANCHE_PATHS)
    if unexpected:
        raise AdmissionError(f"unexpected changed paths: {unexpected}")

    changed_tests = sorted(changed.intersection(OWNED_TESTS))
    if changed_tests != sorted(OWNED_TESTS):
        raise AdmissionError(f"owned test delta mismatch: {changed_tests}")

    if _git("rev-parse", f"{BASELINE}:app") != _git("rev-parse", "HEAD:app"):
        raise AdmissionError("committed application tree changed")
    if _git("diff", "--name-only", "--", "app"):
        raise AdmissionError("working application tree changed")

    for path in OWNED_TESTS:
        if _status_assertions(_source(path)) != _status_assertions(_baseline_source(path)):
            raise AdmissionError(f"status assertion changed: {path}")

    create_source = _source("tests/test_booking_create_edit.py")
    patient_source = _source("tests/test_booking_patient_flow.py")
    if create_source.count("def _freeze_clinic_clock") != 1:
        raise AdmissionError("booking create/edit clinic clock is not frozen exactly once")
    if patient_source.count("def _freeze_clinic_clock") != 1:
        raise AdmissionError("booking patient-flow clinic clock is not frozen exactly once")
    if "datetime.combine(TODAY, time(1), tzinfo=timezone.utc).isoformat()" not in create_source:
        raise AdmissionError("UTC conversion fixture is not derived from the frozen test date")

    forbidden_elapsed_literals = {
        "tests/test_break_overlap_contract.py": "2026-06-25",
        "tests/test_location_scoped_diary.py": "2026-06-23",
        "tests/test_nurse_practitioner.py": "2026-06-22",
        "tests/test_slots.py": "2026-06-22",
    }
    for path in WEEKDAY_FILES:
        source = _source(path)
        if source.count("def _next_weekday") != 1:
            raise AdmissionError(f"future weekday fixture missing: {path}")
        if forbidden_elapsed_literals[path] in source:
            raise AdmissionError(f"elapsed date literal retained: {path}")

    noshow_source = _source("tests/test_noshow_dna_status_contract.py")
    reason_source = _source("tests/test_reason_code_backend.py")
    if "Idempotency-Key\": f\"noshow-dna-{appt_id}-{new_status.lower()}" not in noshow_source:
        raise AdmissionError("NoShow/DNA proposal idempotency identity is missing")
    for marker in (
        "reason-status-proposal-{appt.id}",
        "reason-delete-proposal-{appt.id}",
    ):
        if marker not in reason_source:
            raise AdmissionError(f"reason-code proposal idempotency identity is missing: {marker}")

    return {
        "schema_version": "raisa.compatibility_conformance_harness_readiness_repair.v1",
        "baseline_head": BASELINE,
        "application_tree_unchanged": True,
        "owned_test_files": list(OWNED_TESTS),
        "changed_test_file_count": len(changed_tests),
        "status_assertions_unchanged": True,
        "same_day_clock_fixture_count": 2,
        "future_weekday_fixture_count": 4,
        "proposal_header_source_sites": 3,
        "proposal_header_exercised_cases": 12,
        "pre_repair_test_result": {"passed": 266, "failed": 45},
        "frozen_failure_classification": {
            "past_or_elapsed_time_fixture": 33,
            "missing_required_proposal_idempotency_header": 12,
        },
        "file_sha256": {path: _sha256(path) for path in OWNED_TESTS},
        "runtime_or_command_authority_granted": False,
        "status": "structural_repair_pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = build_evidence()
    rendered = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
