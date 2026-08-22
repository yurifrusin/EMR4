from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
OPERATION_DIR = ROOT / "orchestration" / "continuity" / (
    "raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-"
    "conformance-repair"
)
ATTESTATION = OPERATION_DIR / "repair-attestation.json"
SCHEMA = OPERATION_DIR / "repair-attestation.schema.json"
REPORT = OPERATION_DIR / "repair-report.md"
HARNESS = ROOT / "scripts" / (
    "raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_"
    "rollback_unknown_commit_recovery_rehearsal.py"
)


def test_attestation_is_canonical_schema_valid_and_exact() -> None:
    raw = ATTESTATION.read_bytes()
    value = json.loads(raw)
    assert raw == (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    jsonschema.Draft202012Validator(
        json.loads(SCHEMA.read_text(encoding="utf-8"))
    ).validate(value)
    assert hashlib.sha256(raw).hexdigest() == (
        "73d5773d3662509ec2cdb8d8f109651b77ef79be42f5b641f07e36d7ca8bcf91"
    )


def test_source_is_full_commit_ancestor_and_harness_is_exact() -> None:
    value = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    source = value["source_head"]
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
    assert hashlib.sha256(HARNESS.read_bytes()).hexdigest() == (
        "1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16"
    )


def test_exact_one_token_repair_and_closed_authority() -> None:
    value = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    assert value["exact_diff"] == {
        "pre_repair_sha256": "839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2",
        "post_repair_sha256": "1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16",
        "removed_tokens": ["--sig-proxy=false"],
        "added_tokens": [],
        "other_harness_changes": 0,
    }
    assert value["repair"]["implemented"] is True
    assert value["repair"]["attempt_007_authorized"] is False
    assert all(count == 0 for count in value["closed_boundaries"].values())


def test_stdin_and_teardown_relations_remain_closed() -> None:
    value = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    assert value["stdin_lifecycle"] == {
        "payload": "two_lines_ascii_newline_terminated",
        "write_count": 1,
        "flush_count": 1,
        "open_after_delivery": True,
        "normal_path_close_count": 0,
    }
    assert value["signal_and_teardown"] == {
        "docker_attach_default_forwards_signals": True,
        "normal_path_terminate_count": 0,
        "normal_path_kill_count": 0,
        "teardown_stdin_close_count": 1,
        "teardown_terminate_count": 1,
        "teardown_wait_count": 1,
        "teardown_kill_count": 0,
        "teardown_result": "attachment_absent",
    }


def test_report_preserves_historical_diagnosis_and_denies_attempt_007() -> None:
    text = REPORT.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "zero other harness changes" in normalized
    assert "Historical diagnosis bytes remain unchanged" in text
    assert "Attempt 007 is not authorised" in normalized
