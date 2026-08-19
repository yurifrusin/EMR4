from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-003-plan.md"
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-recovery-attempt-003-"
    "threat-model-delta.md"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_distinct_single_execution_and_full_git_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "dd9f0f8469b04bd91ddf38888032ce38a93926a5",
        "02a1fbfaa517a0d2a2dff66f31fabe482653c430",
        "260eeda97a3204a39b0f639d216fd7a53c0d2014",
        "cf7e86c19e0a33c9702359f4ee4439c4f86ff977",
        "4f0f54c2b0861828f9994444201b8da1bd54be00",
        "6a2832575e9b4df5c40a13984db7281e79814a94",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "exactly one newly named attempt-003 occupied execution" in normalized
    assert "may not be rerun under this plan" in normalized


def test_plan_binds_consumed_attempts_and_corrective_evidence() -> None:
    bindings = {
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence.json": "5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/attempt-001-cleanup-recovery.json": "a8920b0a294b43c8f67d0348bc6087b84921f8f8788ccd3f969913d95861c06a",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/rehearsal-failure-evidence.json": "7efb9853beee9723dbb01fac1f03c4392216bfcc15e9f490f4cb0baae08920ff",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/attempt-002-execution-envelope.json": "6418ecf2e2356b6c875a70106136cdc65d6e545ead5fceeb2c793db45ebe2e40",
        "orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/created-state-representation-evidence.json": "9f721e0d0e11f5570c2ebe95f8e62d4f1f0e7b2af27f704e4108e2f1792fb98b",
        "orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/repair-attestation.json": "49c5a3673d388fc84b2f046a993a8f4c747f9887252ef4cdd2dfcc59e9a11410",
    }
    plan = PLAN.read_text(encoding="utf-8")
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan
    assert "6965328b6dce6ecf939e86456bfcd99f1bdee7d32202e276f37454796e012b6b" in plan


def test_plan_freezes_output_collision_and_corrected_profile() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "caller-supplied or arbitrary filesystem output path",
        "attempt-003-execution-envelope.json",
        "refuse any pre-existing terminal file",
        "no automatic or manual retry",
        "no host tcp listener",
        "exact terminal oci state",
        "remain byte-for-byte unchanged",
        "restore all three in a `finally` block",
        "sole network map key equals the captured network name",
        "empty before attachment or the captured id after attachment",
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


def test_clockwork_and_parallelism_controls_are_explicit() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "**DeepSeek:** declined" in plan
    assert "**Gemini:** reserved" in plan
    assert "**Native subagents:** declined" in plan
    assert "one cleanup owner" in plan
    assert "separate clockwork check" in plan
    assert "separate publish" in plan
    assert "every exact verifier assertion is executed locally" in plan
