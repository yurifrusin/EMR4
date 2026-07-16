"""Pre-execution binding checks for the sole LC4V10 attempt."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from app.services.bernie.lc4v10_content_blind_framework import (
    MANIFEST_KEYS,
    MANIFEST_SCHEMA,
    MARKER_SCHEMA,
    REPORT_KEYS,
    REPORT_SCHEMA,
    SEAL_KEYS,
    SEAL_SCHEMA,
)
from app.services.bernie import lc4v10_protected_sealing as sealing

ROOT = Path(__file__).resolve().parents[1]
CONSUMED = (ROOT / sealing.MARKER_PATH).exists()


@pytest.mark.skipif(CONSUMED, reason="LC4V10 already consumed")
def test_source_commit_is_ancestor_and_every_bound_blob_is_exact() -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert subprocess.run(
        ["git", "merge-base", "--is-ancestor", sealing.SOURCE_COMMIT, head],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    manifest = sealing.build_manifest(ROOT)
    assert set(manifest) == MANIFEST_KEYS
    assert manifest["schema_version"] == MANIFEST_SCHEMA
    assert manifest["corpus_source_commit"] == sealing.SOURCE_COMMIT


@pytest.mark.skipif(CONSUMED, reason="LC4V10 already consumed")
def test_durable_manifest_and_unconsumed_seal_are_exact() -> None:
    manifest_bytes = (ROOT / sealing.MANIFEST_PATH).read_bytes()
    seal_bytes = (ROOT / sealing.SEAL_PATH).read_bytes()
    manifest = json.loads(manifest_bytes)
    seal = json.loads(seal_bytes)
    assert manifest == sealing.build_manifest(ROOT)
    assert seal == sealing.build_seal(ROOT, manifest)
    assert set(seal) == SEAL_KEYS
    assert seal["schema_version"] == SEAL_SCHEMA
    assert seal["state"] == "unconsumed"
    canonical_manifest = json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8") + b"\n"
    assert seal["manifest_sha256"] == hashlib.sha256(canonical_manifest).hexdigest()


def test_consumed_marker_seal_and_aggregate_are_exact() -> None:
    marker_path = ROOT / sealing.MARKER_PATH
    seal_path = ROOT / sealing.SEAL_PATH
    report_path = ROOT / sealing.REPORT_PATH
    assert marker_path.exists() and report_path.exists()
    marker = json.loads(marker_path.read_bytes())
    seal = json.loads(seal_path.read_bytes())
    report = json.loads(report_path.read_bytes())
    assert marker == {
        "schema_version": MARKER_SCHEMA,
        "attempt_id": "lc4v10-fresh-certification-001",
        "state": "consumed",
    }
    assert set(seal) == SEAL_KEYS
    assert seal["schema_version"] == SEAL_SCHEMA
    assert seal["state"] == "consumed"
    assert set(report) == REPORT_KEYS
    assert report["schema_version"] == REPORT_SCHEMA
    assert report["decision"] == "certification_pass"
    assert report["attempted_samples"] == 576
    assert report["dimension_counts"] == {
        "action_semantics": 576,
        "clarification_composition": 576,
        "complete": 576,
        "entity_semantics": 576,
        "exact_policy_projection": 576,
        "extraction_clarification": 576,
        "intended_action": 576,
        "interpretation_tool": 576,
        "lossless_source_spans": 576,
        "normalized_values": 576,
        "policy_behavior": 576,
        "policy_clarification": 576,
        "replay": 576,
        "safety": 576,
        "temporal_relation_and_bounds": 576,
    }
    assert not report["evidence_failures"]
    assert not report["product_gate_failures"]
    without_hash = {key: value for key, value in report.items() if key != "report_hash"}
    canonical = json.dumps(
        without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert report["report_hash"] == hashlib.sha256(canonical).hexdigest()
    rendered = json.dumps(report, sort_keys=True)
    for forbidden in ("utterances", "expected", "patient", "practitioner", "scenario_id"):
        assert forbidden not in rendered
    assert hashlib.sha256(seal_path.read_bytes()).hexdigest() == (
        "3d12da4fa39337c1e7f7f690f9cb49a0ca6f40b92ab842d8623932453b0fc945"
    )
    assert hashlib.sha256(marker_path.read_bytes()).hexdigest() == (
        "a32e99ed7ec90f41717ebce788958d15e418a1c4317616ac5545ffa070b51a17"
    )
    assert hashlib.sha256(report_path.read_bytes()).hexdigest() == (
        "5986691e8034f31d22d0b107d7d73c6d701b989ed1757d1381e04f251b8b3456"
    )
