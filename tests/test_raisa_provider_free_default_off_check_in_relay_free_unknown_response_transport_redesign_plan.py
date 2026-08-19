from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign-threat-model-delta.md"
DESIGN = ROOT / "docs/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign.md"
CONTRACT = ROOT / "orchestration/continuity/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign/contract.json"


def test_plan_freezes_timestamp_full_git_and_no_database_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    compact_plan = " ".join(plan.split())
    threat = THREAT.read_text(encoding="utf-8")
    design = DESIGN.read_text(encoding="utf-8")
    assert "Date: 2026-08-19" in plan
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    assert "Timestamp: 2026-08-19T" in threat
    assert "44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4" in plan
    assert "44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4" in threat
    assert "44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4" in design
    assert not re.search(r"`[0-9a-f]{7}`", plan)
    assert "perform no fourth or successor PostgreSQL execution" in compact_plan
    assert "No PostgreSQL server, database connection, SQL" in design


def test_plan_and_contract_preserve_api_spine_and_closed_product_surfaces() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").lower().split())
    threat = THREAT.read_text(encoding="utf-8").lower()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for phrase in (
        "graphql remains read-only",
        "explicit practice scope",
        "idempotency identity",
        "audit atomicity",
        "default denial",
        "authoritative readback",
        "no ordinary-practice enablement",
        "protected-ref movement",
        "preserve `docs/branding/`",
        "stage explicit paths only",
    ):
        assert phrase in plan
    assert "no database execution" in threat
    assert all(value is False for value in contract["closed_boundaries"].values())


def test_plan_binds_all_three_immutable_predecessor_attempts_exactly() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected = {
        "001": "e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1",
        "002": "bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed",
        "003": "15cebad64c7bfbddb83878e75cf8f3a0d137a7834075e063c92aead8b603e219",
    }
    for attempt, digest in expected.items():
        assert digest in plan
        binding = next(
            row
            for row in contract["source_bindings"]
            if row["path"].endswith(
                f"rehearsal-failure-evidence-attempt-{attempt}.json"
            )
        )
        assert binding["sha256"] == digest


def test_worker_mix_is_explicit_and_serial() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "**DeepSeek:** declined" in plan
    assert "**Gemini:** reserved" in plan
    assert "**Native subagents:** declined" in plan
    assert "one mutable lifecycle are serial" in plan
