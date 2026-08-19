from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-004-plan.md"
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-recovery-attempt-004-"
    "threat-model-delta.md"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_distinct_single_execution_and_full_git_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-20T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "1ddfb4819b161e64731f73ecf80b540ac4e5a9fd",
        "19e4414fec067fcbb6af12818e432953432878be",
        "d2c6f7e465b1bcf2f8cf458a8fbd5721631db422",
        "95d456a1e3861ae463cf3643f347fa666c75fa48",
        "8bda88069daeb314998341fc961b9aa061d496e5",
        "958ae762e7c6a065b5926f47eb1a2b63115212c7",
        "5ff79d68f6df25d8bebdba78a6d504afb64de2ab",
        "4f0f54c2b0861828f9994444201b8da1bd54be00",
        "6a2832575e9b4df5c40a13984db7281e79814a94",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "exactly one occupied local execution" in normalized
    assert "This plan has no retry path" in plan


def test_plan_binds_all_consumed_attempts_and_corrective_controls() -> None:
    bindings = {
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence.json": "5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/attempt-001-cleanup-recovery.json": "a8920b0a294b43c8f67d0348bc6087b84921f8f8788ccd3f969913d95861c06a",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/rehearsal-failure-evidence.json": "7efb9853beee9723dbb01fac1f03c4392216bfcc15e9f490f4cb0baae08920ff",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/attempt-002-execution-envelope.json": "6418ecf2e2356b6c875a70106136cdc65d6e545ead5fceeb2c793db45ebe2e40",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/rehearsal-failure-evidence.json": "e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/attempt-003-execution-envelope.json": "91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/attempt-003-cleanup-recovery.json": "048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71",
        "orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/created-state-representation-evidence.json": "9f721e0d0e11f5570c2ebe95f8e62d4f1f0e7b2af27f704e4108e2f1792fb98b",
        "orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/repair-attestation.json": "49c5a3673d388fc84b2f046a993a8f4c747f9887252ef4cdd2dfcc59e9a11410",
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py": "eda68427b87db48064bcfb82762d55c51b600cf2ba5d4724a0faae24d8a3db5b",
        "orchestration/continuity/ariadne-provider-free-no-database-manifest-runner-admission-repair/provider-free-no-database-admission-evidence.json": "9770af5d6d8e4282456e2ddd43ce6359c5dbff13b974c7d37a887fab331476d8",
        "orchestration/continuity/deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-boot-proof/provider-free-native-harness-hmr-boot-evidence.json": "68d4168649d80268fdb81ba3582bed261e7944fc0f19d24aee5933270882afcc",
    }
    plan = PLAN.read_text(encoding="utf-8")
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan


def test_plan_freezes_collision_repaired_lifecycle_and_no_retry() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "no caller-supplied output path",
        "attempt-004-execution-envelope.json",
        "refuse execution if any attempt-004 terminal path already exists",
        "no automatic or manual retry",
        "both real call sites pass `network_name`",
        "pre-registry cleanup interval is owned",
        "no forbidden host relay",
        "exact terminal oci state",
        "restore all three unconditionally in `finally`",
        "one cleanup owner",
    ):
        assert phrase in plan


def test_plan_preserves_api_spine_and_protected_boundaries() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "graphql is read-only",
        "explicit actor and practice scope",
        "idempotency identity",
        "atomic receipt/effect/audit",
        "default denial",
        "forced rls",
        "no product, patient, appointment, clinical, historical or protected data",
        "preserves `docs/branding/`",
        "`git add .`",
    ):
        assert phrase in plan
    assert "grants no product, ordinary-practice or model authority" in threat


def test_clockwork_and_parallelism_controls_are_explicit() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "**DeepSeek:** declined" in plan
    assert "**Gemini:** reserved" in plan
    assert "**Native subagents:** declined" in plan
    assert "a clockwork checkpoint `--check`" in plan
    assert "a separate `--publish`" in normalized
    assert "No verifier call occurs during planning" not in plan
    assert "no verifier call occurs during planning" in plan
