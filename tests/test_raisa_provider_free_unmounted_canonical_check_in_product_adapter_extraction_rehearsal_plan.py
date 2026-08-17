from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal-threat-model-delta.md"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_freezes_exact_result_source_and_timestamp() -> None:
    plan = _text(PLAN)

    assert "Date: 2026-08-18" in plan
    assert "Timestamp: 2026-08-18T08:58:42+10:00 (Australia/Brisbane)" in plan
    assert "Status: `frozen`" in plan
    assert "852f6f26089cf081c205aff952dffcdecb80d63b" in plan
    assert (
        "raisa_provider_free_unmounted_canonical_check_in_product_adapter_"
        "extraction_rehearsal_pass"
    ) in plan


def test_plan_binds_inputs_owned_package_and_route_immutability() -> None:
    plan = _text(PLAN)

    for token in (
        "87a67fd718ac9233f6b1e089d708969749afda0124713e8621d542939f5d605f",
        "c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410",
        "7a2caaa1fc862821cc9f8a666e945ddb5e5e837825978bcdcb5f7445cd7a219f",
        "app/services/appointment_check_in_product_adapter.py",
        "tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py",
        "must not edit or import the adapter from",
        "at least 60 hostile contract mutations",
    ):
        assert token in plan


def test_plan_freezes_authority_idempotency_area_effect_and_api_spine() -> None:
    plan = _text(PLAN)

    for token in (
        "Authenticated current human authority",
        "Stable idempotency and one-use evidence",
        "Locked current truth",
        "Opaque evidence verification",
        "Waiting-area policy",
        "Ordered atomic effect composition",
        "Patient-free release",
        "GraphQL remains read-only",
        "event is a committed acceleration hint",
    ):
        assert token in plan


def test_parallelism_and_closed_surfaces_are_explicit() -> None:
    plan = _text(PLAN)
    threat = _text(THREAT)

    assert "DeepSeek V4 Flash/high" in plan
    assert "Gemini 3.7 Flash/high" in plan
    assert "Native subagents" in plan
    assert "injected authored-synthetic fakes only" in threat
    assert "later atomic convergence" in threat
    assert "No product data" in threat


def test_live_latch_names_the_exact_in_progress_successor() -> None:
    latch = json.loads(_text(LATCH))

    assert latch["operation_id"] == (
        "raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
        "extraction-rehearsal"
    )
    assert latch["status"] == "in_progress"
    assert len(latch["source_head"]) == 40
    assert all(char in "0123456789abcdef" for char in latch["source_head"])
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is False
