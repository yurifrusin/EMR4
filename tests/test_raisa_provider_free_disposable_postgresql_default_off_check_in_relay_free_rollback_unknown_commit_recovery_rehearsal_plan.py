from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-"
    "rollback-unknown-commit-recovery-rehearsal-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-disposable-postgresql-default-off-check-in-"
    "relay-free-rollback-unknown-commit-recovery-rehearsal-threat-model-delta.md"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_full_git_sources_and_one_execution() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "b5afa75bfc759efa689d35cd06c5b330e4b7ed05",
        "4f0f54c2b0861828f9994444201b8da1bd54be00",
        "6a2832575e9b4df5c40a13984db7281e79814a94",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "exactly one newly named disposable execution is authorised" in plan
    assert "may not be rerun under this plan" in plan


def test_plan_binds_accepted_transport_and_all_predecessor_failures() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    bindings = {
        "docs/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign-plan.md": "3b88e96110a33437895a993dfca7e44164e7a342c420c53cc7f366851f424f1b",
        "orchestration/continuity/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign/transport-evidence.json": "0b5a5a0c6e9d95e87907d6f4f0db264640dd1be35eb4c82a4b55841d0e92ebd0",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence-attempt-001.json": "e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence-attempt-002.json": "bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence-attempt-003.json": "15cebad64c7bfbddb83878e75cf8f3a0d137a7834075e063c92aead8b603e219",
    }
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan


def test_plan_removes_failed_host_control_paths() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "no host tcp listener",
        "docker-exec byte bridge",
        "multiprocessing process or queue",
        "attached stdin",
        "exact terminal oci state",
        "no command is reissued",
        "fresh restricted authoritative readback sidecar",
    ):
        assert phrase in plan


def test_plan_preserves_api_spine_product_and_tenant_boundaries() -> None:
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


def test_worker_mix_is_explicit_and_serial() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "**DeepSeek:** declined" in plan
    assert "**Gemini:** reserved" in plan
    assert "**Native subagents:** declined" in plan
    assert "one cleanup owner" in plan
