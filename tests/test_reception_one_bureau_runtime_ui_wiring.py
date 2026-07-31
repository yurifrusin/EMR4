from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs" / "diary"
PLAN = ROOT / "docs" / "bernie-reception-one-bureau-runtime-ui-wiring-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "bernie-reception-one-bureau-runtime-ui-wiring-threat-model-delta.md"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_plan_freezes_provider_free_development_and_proposal_only_boundary() -> None:
    plan = _read(PLAN)
    threat = _read(THREAT)

    for required in (
        "This tranche is provider-free.",
        "`deterministic`, selected by default",
        "`isolated_vertex`",
        "`requires_confirmation=true`",
        "`proposal_only=true`",
        "`write_performed=false`",
        "`confirmation_performed=false`",
        "`model_database_access=false`",
        "live_local_browser_backend_postgres",
    ):
        assert required in plan
    for closed in (
        "No Vertex call",
        "ADC read",
        "real or product-derived",
        "confirmation, write",
        "write",
        "production",
        "deployment",
        "release",
    ):
        assert closed in plan
    assert "prior provenance is removed" in threat
    assert "no confirmation or mutation affordance is added" in threat


def test_planner_control_is_explicit_compact_and_hidden_by_default() -> None:
    html = _read(DIARY / "diary.html")
    css = _read(DIARY / "meta-grid.css")

    assert (
        'id="meta-grid-planner-control" '
        'class="meta-grid-planner-control hidden"'
    ) in html
    assert (
        '<option value="deterministic" selected>Standard</option>'
    ) in html
    assert '<option value="isolated_vertex">Isolated model</option>' in html
    assert 'id="meta-grid-planner-provenance"' in html
    assert ".meta-grid-planner-control" in css
    assert ".meta-grid-planner-provenance" in css
    assert "@media (max-width: 700px)" in css


def test_projection_grows_for_result_heavy_views_then_scrolls_its_canvas() -> None:
    html = _read(DIARY / "diary.html")
    css = _read(DIARY / "meta-grid.css")

    assert 'href="meta-grid.css?v=11"' in html
    assert (
        '.meta-grid[data-family="availability_slots"] .meta-grid-shell'
        in css
    )
    assert "height: min(84vh, 760px);" in css
    canvas_rule = css[css.rindex(".meta-grid-canvas {") :]
    assert "min-height: 0;" in canvas_rule
    assert "overflow-y: auto;" in canvas_rule
    assert "overscroll-behavior: contain;" in canvas_rule
    assert "scrollbar-color: #78958f #eef1ed;" in canvas_rule
    assert "scrollbar-gutter: stable;" in canvas_rule
    assert ".meta-grid-canvas::-webkit-scrollbar-thumb" in canvas_rule


def test_ui_gate_defaults_to_deterministic_and_sends_only_closed_mode() -> None:
    source = _read(DIARY / "meta-grid.js")
    bridge = _read(DIARY / "diary.js")

    assert 'plannerMode: "deterministic"' in source
    assert 'params.get("smoke") === "true"' in source
    assert 'params.get("bureau_runtime_ui") === "true"' in source
    assert 'params.get("product_context_live_local") === "true"' in source
    assert 'state.plannerMode = "deterministic"' in source
    assert (
        'elements.plannerMode.value === "isolated_vertex"'
        in source
    )
    assert (
        "const requestedPlannerMode = state.plannerUiEnabled\n"
        "      ? state.plannerMode\n"
        '      : "deterministic"'
    ) in source
    assert "planner_mode: requestedPlannerMode" in source
    assert (
        'planner_mode: input.planner_mode === "isolated_vertex"'
        in bridge
    )
    assert "fetch(" not in source
    assert "XMLHttpRequest" not in source
    assert "new WebSocket" not in source


def test_provenance_projection_is_an_exact_allowlist_and_clears_on_failure() -> None:
    source = _read(DIARY / "meta-grid.js")
    start = source.index("const runtimeProvenance = {")
    end = source.index("const slots =", start)
    snippet = source[start:end]

    for allowed in (
        "planner_mode",
        "proofreader_disposition",
        "provider_calls",
        "runtime_audit_ref",
    ):
        assert allowed in snippet
    for forbidden in (
        "raw_prompt",
        "provider_response",
        "credential",
        "chain_of_thought",
        "reasoning",
        "unverified_draft",
        "service_account",
        "model_id",
    ):
        assert forbidden not in snippet
    assert "plannerProvenance = null" in source
    assert "elements.plannerProvenance.replaceChildren()" in source
    assert 'classList.toggle("hidden", !visible)' in source
    assert 'provenance.proofreader_disposition === "admit"' in source


def test_backend_gate_precedes_context_read_and_has_no_fallback() -> None:
    router = _read(ROOT / "app" / "routers" / "appointments.py")
    start = router.index("def compose_reception_one_product_context_proposal(")
    end = router.index('@router.post("/proposals/slot-search"', start)
    route = router[start:end]

    isolated_gate = route.index(
        'body.planner_mode == "isolated_vertex"'
    )
    context_read = route.index("build_product_context_frame(")
    assert isolated_gate < context_read
    assert "Isolated planner not admitted" in route
    isolated_branch = route[
        route.index("    else:\n", route.index('if body.planner_mode == "deterministic"'))
        : route.index("    adapter_review = (")
    ]
    assert "run_isolated_vertex_planner(" in isolated_branch
    assert "proofread_provider_blocked_plan(" not in isolated_branch
    assert "write" in route
    assert "never confirms or writes an appointment" in route


def test_continuity_and_compass_bind_accepted_provider_free_ui_result() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "reception-one-bureau-runtime-ui-wiring"
    )
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"]
        == "adopt-reception-one-word-native-diary-hybrid-direction"
    )
    assert not any(
        item["id"] == "reception-one-word-online-authenticated-dialog-check"
        for item in compass["decision_horizon"]
    )

    assert graph["graph_revision"] >= 155
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["map_revision"] >= 136
    assert node["status"] == "accepted"
    assert node["authority"]["authorized_openings"] == [
        {
            "boundary": "api-change",
            "scope": (
                "Provider-free development-only Bureau UI wiring over the "
                "accepted authored-synthetic proposal route; no confirmation, "
                "write or provider call."
            ),
            "source": (
                "docs/bernie-reception-one-bureau-runtime-ui-wiring-plan.md"
            ),
        }
    ]
    assert compass["current_position"]["node_id"] == (
        "raisa-word-online-authenticated-companion-verification"
    )
    assert "Satisfied on 2026-07-31" in decision["required_before"]
