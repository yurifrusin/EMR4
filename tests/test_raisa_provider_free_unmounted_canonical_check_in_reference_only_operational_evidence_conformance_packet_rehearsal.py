"""Acceptance tests for the canonical check-in reference-only packet."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator, FormatChecker
import pytest

from app.services.appointment_check_in_environment_manifest import (
    normalize_check_in_environment_manifest,
)
from app.services.appointment_check_in_operational_evidence import (
    normalize_check_in_operational_evidence_inputs,
)
from scripts import (
    raisa_provider_free_unmounted_canonical_check_in_reference_only_operational_evidence_conformance_packet_rehearsal
    as rehearsal,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_DIR = rehearsal.CONTINUITY_DIR
PACKET_PATH = rehearsal.PACKET_PATH
PACKET_SCHEMA_PATH = CONTINUITY_DIR / "reference-only-packet.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_DIR / "evidence.schema.json"
CONTRACT_PATH = CONTINUITY_DIR / "contract.json"
CANDIDATE_SOURCE = "bd0bcc4689d1139c1025c1fe60ace2c9631e6c94"
PACKET_SHA256 = "c81a38d8d1892a7f02574a9f295a1ca507407dc637acb44e43736ac0f1532571"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert type(value) is dict
    return value


def _validate(instance: object, schema_path: Path) -> None:
    schema = _load(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    validator.validate(instance)


def _canonical_lf_sha256(path: Path) -> str:
    raw = path.read_bytes()
    if b"\r" in raw.replace(b"\r\n", b""):
        raise AssertionError(f"bare CR in {path}")
    canonical = raw.replace(b"\r\n", b"\n")
    canonical.decode("utf-8", errors="strict")
    return hashlib.sha256(canonical).hexdigest()


def test_packet_and_evidence_validate_against_closed_schemas() -> None:
    packet = _load(PACKET_PATH)
    _validate(packet, PACKET_SCHEMA_PATH)

    evidence = rehearsal.run_rehearsal(candidate_source=CANDIDATE_SOURCE)
    _validate(evidence, EVIDENCE_SCHEMA_PATH)


def test_closed_packet_schema_rejects_unlisted_nested_secret_field() -> None:
    packet = _load(PACKET_PATH)
    packet["manifest"]["secret_references"][0]["secret_value"] = "forbidden"

    with pytest.raises(Exception):
        _validate(packet, PACKET_SCHEMA_PATH)
    result = normalize_check_in_environment_manifest(
        rehearsal._manifest_bytes(packet["manifest"])
    )
    assert result.reason_code == "manifest_forbidden_field"


def test_canonical_path_satisfies_evidence_but_releases_no_ordinary_admission() -> None:
    evidence = rehearsal.run_rehearsal(candidate_source=CANDIDATE_SOURCE)

    assert evidence["canonical_path"] == {
        "manifest_reason": "manifest_normalized",
        "evidence_input_reason": "evidence_inputs_normalized",
        "evidence_gate_reason": "evidence_gate_satisfied",
        "base_admission_reason": "ordinary_activation_closed",
        "decision": "denied",
        "lane": "ordinary_practice",
        "reason": "ordinary_activation_closed",
        "admission_released": False,
        "ordinary_admission_released": False,
    }
    assert evidence["packet"]["operational_fact_status"] == "not_established"
    assert evidence["counts"]["admission_releases"] == 0
    assert evidence["counts"]["ordinary_admission_releases"] == 0


def test_all_twelve_hostile_cases_have_exact_reason_precedence() -> None:
    evidence = rehearsal.run_rehearsal(candidate_source=CANDIDATE_SOURCE)
    actual = tuple(
        (case["id"], case["evidence_gate_reason"], case["reason"])
        for case in evidence["hostile_cases"]
    )

    assert actual == rehearsal.EXPECTED_HOSTILE_REASONS
    assert all(case["base_admission_reason"] == "ordinary_activation_closed" for case in evidence["hostile_cases"])
    assert all(case["admission_released"] is False for case in evidence["hostile_cases"])
    assert all(
        case["ordinary_admission_released"] is False
        for case in evidence["hostile_cases"]
    )
    assert all(case["external_fact_count"] == 0 for case in evidence["hostile_cases"])


def test_packet_is_byte_stable_and_caller_input_is_not_mutated() -> None:
    before = PACKET_PATH.read_bytes()
    packet = _load(PACKET_PATH)
    caller_before = deepcopy(packet)

    file_evidence = rehearsal.run_rehearsal(candidate_source=CANDIDATE_SOURCE)
    memory_evidence = rehearsal.run_rehearsal(
        candidate_source=CANDIDATE_SOURCE,
        packet=packet,
    )

    assert PACKET_PATH.read_bytes() == before
    assert hashlib.sha256(before).hexdigest() == PACKET_SHA256
    assert file_evidence["packet"]["sha256"] == PACKET_SHA256
    assert file_evidence["packet"]["unchanged"] is True
    assert memory_evidence["packet"]["unchanged"] is True
    assert packet == caller_before


def test_packet_contains_references_only_and_no_forbidden_secret_material() -> None:
    packet = _load(PACKET_PATH)
    forbidden_fields = {
        "value",
        "secret_value",
        "password",
        "token",
        "private_key",
        "database_url",
        "connection_url",
        "environment_value",
        "resolved_secret",
    }

    def visit(value: object) -> None:
        if type(value) is dict:
            assert forbidden_fields.isdisjoint(value)
            for child in value.values():
                visit(child)
        elif type(value) is list:
            for child in value:
                visit(child)

    visit(packet)
    assert len(packet["manifest"]["secret_references"]) == 3
    assert normalize_check_in_operational_evidence_inputs(
        packet["operational_evidence"]
    ).reason_code == "evidence_inputs_normalized"


def test_six_external_facts_and_five_human_choices_remain_closed() -> None:
    evidence = rehearsal.run_rehearsal(candidate_source=CANDIDATE_SOURCE)

    assert len(evidence["external_facts"]) == 6
    assert {item["status"] for item in evidence["external_facts"]} == {"absent"}
    assert len(evidence["human_choices"]) == 5
    assert {item["status"] for item in evidence["human_choices"]} == {
        "unselected"
    }
    assert evidence["readiness"] == {
        "satisfied": 11,
        "blocking_gap": 0,
        "operational_evidence_gap": 1,
        "repository_prerequisites_remaining": 0,
        "verdict": "not_ready_for_ordinary_practice_admission",
    }


def test_rehearsal_source_has_no_ambient_or_write_capability() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    banned_import_roots = {
        "asyncpg",
        "httpx",
        "os",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "urllib",
    }
    banned_calls = {
        "connect",
        "getenv",
        "open",
        "popen",
        "putenv",
        "urlopen",
        "write_bytes",
        "write_text",
    }

    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    attributes = {
        node.func.attr.casefold()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    names = {
        node.func.id.casefold()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert imports.isdisjoint(banned_import_roots)
    assert attributes.isdisjoint(banned_calls)
    assert names.isdisjoint(banned_calls)
    assert "app.routers" not in source
    assert "app.main" not in source


def test_contract_hashes_and_full_git_objects_are_exact_ancestors() -> None:
    contract = _load(CONTRACT_PATH)
    assert contract["input_hash_mode"] == (
        "strict_utf8_canonical_lf_reject_bare_cr_sha256"
    )
    for item in contract["inputs"]:
        path = REPO_ROOT / item["path"]
        assert _canonical_lf_sha256(path) == item["sha256"]
    for git_object in contract["accepted_git_objects"].values():
        assert rehearsal.FULL_GIT_OBJECT.fullmatch(git_object)
        assert subprocess.run(
            ["git", "cat-file", "-e", f"{git_object}^{{commit}}"],
            cwd=REPO_ROOT,
            check=False,
        ).returncode == 0
        assert subprocess.run(
            ["git", "merge-base", "--is-ancestor", git_object, "HEAD"],
            cwd=REPO_ROOT,
            check=False,
        ).returncode == 0


def test_short_candidate_source_fails_closed() -> None:
    with pytest.raises(
        rehearsal.RehearsalFailure,
        match="candidate_source_not_full_git_object",
    ):
        rehearsal.run_rehearsal(candidate_source="bd0bcc4")


def test_markdown_report_is_complete_and_non_admitting() -> None:
    evidence = rehearsal.run_rehearsal(candidate_source=CANDIDATE_SOURCE)
    report = rehearsal.render_report(evidence)

    assert "ordinary_activation_closed" in report
    assert "11 satisfied / 0 blocking / 1 operational" in report
    assert all(case_id in report for case_id, _gate, _reason in rehearsal.EXPECTED_HOSTILE_REASONS)
    assert "released no ordinary-practice admission" in report
