from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-006-plan.md"
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-recovery-attempt-006-"
    "threat-model-delta.md"
)
SCHEMA = ROOT / (
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-"
    "attempt-006/attempt-006-execution-envelope.schema.json"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_sixth_single_execution_and_full_git_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-23T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "5b2659de15bfd95380619bfb7143fffba6817e5a",
        "905184b76f576006232fcfdc78da71d98fcf0ca0",
        "03b94136c9c6cd82d5a8098705f263ba34a20de4",
        "0c2918e78e86ecd006190850ee29f7c58766fa20",
        "7d39641c3170fc0fec76fadce5cd45309bdffdb2",
        "3ee2b9c074864b12225338d8559fd4226bac2a7a",
        "4f0f54c2b0861828f9994444201b8da1bd54be00",
        "6a2832575e9b4df5c40a13984db7281e79814a94",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "exactly one local provider-free disposable PostgreSQL 16 execution" in normalized
    assert "This plan has no retry, resume or fallback path" in plan


def test_plan_binds_exact_repair_and_predecessor_inputs() -> None:
    bindings = {
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py": "839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-005/rehearsal-failure-evidence.json": "a9e6331471dadc06ddc1fc7f5f6e9510a231fa7cd3a0fc748495f8c9794bb887",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-005/attempt-005-execution-envelope.json": "dedfcbf008ea11c9dac9241a59c900582f5ca82a1de003bcd9f740409c0bbb54",
        "orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/repair-evidence.json": "cbc4ec27435784a45cbff3835028abb5ab18b77eb1c6307fd883e6652f0e0388",
        "orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/repair-report.md": "940297ceab52cf1d82f0607cbd53fa8c033f18a707f831ae471d506f01431f54",
        "orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/contract.json": "db8f31b6bef8fefe7c0af523d452c6598029c1482736219c6006636f3b624b17",
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
        "refuses execution if any attempt-006 terminal already exists",
        "no automatic or manual retry",
        "one sol controller owns every acquisition and cleanup",
        "no docker or database resource",
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
    assert "grants no model-provider, product or ordinary-practice authority" in threat


def test_attempt_006_envelope_schema_is_closed_and_non_retriable() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    properties = schema["properties"]
    assert properties["attempt_id"] == {"const": "attempt-006"}
    assert properties["occupied_execution_count"] == {"const": 1}
    assert properties["automatic_retry_count"] == {"const": 0}
    assert properties["ambiguous_success_released"] == {"const": False}
    assert properties["ordinary_admission_release_count"] == {"const": 0}
    assert properties["product_record_count"] == {"const": 0}
