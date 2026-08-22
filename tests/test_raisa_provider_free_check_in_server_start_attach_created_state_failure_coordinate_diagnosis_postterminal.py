from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
OPERATION_DIR = ROOT / "orchestration" / "continuity" / (
    "raisa-provider-free-read-only-check-in-server-start-attach-created-state-"
    "failure-coordinate-diagnosis"
)
EVIDENCE_PATH = OPERATION_DIR / "diagnosis-evidence.json"
SCHEMA_PATH = OPERATION_DIR / "diagnosis-evidence.schema.json"
REPORT_PATH = OPERATION_DIR / "diagnosis-report.md"
HARNESS_PATH = ROOT / "scripts" / (
    "raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_"
    "rollback_unknown_commit_recovery_rehearsal.py"
)
HARNESS_REPOSITORY_PATH = HARNESS_PATH.relative_to(ROOT).as_posix()


def test_terminal_is_canonical_schema_valid_and_exactly_bound() -> None:
    raw = EVIDENCE_PATH.read_bytes()
    evidence = json.loads(raw)
    assert raw == (
        json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert hashlib.sha256(raw).hexdigest() == (
        "924ca23b361770fa31037232aa342e39c377e91685ac7137d1bb4da264647bb0"
    )


def test_terminal_source_is_full_commit_ancestor() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    source = evidence["source_head"]
    assert re.fullmatch(r"[0-9a-f]{40}", source)
    subprocess.run(
        ["git", "cat-file", "-e", f"{source}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )


def test_terminal_releases_only_the_closed_cli_mismatch() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert evidence["coordinate"] == "cli_option_surface_mismatch"
    assert evidence["source_coordinate"]["unsupported_options"] == ["--sig-proxy"]
    assert evidence["unresolved_causes"] == []
    assert evidence["repair"]["implemented"] is False
    assert evidence["repair"]["attempt_007_authorized"] is False
    assert all(value == 0 for value in evidence["closed_boundaries"].values())


def test_no_raw_output_or_dynamic_failure_text_is_retained() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(evidence, sort_keys=True)
    for prohibited in (
        "raw_stdout",
        "raw_stderr",
        "stack",
        "credential",
        "owner-nonce",
    ):
        assert prohibited not in serialized


def test_database_harness_remains_exact_and_report_names_future_repair() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    historical = subprocess.run(
        ["git", "show", f"{evidence['source_head']}:{HARNESS_REPOSITORY_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert hashlib.sha256(historical).hexdigest() == (
        "839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2"
    )
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert "`cli_option_surface_mismatch`" in report
    assert "remove only the unsupported `--sig-proxy=false` argument" in report
    assert "no repaired command has run" in report.lower()
