from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-007-plan.md"
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-recovery-attempt-007-"
    "threat-model-delta.md"
)
SCHEMA = ROOT / (
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-"
    "attempt-007/attempt-007-execution-envelope.schema.json"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_seventh_single_execution_and_full_git_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-23T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "f30b82ea0b80bdef2fa8d63549ba78d39d14e24d",
        "a9567be36c82bc6d2eebc2488b48cd8bfb9f8d23",
        "53760513c42a380904136eb4ef2f5ffda397e820",
        "022d780726c74cb285d5b626cd004821b4e5ff47",
        "8814d4b5d62885f8f8eca4cf02fe5a49ccdc013b",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "exactly one local provider-free disposable PostgreSQL 16 execution" in normalized
    assert "This plan has no retry, resume or fallback path" in normalized


def test_plan_binds_exact_repair_and_predecessor_inputs() -> None:
    bindings = {
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py": "1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-006/rehearsal-failure-evidence.json": "3c7049b318fffb28aa70e8b4346f1ed857b7cf34e1780eec21373935f6c88efd",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-006/attempt-006-execution-envelope.json": "52470c6c6245f0988dd4f580e68f7a0e21ce5b8636e60119091c089d603bde1c",
        "orchestration/continuity/raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-conformance-repair/repair-attestation.json": "73d5773d3662509ec2cdb8d8f109651b77ef79be42f5b641f07e36d7ca8bcf91",
        "orchestration/continuity/raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-conformance-repair/contract.json": "de9106afdd69db62eaaf6888ba780e65596838c162f2f1db5cc2703b893bf8d7",
        "orchestration/continuity/raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-conformance-repair/repair-report.md": "35afc06958477556f9d0689a99fad26babb8e15fb268d90b1cb983321ee9fee4",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/contract.json": "bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/transaction-attestation.schema.json": "d2c186b0d30419e0459d93d92af1f84907125becdeb75c7e1890dce597d3e72c",
    }
    plan = PLAN.read_text(encoding="utf-8")
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan


def test_plan_freezes_serial_adapter_and_database_boundaries() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "no caller-supplied output path",
        "restores all three unconditionally in `finally`",
        "refuses execution if any attempt-007 terminal already exists",
        "no automatic or manual retry",
        "one sol controller owns every acquisition and cleanup",
        "construction creates no docker or database resource",
    ):
        assert phrase in plan


def test_plan_preserves_api_spine_parallelism_and_protected_boundaries() -> None:
    plan_text = PLAN.read_text(encoding="utf-8")
    plan = " ".join(plan_text.lower().split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "graphql remains read-only",
        "explicit actor and practice scope",
        "idempotency identity",
        "atomic effect/receipt/audit",
        "default denial",
        "forced rls",
        "preserves `docs/branding/`",
        "`git add .`",
    ):
        assert phrase in plan
    assert "**DeepSeek native Harness:** `declined`" in plan_text
    assert "**Gemini:** `declined`" in plan_text
    assert "**Native subagents:** `declined`" in plan_text
    assert "neither result grants model-provider, product, ordinary-practice" in threat


def test_attempt_007_envelope_schema_is_closed_and_non_retriable() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    properties = schema["properties"]
    assert properties["attempt_id"] == {"const": "attempt-007"}
    assert properties["occupied_execution_count"] == {"const": 1}
    assert properties["automatic_retry_count"] == {"const": 0}
    assert properties["ambiguous_success_released"] == {"const": False}
    assert properties["ordinary_admission_release_count"] == {"const": 0}
    assert properties["product_record_count"] == {"const": 0}
