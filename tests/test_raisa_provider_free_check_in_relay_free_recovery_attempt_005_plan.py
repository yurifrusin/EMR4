from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-005-plan.md"
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-recovery-attempt-005-"
    "threat-model-delta.md"
)
SCHEMA = ROOT / (
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-"
    "attempt-005/attempt-005-execution-envelope.schema.json"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_fifth_single_execution_and_full_git_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-20T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "f270fd0be764230ca189cd08dabd8135409cad9e",
        "932ae6ce02e0e973a22dfe999601087295001d1b",
        "4908bf53265e1356a9c5dac84a05b05702ad6d34",
        "cfc7eb472aaaa4fdf7ffef35b07a65a2729073c5",
        "9f9984e0575beb7b300035fdb74433f5bef32028",
        "f9a4ede953cc496e9b778a6162d77dc7e73121df",
        "6ef058b87a2c927efd9d9d2027b59d6ad279fec5",
        "958ae762e7c6a065b5926f47eb1a2b63115212c7",
        "4f0f54c2b0861828f9994444201b8da1bd54be00",
        "6a2832575e9b4df5c40a13984db7281e79814a94",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "exactly one occupied local disposable PostgreSQL execution" in normalized
    assert "This plan has no retry path" in plan


def test_plan_binds_exact_repair_worker_and_predecessor_inputs() -> None:
    bindings = {
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py": "62a18d9ce2a29eb417f491c8ce341416f03183375f042f8c41bcb1f4674df77c",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-004/rehearsal-failure-evidence.json": "1ccc86c76826aa805a48a8823186f5b0eee6e0b571f6deff59ece0474f5df4d3",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-004/attempt-004-execution-envelope.json": "415f054f10639c2dba2466842ad7b957ce9a66f71f48bf07abe5bfdf4e47e7d5",
        "orchestration/continuity/raisa-provider-free-check-in-server-attachment-lifetime-and-post-readiness-observability-conformance-repair/repair-report.md": "0cf005adab3b6117ec19409aa2ce95bfbe1ec8c285b56bd7d6564c6b97252c88",
        "orchestration/continuity/deepseek-native-harness-provider-free-complete-composition-native-boot-recovery/provider-free-complete-composition-native-boot-evidence.json": "9ba784b0726addb5644ac3786def410aed56e5bf9da3e23ec21d8e10f6ba1ea0",
        "orchestration/continuity/ariadne-provider-free-no-database-manifest-runner-admission-repair/work-order-v2.schema.json": "71c87760ff9351b60704b5b2dcf7d3c43c96a36b2c41a53057e3f497b6fc0a5b",
        "orchestration/continuity/ariadne-provider-free-no-database-manifest-runner-admission-repair/provider-free-no-database-admission-evidence.json": "9770af5d6d8e4282456e2ddd43ce6359c5dbff13b974c7d37a887fab331476d8",
    }
    plan = PLAN.read_text(encoding="utf-8")
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan


def test_plan_freezes_worker_and_database_one_run_boundaries() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "only the new attempt-005 adapter and its focused test",
        "exactly `edit`, `glob`, `read`",
        "no shell, test, docker, database, git",
        "claude code is not a fallback",
        "no caller-supplied output path",
        "refuse execution if any attempt-005 terminal path already exists",
        "restore all three unconditionally in `finally`",
        "no automatic or manual retry",
        "one sol controller is the cleanup owner",
    ):
        assert phrase in plan


def test_plan_preserves_api_spine_and_protected_boundaries() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "graphql remains read-only",
        "explicit actor and practice scope",
        "idempotency identity",
        "atomic receipt/effect/audit",
        "default denial",
        "forced rls",
        "preserves `docs/branding/`",
        "`git add .`",
    ):
        assert phrase in plan
    assert "grants no product or ordinary-practice authority" in threat


def test_parallelism_and_clockwork_are_explicit() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.lower().split())
    assert "**DeepSeek native Harness:** `planned`" in plan
    assert "**Gemini:** `reserved`" in plan
    assert "**Native subagents:** `declined`" in plan
    assert "one clockwork checkpoint `--check`" in normalized
    assert "a separate `--publish`" in normalized
    assert "a second distinct clockwork checkpoint `--check`" in normalized


def test_attempt_005_envelope_schema_is_closed_and_non_retriable() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    properties = schema["properties"]
    assert properties["attempt_id"] == {"const": "attempt-005"}
    assert properties["occupied_execution_count"] == {"const": 1}
    assert properties["automatic_retry_count"] == {"const": 0}
    assert properties["ambiguous_success_released"] == {"const": False}
    assert properties["ordinary_admission_release_count"] == {"const": 0}
    assert properties["product_record_count"] == {"const": 0}
