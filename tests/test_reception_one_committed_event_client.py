from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs" / "diary"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_bridge_adds_only_the_two_authorized_event_reads():
    source = _read(DIARY / "diary.js")
    bridge = source[source.index("window.EMR4DiaryMetaGridBridge") :]

    assert "readAppointment: metaGridReadAppointment" in bridge
    assert "readCommittedEvents: metaGridReadCommittedEvents" in bridge
    assert "/diary/events/committed?${params.toString()}" in source
    assert "/appointments/${encodeURIComponent(normalized)}" in source
    assert "method: \"POST\"" not in source[
        source.index("async function metaGridReadCommittedEvents") :
        source.index("async function metaGridSearchPatients")
    ]


def test_consumer_requires_membership_revision_and_fresh_reads_before_notice():
    source = _read(DIARY / "meta-grid.js")
    consumer = source[
        source.index("async function consumeCommittedEvent") :
        source.index("function stopEventPolling")
    ]

    assert "projectionAppointment(current, aggregateId)" in consumer
    assert "event.aggregate_revision <= previousRevision" in consumer
    assert "await bridge.readAppointment(aggregateId)" in consumer
    assert "await freshProjectionForCommittedEvent(current)" in consumer
    assert "previousItem.starts_at === currentItem.starts_at" in consumer
    assert "state.eventRuntime.cue" in consumer
    assert "event.payload.start_time" not in consumer
    assert "event.payload.end_time" not in consumer


def test_attention_state_is_bounded_in_memory_user_controlled_and_nonmodal():
    source = _read(DIARY / "meta-grid.js")
    html = _read(DIARY / "diary.html")
    css = _read(DIARY / "meta-grid.css")

    for expected in (
        "EVENT_ATTENTION_LIMIT = 100",
        "EVENT_SNOOZE_MS = 5 * 60 * 1000",
        "deliveredEventIds: new Set()",
        "aggregateRevisions: new Map()",
        "snoozedUntil: 0",
        "muted: false",
        "document.hidden",
        "clearTimeout",
    ):
        assert expected in source
    for control in (
        'id="meta-grid-event-show"',
        'id="meta-grid-event-dismiss"',
        'id="meta-grid-event-snooze"',
        'id="meta-grid-event-mute"',
    ):
        assert control in html
    assert "aria-live=\"polite\"" in html
    cue_markup = html[
        html.index('id="meta-grid-event-cue"') : html.index('id="meta-grid-canvas"')
    ]
    assert "role=\"alertdialog\"" not in cue_markup
    assert "role=\"dialog\"" not in cue_markup
    assert ".meta-grid-event-cue" in css
    assert "min-height: 44px" in css


def test_event_consumer_opens_no_persistent_or_autonomous_runtime():
    source = _read(DIARY / "meta-grid.js")
    for forbidden in (
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "new WebSocket",
        "new EventSource",
        "serviceWorker",
        "SpeechRecognition",
        "webkitSpeechRecognition",
        "sendBeacon(",
        "fetch(",
        "/confirm",
        "page.route(",
    ):
        assert forbidden not in source
    assert "appointment_write_authority: false" in source


def test_privacy_keyboard_and_interruption_behavior_remain_explicit():
    source = _read(DIARY / "meta-grid.js")

    assert '"Time and appointment details are hidden while privacy mode is on."' in source
    assert "elements.eventShow.disabled = state.private" in source
    assert "if (dismissEventCue() || closeExplanation())" in source
    assert "row.focus({ preventScroll: true })" in source
    assert "stopEventPolling();\n        markInterrupted();" in source
    assert "startEventPolling();" in source
    assert "Patient" not in (
        source[source.index("elements.announcer.textContent = \"An appointment time") :]
        .split(";", 1)[0]
    )


def test_api_spine_declares_only_the_bounded_local_exception():
    async_contract = yaml.safe_load(
        _read(ROOT / "docs" / "api-spine" / "async" / "integration-events.yaml")
    )
    charter = yaml.safe_load(
        _read(ROOT / "docs" / "api-spine" / "manifests" / "agent-capability-charters.yaml")
    )
    openapi = yaml.safe_load(
        _read(ROOT / "docs" / "api-spine" / "openapi" / "diary-committed-events.yaml")
    )

    exception = async_contract["source_safety"]["bounded_local_runtime_exception"]
    assert exception["event_type"] == "diary.appointment_rescheduled"
    assert exception["feature_default"] == "disabled"
    assert exception["broader_runtime_wiring"] == "blocked"
    assert async_contract["blocked_gates"]["graph_ql_mutations"] == "blocked"

    bernie = next(row for row in charter["agents"] if row["agent_id"] == "bernie")
    assert bernie["bounded_runtime_authority"]["appointment_write_authority"] is False
    assert bernie["bounded_runtime_authority"]["enabled_by_default"] is False
    assert "treat_event_as_command_authority" in bernie["must_not"]

    path = openapi["paths"]["/diary/events/committed"]
    assert set(path) == {"get"}
    assert path["get"]["operationId"] == "readCommittedDiaryEvents"
    payload = openapi["components"]["schemas"]["AppointmentRescheduledPayload"]
    assert payload["additionalProperties"] is False
    assert not ({"patient_id", "patient_name", "reason", "notes"} & set(payload["properties"]))
