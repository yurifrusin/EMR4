import json
import re
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_TASKPANE = ROOT / "EMR4 Sidebar" / "src" / "taskpane"
PUBLISHED_TASKPANE = ROOT / "docs" / "taskpane"
DIARY = ROOT / "docs" / "diary"
CONTRACTS = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-compact-companion-shell"
)
REQUEST_SCHEMA = CONTRACTS / "word-companion-request.schema.json"
SUMMARY_SCHEMA = CONTRACTS / "word-companion-summary.schema.json"
PLAN = ROOT / "docs" / "bernie-reception-one-word-compact-companion-shell-plan.md"
THREAT_MODEL = (
    ROOT
    / "docs"
    / "security"
    / "bernie-reception-one-word-compact-companion-shell-threat-model-delta.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _request() -> dict:
    return {
        "contract_version": "reception.one.word-companion-request.v1",
        "type": "reception_one_companion_request",
        "source_surface": "word_taskpane",
        "target_surface": "native_diary_bureau",
        "correlation_id": (
            "word-launch-3f9c2e4a-70af-4d91-8fab-95170b8be8d3"
        ),
        "request_id": "word-request-680bf92c-450b-4b8d-8a7e-0e817ea323d4",
        "reference_date": "2026-07-31",
        "data_class": "authored_synthetic",
        "request_text": "Show Margaret Thompson's upcoming appointments",
        "planner_mode": "deterministic",
        "projection_intent": "view",
        "patient_context_authority": False,
        "appointment_context_authority": False,
        "appointment_write_authority": False,
        "command_authority": False,
        "provider_authority": False,
        "evidence_mode": "local_authored_synthetic_companion",
    }


def _summary(**changes) -> dict:
    value = {
        "contract_version": "reception.one.word-companion-summary.v1",
        "type": "reception_one_companion_summary",
        "source_surface": "native_diary_bureau",
        "target_surface": "word_taskpane",
        "correlation_id": _request()["correlation_id"],
        "request_id": _request()["request_id"],
        "reference_date": "2026-07-31",
        "status": "admitted",
        "projection_family": "patient_timeline",
        "result_count": 2,
        "planner_mode": "deterministic",
        "proofreader_disposition": "admit",
        "summary_code": "results_ready",
        "details_surface": "native_diary_bureau",
        "detail_fields_released": False,
        "request_text_included": False,
        "patient_context_included": False,
        "appointment_context_included": False,
        "appointment_write_authority": False,
        "command_authority": False,
        "provider_authority": False,
        "evidence_mode": "local_authored_synthetic_companion",
    }
    value.update(changes)
    return value


def _validator(path: Path) -> jsonschema.Draft202012Validator:
    schema = json.loads(_read(path))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )


def test_request_and_summary_schemas_are_closed_and_accept_valid_examples():
    request_schema = json.loads(_read(REQUEST_SCHEMA))
    summary_schema = json.loads(_read(SUMMARY_SCHEMA))

    _validator(REQUEST_SCHEMA).validate(_request())
    _validator(SUMMARY_SCHEMA).validate(_summary())

    assert request_schema["additionalProperties"] is False
    assert summary_schema["additionalProperties"] is False
    assert set(request_schema["required"]) == set(_request())
    assert set(summary_schema["required"]) == set(_summary())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("patient_id", "synthetic-patient-1"),
        ("appointment_id", "synthetic-appointment-1"),
        ("token", "not-a-token"),
        ("provider", "unapproved"),
        ("command_payload", {}),
    ],
)
def test_request_rejects_unknown_sensitive_or_authoritative_fields(field, value):
    payload = _request()
    payload[field] = value
    with pytest.raises(jsonschema.ValidationError):
        _validator(REQUEST_SCHEMA).validate(payload)


@pytest.mark.parametrize(
    ("changes", "expected_valid"),
    [
        ({"result_count": 0, "summary_code": "no_results"}, True),
        (
            {
                "status": "clarification_required",
                "projection_family": "clarification",
                "result_count": 0,
                "proofreader_disposition": "human_gate",
                "summary_code": "clarification_required",
            },
            True,
        ),
        (
            {
                "status": "blocked",
                "projection_family": "clarification",
                "result_count": 0,
                "proofreader_disposition": "edge_abort",
                "summary_code": "request_blocked",
            },
            True,
        ),
        ({"result_count": 2, "summary_code": "no_results"}, False),
        ({"proofreader_disposition": "human_gate"}, False),
        ({"patient_context_included": True}, False),
        ({"request_text": "sensitive draft"}, False),
    ],
)
def test_summary_cross_field_contract_fails_closed(changes, expected_valid):
    payload = _summary(**changes)
    if expected_valid:
        _validator(SUMMARY_SCHEMA).validate(payload)
    else:
        with pytest.raises(jsonschema.ValidationError):
            _validator(SUMMARY_SCHEMA).validate(payload)


def test_taskpane_shell_is_default_off_loopback_only_and_visually_bounded():
    html = _read(SOURCE_TASKPANE / "taskpane.html")
    css = _read(SOURCE_TASKPANE / "taskpane.css")
    source = _read(SOURCE_TASKPANE / "taskpane.js")

    assert 'id="reception-one-companion"' in html
    assert 'class="reception-one-companion hidden"' in html
    assert 'id="reception-one-companion-request"' in html
    assert 'maxlength="280"' in html
    assert 'id="btn-reception-one-prepare"' in html
    assert "Development preview &middot; synthetic names only" in html
    assert ".reception-one-companion-footer" in css
    assert "@media (max-width: 330px)" in css
    assert "isReceptionOneCompanionDemoEnabled" in source
    companion_gate = source[
        source.index("function isReceptionOneCompanionDemoEnabled()"):
        source.index("function isClinicianOneDocumentContextDemoEnabled()")
    ]
    assert "(localHost || isHostedSyntheticOnlyModeEnabled())" in companion_gate
    assert 'get("reception_one_companion_demo") === "true"' in source
    assert '["127.0.0.1", "localhost", "[::1]"]' in source


def test_taskpane_keeps_auth_launch_request_and_summary_distinct():
    source = _read(SOURCE_TASKPANE / "taskpane.js")
    dialog_section = source[
        source.index("function _setupDiaryDialog")
        : source.index("// COMMAND CENTRE")
    ]

    auth = 'messageChild(JSON.stringify({ type: "auth", token }))'
    launch = "messageChild(JSON.stringify(launchContext))"
    request = "messageChild(JSON.stringify(companionRequest))"
    assert dialog_section.index(auth) < dialog_section.index(launch)
    assert dialog_section.index(launch) < dialog_section.index(request)
    assert "validateReceptionOneCompanionSummary" in dialog_section
    assert "renderReceptionOneCompanionSummary(summary)" in dialog_section


def test_request_constructor_does_not_read_word_patient_or_document_context():
    source = _read(SOURCE_TASKPANE / "taskpane.js")
    constructor = source[
        source.index("function createReceptionOneCompanionRequest")
        : source.index("function diaryDialogUrl")
    ]

    for prohibited in (
        "currentPatient",
        "patient_id",
        "appointment_id",
        "document",
        "token",
        "provider:",
    ):
        assert prohibited not in constructor
    for false_authority in (
        "patient_context_authority",
        "appointment_context_authority",
        "appointment_write_authority",
        "command_authority",
        "provider_authority",
    ):
        assert re.search(rf"{false_authority}: false", constructor)


def test_dialog_url_carries_only_the_local_capability_not_request_or_context():
    source = _read(SOURCE_TASKPANE / "taskpane.js")
    resolver = source[
        source.index("function diaryDialogUrl")
        : source.index("function companionStatus")
    ]

    assert 'url.searchParams.set("reception_one_companion_demo", "true")' in resolver
    assert 'url.searchParams.set("smoke", "true")' in resolver
    for prohibited in (
        "request_text",
        "correlation_id",
        "request_id",
        "patient",
        "appointment",
        "token",
    ):
        assert prohibited not in resolver


def test_diary_revalidates_default_off_request_before_dispatch():
    diary = _read(DIARY / "diary.js")
    handler = diary[
        diary.index('} else if (msg.type === "reception_one_companion_request")')
        : diary.index('} else if (msg.type === "focus")')
    ]

    assert "validateReceptionOneWordCompanionRequest" in diary
    assert "RECEPTION_ONE_WORD_COMPANION_REQUEST_KEYS" in diary
    assert 'isLocalHarnessCapabilityEnabled(' in handler
    assert '"reception_one_companion_demo"' in handler
    assert "validateReceptionOneWordCompanionRequest(msg)" in handler
    assert 'new CustomEvent("emr4:reception-one-companion-request"' in handler


def test_native_request_waits_for_verified_launch_then_returns_only_summary():
    source = _read(DIARY / "meta-grid.js")
    handler = source[
        source.index("async function applyWordCompanionRequest")
        : source.index("function init()")
    ]

    assert handler.index(
        "const launchApplied = await applyWordLaunchContext(launchContext)"
    ) < handler.index("await submitRequest(request.request_text)")
    assert handler.index(
        "await submitRequest(request.request_text)"
    ) < handler.index("buildWordCompanionSummary(request, projection)")
    assert "consumedWordCompanionRequestIds.has(request.request_id)" in handler
    assert "request.correlation_id !== launchContext.correlation_id" in handler
    assert "request.reference_date !== launchContext.reference_date" in handler


def test_native_summary_proofreader_requires_fresh_zero_command_projection():
    source = _read(DIARY / "meta-grid.js")
    proofreader = source[
        source.index("function buildWordCompanionSummary")
        : source.index("function sendWordCompanionSummary")
    ]

    assert "projection.freshness?.stale !== false" in proofreader
    assert (
        "projection.action_boundary?.appointment_write_authority !== false"
        in proofreader
    )
    assert (
        "projection.action_boundary?.operational_command_available !== false"
        in proofreader
    )
    assert 'proofreader_disposition: "admit"' in proofreader
    assert 'proofreader_disposition: "human_gate"' in proofreader
    assert 'proofreader_disposition: "edge_abort"' in proofreader
    assert "request_text" not in _summary()


def test_word_generates_visible_copy_from_code_not_returned_free_text():
    source = _read(SOURCE_TASKPANE / "taskpane.js")
    renderer = source[
        source.index("function renderReceptionOneCompanionSummary")
        : source.index("function prepareReceptionOneFromWord")
    ]

    assert "summary.summary_code" in renderer
    assert "summary.result_count" in renderer
    assert "summary.request_text" not in renderer
    assert "summary.patient" not in renderer
    assert "summary.appointment" not in renderer


def test_source_and_published_taskpane_are_synchronised():
    for name in ("taskpane.html", "taskpane.css", "taskpane.js"):
        assert _read(SOURCE_TASKPANE / name) == _read(PUBLISHED_TASKPANE / name)


def test_plan_and_threat_model_preserve_api_spine_and_protected_boundaries():
    combined = f"{_read(PLAN)}\n{_read(THREAT_MODEL)}".lower()
    for phrase in (
        "no live provider call",
        "no url-carried phi",
        "patient identifier",
        "appointment command",
        "provider authority",
        "protected holdout fixture paths",
        "zero database reads or writes",
        "route_intercepted_browser",
    ):
        assert phrase in combined
