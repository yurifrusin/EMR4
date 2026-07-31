import json
import re
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_TASKPANE = ROOT / "EMR4 Sidebar" / "src" / "taskpane"
PUBLISHED_TASKPANE = ROOT / "docs" / "taskpane"
DIARY = ROOT / "docs" / "diary"
SCHEMA = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-hybrid-contextual-launch"
    / "word-launch-context.schema.json"
)
PLAN = ROOT / "docs" / "bernie-reception-one-word-hybrid-contextual-launch-plan.md"
THREAT_MODEL = (
    ROOT
    / "docs"
    / "security"
    / "bernie-reception-one-word-hybrid-contextual-launch-threat-model-delta.md"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
RENDERED_COMPASS = ROOT / "docs" / "ariadne-compass-current.md"
CLOSEOUT = ROOT / "docs" / "bernie-reception-one-word-hybrid-contextual-launch-closeout.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _valid_context() -> dict:
    return {
        "contract_version": "reception.one.word-launch-context.v1",
        "type": "reception_one_launch_context",
        "source_surface": "word_taskpane",
        "target_surface": "native_diary_bureau",
        "reference_date": "2026-07-31",
        "correlation_id": "word-launch-3f9c2e4a-70af-4d91-8fab-95170b8be8d3",
        "open_projection": True,
        "planner_mode": "deterministic",
        "patient_context_authority": False,
        "command_authority": False,
        "provider_authority": False,
        "evidence_mode": "local_development_context_frame",
    }


def test_launch_context_schema_is_closed_and_accepts_only_bounded_navigation():
    schema = json.loads(_read(SCHEMA))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )
    validator.validate(_valid_context())

    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == set(_valid_context())
    for authority_field in (
        "patient_context_authority",
        "command_authority",
        "provider_authority",
    ):
        assert schema["properties"][authority_field]["const"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("patient_id", "patient-1"),
        ("patient_name", "Synthetic Person"),
        ("appointment_id", "appointment-1"),
        ("request_text", "Move the appointment"),
        ("token", "not-a-real-token"),
        ("command_payload", {}),
    ],
)
def test_launch_context_rejects_sensitive_or_authoritative_extra_fields(field, value):
    schema = json.loads(_read(SCHEMA))
    payload = _valid_context()
    payload[field] = value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    "reference_date",
    ["31-07-2026", "2026-7-31", "2026-02-30", "tomorrow", "", None],
)
def test_launch_context_rejects_malformed_date_shapes(reference_date):
    schema = json.loads(_read(SCHEMA))
    payload = _valid_context()
    payload["reference_date"] = reference_date

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            schema,
            format_checker=jsonschema.FormatChecker(),
        ).validate(payload)


def test_taskpane_exposes_distinct_ordinary_diary_and_reception_one_actions():
    html = _read(SOURCE_TASKPANE / "taskpane.html")
    source = _read(SOURCE_TASKPANE / "taskpane.js")

    assert 'id="btn-diary"' in html
    assert 'title="Open Diary"' in html
    assert 'id="btn-reception-one"' in html
    assert "Open in Diary" in html
    assert 'document.getElementById("btn-diary").onclick = () => openDiary();' in source
    assert 'document.getElementById("btn-reception-one").onclick = openReceptionOne;' in source


def test_taskpane_keeps_launch_context_out_of_url_and_separate_from_authentication():
    source = _read(SOURCE_TASKPANE / "taskpane.js")

    assert "const DIARY_URL = resolveDiaryUrl(window.location);" in source
    assert "displayDialogAsync(DIARY_URL" in source
    assert "JSON.stringify({ type: \"auth\", token })" in source
    assert "JSON.stringify(launchContext)" in source
    assert "?patient" not in source[source.index("function openReceptionOne()") : source.index("// COMMAND CENTRE")]
    assert "?appointment" not in source[source.index("function openReceptionOne()") : source.index("// COMMAND CENTRE")]
    assert "?request" not in source[source.index("function openReceptionOne()") : source.index("// COMMAND CENTRE")]


def test_taskpane_launch_contract_has_exact_zero_authority_shape():
    source = _read(SOURCE_TASKPANE / "taskpane.js")
    schema = json.loads(_read(SCHEMA))
    function_body = source[
        source.index("function createReceptionOneLaunchContext")
        : source.index("// Office displayDialogAsync error codes")
    ]

    for key in schema["required"]:
        assert re.search(rf"\b{re.escape(key)}\s*:", function_body)
    for prohibited in (
        "patient_id",
        "patient_name",
        "appointment_id",
        "request_text",
        "token",
        "command_payload",
    ):
        assert prohibited not in function_body
    assert 'planner_mode: "deterministic"' in function_body
    assert "patient_context_authority: false" in function_body
    assert "command_authority: false" in function_body
    assert "provider_authority: false" in function_body


def test_native_diary_revalidates_and_date_verifies_before_opening_projection():
    diary_source = _read(DIARY / "diary.js")
    meta_grid_source = _read(DIARY / "meta-grid.js")

    assert "validateReceptionOneWordLaunchContext(msg)" in diary_source
    assert "RECEPTION_ONE_WORD_LAUNCH_CONTEXT_KEYS" in diary_source
    assert 'new CustomEvent("emr4:reception-one-launch-context"' in diary_source
    handler = meta_grid_source[
        meta_grid_source.index("async function applyWordLaunchContext")
        : meta_grid_source.index("function init()")
    ]
    assert handler.index("bridge.navigateDiaryDate(context.reference_date)") < handler.index(
        "await openMetaGrid()"
    )
    assert "if (!navigation?.verified)" in handler
    assert 'context?.planner_mode !== "deterministic"' in handler


def test_request_input_has_bounded_autogrow_and_non_clipping_line_metrics():
    css = _read(DIARY / "meta-grid.css")
    source = _read(DIARY / "meta-grid.js")

    input_rules = re.findall(r"#meta-grid-request\s*\{([^}]+)\}", css)
    bounded_rule = next(rule for rule in input_rules if "line-height: 1.35;" in rule)
    assert "height: 52px;" in bounded_rule
    assert "min-height: 52px;" in bounded_rule
    assert "padding: 8px 12px;" in bounded_rule
    assert "overflow-y: hidden;" in bounded_rule
    assert "REQUEST_INPUT_MIN_HEIGHT_PX = 52" in source
    assert "REQUEST_INPUT_MAX_HEIGHT_PX = 96" in source
    assert 'elements.request.addEventListener("input", resizeRequestInput);' in source
    assert "elements.request.scrollHeight" in source


def test_source_and_published_taskpane_launch_surfaces_are_synchronised():
    assert _read(SOURCE_TASKPANE / "taskpane.html") == _read(
        PUBLISHED_TASKPANE / "taskpane.html"
    )
    assert _read(SOURCE_TASKPANE / "taskpane.css") == _read(
        PUBLISHED_TASKPANE / "taskpane.css"
    )

    source_js = _read(SOURCE_TASKPANE / "taskpane.js")
    published_js = _read(PUBLISHED_TASKPANE / "taskpane.js")
    start = source_js.index("function resolveDiaryUrl")
    end = source_js.index("// COMMAND CENTRE")
    published_start = published_js.index("function resolveDiaryUrl")
    published_end = published_js.index("// COMMAND CENTRE")
    assert source_js[start:end] == published_js[published_start:published_end]


def test_plan_and_threat_model_keep_command_provider_and_real_data_gates_closed():
    plan = _read(PLAN)
    threat_model = _read(THREAT_MODEL)
    combined = f"{plan}\n{threat_model}".lower()

    for phrase in (
        "no live provider call",
        "no new backend, provider or command authority",
        "no url-carried phi",
        "patient identifier",
        "provider authority",
        "appointment command",
    ):
        assert phrase in combined
    assert "protected holdout fixture path" in combined


def test_continuity_and_compass_bind_the_accepted_hybrid_descendant():
    graph = json.loads(_read(GRAPH))
    compass = json.loads(_read(COMPASS))
    node_id = "reception-one-word-hybrid-contextual-launch"
    node = next(node for node in graph["nodes"] if node["id"] == node_id)

    assert node["status"] == "accepted"
    assert any(
        relationship["node_id"]
        == "reception-one-bureau-post-admission-runtime-hardening"
        and relationship["relation"] == "builds_on"
        for relationship in node["relationships"]
    )
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == node_id for item in compass["journey"])
    assert compass["current_position"]["node_id"] == compass["journey"][-1]["node_id"]
    assert node_id in _read(RENDERED_COMPASS)
    assert "reception_one_word_hybrid_contextual_launch_pass" in _read(CLOSEOUT)
