from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-check-in-relay-free-profile-call-site-and-"
    "pre-registry-cleanup-conformance-repair-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-profile-call-site-"
    "and-pre-registry-cleanup-conformance-repair-threat-model-delta.md"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_exact_sources_and_no_occupied_execution() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "78e0202343b4a925a0674e58486d8616df7f7599",
        "19e4414fec067fcbb6af12818e432953432878be",
        "d2c6f7e465b1bcf2f8cf458a8fbd5721631db422",
        "02a1fbfaa517a0d2a2dff66f31fabe482653c430",
        "260eeda97a3204a39b0f639d216fd7a53c0d2014",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "does not reopen or retry attempt 003" in normalized
    assert "may not create a Docker object" in normalized


def test_plan_binds_failure_cleanup_and_created_state_evidence() -> None:
    bindings = {
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/rehearsal-failure-evidence.json": "e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/attempt-003-execution-envelope.json": "91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/attempt-003-cleanup-recovery.json": "048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71",
        "orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/created-state-representation-evidence.json": "9f721e0d0e11f5570c2ebe95f8e62d4f1f0e7b2af27f704e4108e2f1792fb98b",
        "orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/repair-attestation.json": "49c5a3673d388fc84b2f046a993a8f4c747f9887252ef4cdd2dfcc59e9a11410",
    }
    plan = PLAN.read_text(encoding="utf-8")
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan
    assert "6965328b6dce6ecf939e86456bfcd99f1bdee7d32202e276f37454796e012b6b" in plan


def test_plan_freezes_two_call_sites_and_cleanup_invariants() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "`_create_server` passes its captured `network_name`",
        "`_create_sidecar` passes its captured `network_name`",
        "post-create/pre-registry exception",
        "full resolved id shape",
        "exact name/image/harness-label/nonce ownership",
        "`created` state and `running=false`",
        "remove only the resolved full id",
        "no accepted profile predicate",
        "every exact verifier assertion is executed locally",
        "clockwork check and publish remain separate commands",
    ):
        assert phrase in plan


def test_parallelism_and_protected_boundaries_are_explicit() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").lower().split())
    assert "**DeepSeek:** declined" in plan
    assert "**Gemini:** reserved" in plan
    assert "**Native subagents:** declined" in plan
    for phrase in (
        "no docker or database execution",
        "no product or ordinary-practice authority",
        "protected-ref movement",
    ):
        assert phrase in threat
    assert "preserve `docs/branding/`" in plan.lower()
    assert "explicit paths only" in plan.lower()
