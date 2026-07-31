"""Focused guards for the integrated provider-free Reception One Bureau."""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from scripts import reception_one_integrated_bureau_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "bernie-reception-one-integrated-bureau-plan.md"
DIARY = ROOT / "docs" / "diary"
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
ARTIFACTS = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-integrated-bureau"
)
BROWSER_ARTIFACTS = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-integrated-bureau"
)


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _node(graph: dict, node_id: str) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == node_id]
    assert len(matches) == 1
    return matches[0]


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden_depth = 0
        self.values: list[str] = []

    def handle_starttag(self, tag: str, _attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden_depth = max(0, self.hidden_depth - 1)

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth and data.strip():
            self.values.append(data.strip())


def _visible_text(html: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(html)
    return " ".join(parser.values)


def test_plan_freezes_provider_free_product_and_zero_call_lane() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for required in (
        "provider-free integrated Bureau baseline",
        "move the underlying Diary to a requested different day before opening the",
        "content-sized modeless in-application foreground",
        "reversible horizontal expansion into the wider Bureau console",
        "`Understanding your request`",
        "`Checking the Diary`",
        "`Preparing the view`",
        "`I need one detail`",
        "`execution_enabled: false`",
        "`provider_call_count: 0`",
        "An occupied provider call is outside this plan.",
    ):
        assert required in text


def test_continuity_and_compass_bind_the_new_descendant_without_history_rewrite() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = _node(graph, "reception-one-integrated-bureau")
    historical = _node(graph, "reception-one-yuri-internal-walkthrough-result")

    assert graph["graph_revision"] >= 60
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["map_revision"] >= 47
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "reception-one-yuri-internal-walkthrough-result",
            "relation": "builds_on",
        }
    ]
    assert historical["status"] == "accepted"
    assert historical["created_at"] == "2026-07-28T23:52:20Z"


def test_reference_date_and_date_first_bridge_fail_closed() -> None:
    source = (DIARY / "diary.js").read_text(encoding="utf-8")
    css = (DIARY / "meta-grid.css").read_text(encoding="utf-8")

    for required in (
        "function initialDiaryDate()",
        'urlParams.get("reference_date")',
        "async function navigateDiaryForProjection(targetDateKey)",
        'window.dispatchEvent(new CustomEvent("emr4:diary-page-settled"',
        "navigateDiaryDate: navigateDiaryForProjection",
        "const verified = readVerified && localDateKey(diaryDate) === targetDateKey",
    ):
        assert required in source
    for required in (
        ".diary-page-turn-forward",
        ".diary-page-turn-backward",
        "@keyframes diary-page-turn-forward",
        "@keyframes diary-page-turn-backward",
        "@media (prefers-reduced-motion: reduce)",
        "animation: diary-page-dissolve 1ms linear",
    ):
        assert required in css


def test_modeless_bureau_has_plain_return_and_conversational_copy() -> None:
    html = (DIARY / "diary.html").read_text(encoding="utf-8")
    source = (DIARY / "meta-grid.js").read_text(encoding="utf-8")
    css = (DIARY / "meta-grid.css").read_text(encoding="utf-8")
    visible_html = _visible_text(html).casefold()

    for required in (
        'role="dialog"',
        'aria-modal="false"',
        'id="meta-grid-return"',
        'id="meta-grid-close"',
        'id="meta-grid-expand"',
        "Return to Diary",
        "Synthetic demo",
    ):
        assert required in html
    for required in (
        "Understanding your request",
        "Checking the Diary",
        "Preparing the view",
        "I need one detail",
        "focusCanvasWithoutWindowScroll",
        "elements.shell.scrollTop = 0",
        "toggleExpandedBureau",
        "The Bureau console is expanded",
        "Reception One cannot confirm this appointment",
        "meta-grid-appointment-date",
        "meta-grid-appointment-details",
        "meta-grid-appointment-status",
        "Proposal only — nothing booked",
    ):
        assert required in source
    assert "grid" not in visible_html
    assert "body.meta-grid-open #diary-grid-container" in css
    assert "display: block !important" in css
    assert "pointer-events: none" in css
    assert "pointer-events: auto" in css
    assert ".meta-grid.is-expanded .meta-grid-shell" in css
    assert ".meta-grid.is-expanded .meta-grid-rail" in css
    assert ".meta-grid-appointment-card" in css
    assert "grid-template-columns: 76px minmax(0, 1fr) 110px" in css
    assert "justify-content: end" in css
    assert "text-align: right" in css
    assert ".meta-grid-request-actions .meta-grid-primary" in css
    assert "background: #c6431c" in css


def test_smoke_mode_opens_no_eligibility_network_probe() -> None:
    source = (DIARY / "diary.js").read_text(encoding="utf-8")
    function = source[
        source.index("async function checkBerniePilotEligibility()") :
        source.index("function renderBernieInstructionInput")
    ]
    smoke_return = function.index("if (isSmoke) {")
    provider_probe = function.index('apiFetch("/appointments/bernie/pilot-eligibility")')
    assert "setMetaGridLaunchAvailability(true);\n    return;" in function
    assert smoke_return < provider_probe


def test_preview_link_opens_the_reference_appointment_sheet_directly() -> None:
    source = (DIARY / "meta-grid.js").read_text(encoding="utf-8")

    assert 'params.get("reception_one_demo") === "appointment_sheet"' in source
    assert "await submitRequest(\"Show Margaret Thompson's upcoming appointments\")" in source
    assert source.index("await openMetaGrid()") < source.index(
        'params.get("reception_one_demo") === "appointment_sheet"'
    )


def test_provider_blocked_contracts_admit_only_grounded_fresh_read_intent() -> None:
    evidence = contracts.build_evidence()
    persisted = _json(ARTIFACTS / "provider-blocked-evidence.json")
    policy = _json(ARTIFACTS / "provider-blocked-policy.json")

    assert evidence == persisted
    assert evidence["status"] == "pass"
    assert evidence["positive_case"]["decision"] == "admit"
    assert evidence["positive_case"]["safe_repairs"] == []
    assert len(evidence["negative_cases"]) == 5
    assert all(case["decision"] == "reject" for case in evidence["negative_cases"])
    assert evidence["provider_boundary"] == {
        "credentials_requested": False,
        "execution_enabled": False,
        "network_requested": False,
        "product_delivery_enabled": False,
        "provider_call_count": 0,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
    }
    contracts.verify_policy(policy)


def test_proofreader_allows_mechanical_repair_but_not_semantic_repair() -> None:
    case = _json(ARTIFACTS / "authored-synthetic-case.json")
    mechanical = copy.deepcopy(case["draft"])
    mechanical["family"] = " FOCUSED_SCHEDULE_LANE "
    mechanical["source_evidence_paths"] = list(
        reversed(mechanical["source_evidence_paths"])
    )
    result, normalized = contracts.proofread(
        case["input"],
        mechanical,
        now=datetime(2026, 7, 28, tzinfo=timezone.utc),
    )
    assert result["decision"] == "admit"
    assert result["safe_repairs"] == [
        "canonical_enum_casing",
        "deterministic_ordering",
        "trim_whitespace",
    ]
    assert normalized["family"] == "focused_schedule_lane"

    semantic = copy.deepcopy(case["draft"])
    semantic["target_date"] = "2026-07-29"
    result, _ = contracts.proofread(
        case["input"],
        semantic,
        now=datetime(2026, 7, 28, tzinfo=timezone.utc),
    )
    assert result["decision"] == "reject"
    assert "ungrounded-date" in result["reason_codes"]


def test_verifier_has_no_provider_credential_or_network_runtime() -> None:
    source = (
        ROOT / "scripts" / "reception_one_integrated_bureau_contracts.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "google.auth",
        "google.cloud",
        "requests.",
        "urllib.request",
        "socket.",
        "subprocess.",
        "os.environ",
        "access_token",
    ):
        assert forbidden not in source


def test_browser_evidence_is_responsive_modeless_and_provider_free() -> None:
    evidence = _json(BROWSER_ARTIFACTS / "browser-acceptance-evidence.json")

    assert evidence["result"] == "browser_pass"
    assert evidence["reference_date"] == "2026-07-27"
    assert evidence["target_date"] == "2026-07-28"
    assert evidence["network"]["provider_hosts_observed"] == []
    assert evidence["console_warnings_or_errors"] == []
    assert evidence["page_errors"] == []
    assert {item["id"] for item in evidence["viewports"]} == {
        "desktop",
        "tablet",
        "phone",
    }
    for item in evidence["viewports"]:
        assert item["aria_modal"] == "false"
        assert item["diary_visible"] is True
        assert item["visible_bureau_copy_contains_grid"] is False
        assert item["horizontal_overflow_px"] == 0
        assert item["shell_scroll_top"] == 0
        assert item["close_control"]["width"] >= 44
        assert item["close_control"]["height"] >= 44
        assert item["return_control"]["width"] >= 44
        assert item["return_control"]["height"] >= 44
    assert evidence["date_first_flow"]["date_set_before_projection"] is True
    assert evidence["date_first_flow"]["focus_after_return"] == "btn-meta-grid-launch"
    assert evidence["date_first_flow"]["focus_after_escape"] == "btn-meta-grid-launch"
    assert evidence["expanded_bureau_flow"]["expanded"]["rail_visible"] is True
    assert evidence["expanded_bureau_flow"]["expanded"]["diary_visible"] is True
    assert (
        evidence["expanded_bureau_flow"]["expanded"]["shell_width"]
        > evidence["expanded_bureau_flow"]["collapsed"]["shell_width"]
    )
    assert evidence["expanded_bureau_flow"]["collapsed"]["rail_visible"] is False
    assert len(evidence["screenshots"]) == 4
    for item in evidence["screenshots"]:
        assert (BROWSER_ARTIFACTS / item["file"]).is_file()


def test_generated_concept_is_fictional_design_reference_only() -> None:
    concept = BROWSER_ARTIFACTS / "reception-one-integrated-bureau-desktop-concept.png"
    payload = concept.read_bytes()
    assert payload[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(payload) > 100_000
