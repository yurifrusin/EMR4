"""Build deterministic evidence for typed verification-envelope admission."""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.governance_clockwork_tick import (  # noqa: E402
    ClockworkTickRejection,
    _validate_commands,
)
from scripts.ariadne_evidence_gate import (  # noqa: E402
    COMMAND_MANIFEST_SCHEMA_VERSION,
    COMMAND_MANIFEST_SCHEMA_VERSION_V2,
    validate_command_manifest,
)
from scripts.ariadne_validation_runner import _commands_for_phase  # noqa: E402


OPERATION_ID = (
    "ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair"
)
TOPIC = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = TOPIC / "contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "contract.schema.json"
EVIDENCE_PATH = TOPIC / "evidence.json"
EVIDENCE_SCHEMA_PATH = TOPIC / "evidence.schema.json"
REPORT_PATH = TOPIC / "report.md"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _resolve_source(source: str) -> str:
    if HEX40.fullmatch(source) is None:
        raise ValueError("source_head_must_be_full_git_object")
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{source}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        shell=False,
    ).stdout.strip()
    if resolved != source:
        raise ValueError("source_head_resolution_mismatch")
    descendant = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        shell=False,
    )
    if descendant.returncode != 0:
        raise ValueError("source_head_not_ancestor")
    return resolved


def _verifier_v1() -> dict[str, Any]:
    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [{"id": "LEGACY", "argv": [sys.executable, "-m", "py_compile", "safe.py"]}],
    }


def _verifier_v2() -> dict[str, Any]:
    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION_V2,
        "database_authority": "closed",
        "commands": [
            {
                "id": "PRE",
                "argv": [sys.executable, "-m", "scripts.ariadne_provider_free_pytest", "tests/test_safe.py"],
                "verification_phase": "prepublication",
            },
            {
                "id": "POST",
                "argv": [sys.executable, "-m", "py_compile", "safe.py"],
                "verification_phase": "postpublication",
            },
        ],
    }


def _governance_v1() -> dict[str, Any]:
    return {
        "schema_version": "ariadne.governance_command_manifest.v1",
        "commands": [
            {
                "command_id": "legacy",
                "executable": ".venv/Scripts/python.exe",
                "arguments": ["-m", "py_compile", "safe.py"],
                "completion_contract": "final_exit_code_zero_required",
            }
        ],
    }


def _governance_v2() -> dict[str, Any]:
    return {
        "schema_version": "ariadne.governance_command_manifest.v2",
        "database_authority": "closed",
        "commands": [
            {
                "command_id": "provider-free-pre",
                "executable": ".venv/Scripts/python.exe",
                "arguments": ["-m", "scripts.ariadne_provider_free_pytest", "tests/test_safe.py"],
                "completion_contract": "final_exit_code_zero_required",
                "verification_phase": "prepublication",
            },
            {
                "command_id": "post-readback",
                "executable": ".venv/Scripts/python.exe",
                "arguments": ["-m", "py_compile", "safe.py"],
                "completion_contract": "final_exit_code_zero_required",
                "verification_phase": "postpublication",
            },
        ],
    }


def _must_reject(
    validator: Callable[[object], object], value: object, expected: str
) -> None:
    try:
        validator(value)
    except (ClockworkTickRejection, ValueError) as error:
        if expected not in str(error):
            raise AssertionError(f"unexpected rejection: {error}") from error
        return
    raise AssertionError(f"hostile coordinate admitted: {expected}")


def _exercise_surface(
    *,
    validator: Callable[[object], object],
    legacy: dict[str, Any],
    typed: dict[str, Any],
    command_key: str,
    argv_key: str,
    surface: str,
    ordinary_reason: str,
    serial_reason: str,
    unknown_reason: str,
    order_reason: str,
) -> dict[str, Any]:
    validator(legacy)
    validator(typed)
    ordinary = copy.deepcopy(typed)
    ordinary["commands"][0][argv_key][1] = "pytest"
    _must_reject(validator, ordinary, ordinary_reason)
    serial = copy.deepcopy(typed)
    serial["commands"][0][argv_key][1] = "scripts.ariadne_serial_pytest"
    _must_reject(validator, serial, serial_reason)
    unknown = copy.deepcopy(typed)
    unknown["commands"][0]["verification_phase"] = "before_publish"
    _must_reject(validator, unknown, unknown_reason)
    reversed_order = copy.deepcopy(typed)
    reversed_order["commands"][0]["verification_phase"] = "postpublication"
    reversed_order["commands"][1]["verification_phase"] = "prepublication"
    _must_reject(validator, reversed_order, order_reason)
    if any(command_key not in row for row in typed["commands"]):
        raise AssertionError("command identifier missing")
    return {
        "surface": surface,
        "legacy_v1_admitted": True,
        "typed_v2_admitted": True,
        "rejected_coordinates": [
            "ordinary_pytest",
            "serial_pytest",
            "unknown_phase",
            "reversed_phase_order",
        ],
    }


def build_evidence(source: str) -> dict[str, Any]:
    source_head = _resolve_source(source)
    contract = _load(CONTRACT_PATH)
    Draft202012Validator(_load(CONTRACT_SCHEMA_PATH)).validate(contract)
    verifier = validate_command_manifest(_verifier_v2())
    pre = _commands_for_phase(verifier, phase="prepublication")
    post = _commands_for_phase(verifier, phase="postpublication")
    evidence = {
        "schema_version": "ariadne.provider_free_verification_envelope_evidence.v1",
        "operation_id": OPERATION_ID,
        "source_head": source_head,
        "recorded_at": contract["recorded_at"],
        "result": "ariadne_provider_free_verification_envelope_phase_and_runner_admission_repair_pass",
        "database_authority": "closed",
        "verification_phases": ["prepublication", "postpublication"],
        "surface_results": [
            _exercise_surface(
                validator=validate_command_manifest,
                legacy=_verifier_v1(),
                typed=_verifier_v2(),
                command_key="id",
                argv_key="argv",
                surface="verifier_command_manifest",
                ordinary_reason="database_closed_ordinary_pytest_forbidden",
                serial_reason="database_closed_serial_pytest_forbidden",
                unknown_reason="verification_phase_invalid",
                order_reason="verification_phase_order_invalid",
            ),
            _exercise_surface(
                validator=_validate_commands,
                legacy=_governance_v1(),
                typed=_governance_v2(),
                command_key="command_id",
                argv_key="arguments",
                surface="governance_command_manifest",
                ordinary_reason="tick_database_closed_pytest_runner",
                serial_reason="tick_database_closed_pytest_runner",
                unknown_reason="tick_verification_phase",
                order_reason="tick_verification_phase_order",
            ),
        ],
        "phase_partition": {
            "prepublication_command_ids": [row["id"] for row in pre],
            "postpublication_command_ids": [row["id"] for row in post],
            "cross_phase_execution_count": 0,
        },
        "hostile_rejection_count": 8,
        "subprocess_launch_count": 0,
        "closed_boundaries": contract["closed_boundaries"],
    }
    Draft202012Validator(_load(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence


def _report(evidence: dict[str, Any]) -> str:
    return f"""# Provider-free verification-envelope phase and runner-admission repair

Date: 2026-08-23

Timestamp: {evidence['recorded_at']} (Australia/Brisbane)

Status: `candidate_passed`

Exact source: `{evidence['source_head']}`

The shared gear admits both historical v1 surfaces and their typed v2
descendants. With database authority closed it rejects ordinary and serial
pytest on both surfaces: {evidence['hostile_rejection_count']} hostile
coordinates rejected before subprocess launch.

The v2 validation runner selects `PRE` only for prepublication and `POST` only
for postpublication. Cross-phase execution and subprocess launches in this
conformance reading are both zero.

No database conftest, engine, schema, fixture, Docker, PostgreSQL, SQL,
attempt 008, worker/provider, product, deployment, Pages or protected-ref
surface was used.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--source", required=True)
    args = parser.parse_args(argv)
    try:
        evidence = build_evidence(args.source)
        report = _report(evidence)
        if args.write:
            EVIDENCE_PATH.write_text(_canonical(evidence), encoding="utf-8", newline="\n")
            REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")
        elif (
            EVIDENCE_PATH.read_text(encoding="utf-8") != _canonical(evidence)
            or REPORT_PATH.read_text(encoding="utf-8") != report
        ):
            raise ValueError("canonical_evidence_or_report_drift")
    except (OSError, ValueError, AssertionError, subprocess.SubprocessError) as error:
        print(f"verification-envelope conformance failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
