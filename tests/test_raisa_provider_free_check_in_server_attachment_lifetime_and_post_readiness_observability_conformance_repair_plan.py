from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-check-in-server-attachment-lifetime-and-"
    "post-readiness-observability-conformance-repair-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-server-attachment-lifetime-"
    "and-post-readiness-observability-conformance-repair-threat-model-delta.md"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_full_git_lineage_and_immutable_attempt_004() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "dccddf16d4c617a34ba006f09e9bda9373a4e731",
        "4908bf53265e1356a9c5dac84a05b05702ad6d34",
        "a6a292e36978aa95e439fa398242c67816b6d4cc",
        "958ae762e7c6a065b5926f47eb1a2b63115212c7",
        "5ff79d68f6df25d8bebdba78a6d504afb64de2ab",
        "4f0f54c2b0861828f9994444201b8da1bd54be00",
        "6a2832575e9b4df5c40a13984db7281e79814a94",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "Attempt 004 remains consumed" in plan
    bindings = {
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-004/rehearsal-failure-evidence.json": "1ccc86c76826aa805a48a8823186f5b0eee6e0b571f6deff59ece0474f5df4d3",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-004/attempt-004-execution-envelope.json": "415f054f10639c2dba2466842ad7b957ce9a66f71f48bf07abe5bfdf4e47e7d5",
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py": "eda68427b87db48064bcfb82762d55c51b600cf2ba5d4724a0faae24d8a3db5b",
    }
    for path, digest in bindings.items():
        assert _sha256(path) == digest
        assert digest in plan
        assert f"`{path}`" in plan


def test_plan_freezes_lifetime_and_diagnostic_semantics() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").split())
    for phrase in (
        "must not set the handle to `None` after readiness",
        "inspect the captured server exactly once",
        "server_not_running_after_readiness",
        "server_identity_mismatch_after_readiness",
        "sorted, comma-joined failed predicate names",
        "append `relay_free_server_readiness_verified` only after",
        "final `finally` block remains the sole attachment teardown owner",
        "malformed-inspection fallback remains the sanitized predicate `inspect_shape`",
    ):
        assert phrase in plan


def test_plan_admits_one_bounded_native_harness_worker() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    for phrase in (
        "one `ariadne.deepseek_work_order.v2`",
        "one passing static no-database admission artifact",
        "one clockwork one-run latch",
        "exactly `read`, `glob`, `edit`",
        "zero automatic retries, zero fallback",
        "worker has no shell",
        "Claude Code is not a fallback",
        "A terminal worker failure consumes the one model attempt",
    ):
        assert phrase in normalized
    assert "**DeepSeek native Harness:** `planned`" in plan
    assert "**Gemini:** `reserved`" in plan
    assert "**Native subagents:** `declined`" in plan


def test_plan_preserves_provider_free_api_and_protected_boundaries() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "no docker object creation",
        "ordinary pytest, docker, postgresql",
        "graphql remains read-only",
        "explicit actor and practice scope",
        "atomic effect/receipt/audit",
        "dedicated check-in remains default-off",
        "generic status does not gain `arrived`",
        "preserves `docs/branding/`",
        "`git add .` and `git add -a` are forbidden",
    ):
        assert phrase in plan
    assert "grants no docker, database, product, ordinary-practice" in threat
    assert "cannot prove" in threat


def test_clockwork_is_the_only_canonical_writer() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").split())
    assert "clockwork is the sole writer of canonical governance surfaces" in plan
    assert "must run `--check` before a separate `--publish`" in plan
