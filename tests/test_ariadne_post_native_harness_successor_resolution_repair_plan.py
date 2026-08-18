from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/ariadne-post-native-harness-successor-resolution-repair-plan.md"
THREAT = (
    ROOT
    / "docs/security/ariadne-post-native-harness-successor-resolution-repair-threat-model-delta.md"
)
BATON = ROOT / "AGENTS.md"


def test_plan_freezes_exact_accepted_route_and_read_only_successor() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    assert "5fab227e7a0bf1d308d1373858f490419fee660e" in text
    assert "c82c3a741053a9c8da260aa62e1a968af22bb54e" in text
    assert (
        "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
        "admission-readiness-review"
    ) in text
    assert "may not enable a practice" in text


def test_plan_keeps_product_and_protected_surfaces_closed() -> None:
    text = (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).lower()
    for phrase in (
        "no product source or behavior",
        "no-product-code",
        "no-product-data",
        "no-live-route",
        "generic-status",
        "first-party client",
        "waiting-area movement",
        "protected-ref",
        "docs/branding/",
        "explicit-path staging only",
    ):
        assert phrase in text


def test_live_next_tranche_does_not_intersect_accepted_plan_names() -> None:
    baton = BATON.read_text(encoding="utf-8")
    next_row = next(
        line for line in baton.splitlines() if line.startswith("| Next implementation |")
    )
    accepted_plan_names = set(re.findall(r"`docs/([a-z0-9-]+)-plan\\.md`", baton))
    next_names = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", next_row))
    assert next_names
    assert accepted_plan_names.isdisjoint(next_names)
    assert (
        "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
        "admission-readiness-review"
    ) in next_names
