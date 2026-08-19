from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-002-plan.md"
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-recovery-attempt-002-"
    "threat-model-delta.md"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_distinct_single_execution_and_full_git_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "4012ce578b0409c72215a624b1c4f115e45a7d60",
        "fc772085a02d7db790b938fb845ef4546156d31e",
        "4f0f54c2b0861828f9994444201b8da1bd54be00",
        "6a2832575e9b4df5c40a13984db7281e79814a94",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "authorises exactly one attempt-002 occupied execution" in plan
    assert "may not be rerun under this plan" in plan


def test_plan_binds_immutable_attempt_001_and_transition_evidence() -> None:
    bindings = {
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence.json": "5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/attempt-001-cleanup-recovery.json": "a8920b0a294b43c8f67d0348bc6087b84921f8f8788ccd3f969913d95861c06a",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/contract.json": "bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/clockwork-tick-evidence.json": "a7cbc9e7ce683f0cbd53e95d40e54f01a4bce43a688c7a0a93ff0794f90c3cae",
    }
    plan = PLAN.read_text(encoding="utf-8")
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan


def test_plan_freezes_output_collision_and_no_arbitrary_path() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "caller-supplied or arbitrary filesystem output path",
        "attempt-002-execution-envelope.json",
        "refuse any pre-existing terminal file",
        "no automatic or manual retry",
        "no host tcp listener",
        "exact terminal oci state",
        "remain byte-for-byte unchanged",
        "restore all three in a `finally` block",
    ):
        assert phrase in plan


def test_plan_preserves_api_spine_and_protected_boundaries() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "graphql remains read-only",
        "explicit practice scope",
        "idempotency",
        "audit atomicity",
        "default denial",
        "forced rls",
        "no ordinary-practice enablement",
        "protected-ref movement",
        "preserve `docs/branding/`",
        "explicit paths only",
    ):
        assert phrase in plan
    assert "grants no product or ordinary-practice authority" in threat


def test_parallelism_is_explicit_and_database_lifecycle_is_serial() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "**DeepSeek:** declined" in plan
    assert "**Gemini:** reserved" in plan
    assert "**Native subagents:** declined" in plan
    assert "one cleanup owner" in plan
