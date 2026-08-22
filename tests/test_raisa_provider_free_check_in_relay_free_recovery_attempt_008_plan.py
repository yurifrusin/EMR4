from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-008-plan.md"
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-relay-free-recovery-attempt-008-"
    "threat-model-delta.md"
)
SCHEMA = ROOT / (
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-"
    "attempt-008/attempt-008-execution-envelope.schema.json"
)


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_plan_freezes_distinct_single_execution_and_full_git_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "Status: `frozen`" in plan
    assert "Timestamp: 2026-08-23T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    for source in (
        "2027c2252685c73772de6c60a0f5d11f82ab2c9d",
        "6657ee5061265d732096e9987f327d82feed800c",
        "5d93380060f31bab21bddc9ffdd5580754eb4fc6",
        "a33a4ccc7619fcae5cdd45a48a2312ab0c0384a4",
        "d01ef2f3afe16ccdb9a8f2077d5e76688397adb6",
        "bcdd7fc25f745ade62cb145ead73c4a1ad6f4e83",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
    ):
        assert source in plan
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "exactly one local provider-free disposable PostgreSQL 16 invocation" in normalized
    assert "There is no retry, resume or fallback" in normalized


def test_plan_freezes_every_p06_through_p14_condition() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    for number in range(6, 15):
        assert f"`P{number:02d}`" in plan
    assert "P12 through P14 as hard preexecution locks" in " ".join(plan.split())
    assert "No interpretation, partial satisfaction or later prose may weaken a row" in " ".join(plan.split())


def test_plan_binds_repaired_base_and_immutable_evidence() -> None:
    bindings = {
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py": "c4372d443206c2a39351667b6d599c6911d575059955e6c615358d379355ae78",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/rehearsal-failure-evidence.json": "86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/attempt-007-execution-envelope.json": "3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5",
    }
    plan = PLAN.read_text(encoding="utf-8")
    for path, expected in bindings.items():
        assert _sha256(path) == expected
        assert expected in plan
        assert f"`{path}`" in plan


def test_plan_freezes_provider_free_phase_and_checkpoint_order() -> None:
    plan_text = PLAN.read_text(encoding="utf-8")
    plan = " ".join(plan_text.lower().split())
    for phrase in (
        "no caller output path",
        "restores them unconditionally in `finally`",
        "construction creates no docker or database resource",
        "ordinary or serial pytest is forbidden",
        "after the candidate is committed and tracked-clean",
        "a separate `--publish`",
        "no automatic or manual retry",
        "one sol controller owns acquisition and cleanup",
    ):
        assert phrase in plan


def test_plan_preserves_api_parallelism_and_protected_boundaries() -> None:
    plan_text = PLAN.read_text(encoding="utf-8")
    plan = " ".join(plan_text.lower().split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").lower().split())
    for phrase in (
        "graphql remains read-only",
        "explicit actor/practice scope",
        "idempotency identity",
        "atomic effect/receipt/audit",
        "forced rls",
        "preserves `docs/branding/`",
        "`git add .`",
    ):
        assert phrase in plan
    assert "**DeepSeek native Harness:** `declined`" in plan_text
    assert "**Gemini:** `declined`" in plan_text
    assert "**Native subagents:** `declined`" in plan_text
    assert "neither result grants provider, product, ordinary-practice" in threat


def test_attempt_008_envelope_schema_is_closed_and_non_retriable() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    properties = schema["properties"]
    assert properties["attempt_id"] == {"const": "attempt-008"}
    assert properties["occupied_execution_count"] == {"const": 1}
    assert properties["automatic_retry_count"] == {"const": 0}
    assert properties["resume_count"] == {"const": 0}
    assert properties["fallback_count"] == {"const": 0}
    assert properties["ambiguous_success_released"] == {"const": False}
    assert properties["ordinary_admission_release_count"] == {"const": 0}
    assert properties["product_record_count"] == {"const": 0}
