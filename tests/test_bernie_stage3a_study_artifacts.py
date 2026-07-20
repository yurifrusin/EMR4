"""Protected-safe deterministic checks for the Stage 3A Yuri study surface."""

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = ROOT / "docs" / "diary" / "stage3a"
HTML = STUDY_DIR / "index.html"
DATA_JS = STUDY_DIR / "stage3a-data.js"
CORE_JS = STUDY_DIR / "stage3a-core.js"
APP_JS = STUDY_DIR / "stage3a.js"
PLAN = ROOT / "docs" / "bernie-stage3a-yuri-formative-validation-plan.md"


def _node_json(source: str):
    result = subprocess.run(
        ["node", "-e", source],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return json.loads(result.stdout)


def test_stage3a_surface_is_explicitly_synthetic_mutation_free_and_yuri_only():
    html = HTML.read_text(encoding="utf-8")

    assert "Yuri-only formative study" in html
    assert "Nothing on this page writes to the Diary" in html
    assert "authored_synthetic_fixture_browser" in html
    assert "Typed, local and provider-disabled" in html
    assert "Not language-model evidence" in html


def test_stage3a_browser_code_has_no_runtime_provider_voice_or_persistence_surface():
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in (HTML, DATA_JS, CORE_JS, APP_JS)
    )
    forbidden_active_fragments = {
        "fetch(",
        "XMLHttpRequest",
        "new WebSocket",
        "new EventSource",
        "sendBeacon(",
        "localStorage",
        "sessionStorage",
        "navigator.mediaDevices",
        "SpeechRecognition",
        "webkitSpeechRecognition",
        "/api/v1/",
        "confirm-bernie",
    }

    hits = sorted(fragment for fragment in forbidden_active_fragments if fragment in source)
    assert not hits, f"Stage 3A fixture surface opened a forbidden runtime: {hits}"


def test_stage3a_fixture_contract_contains_exact_fourteen_scenarios():
    data = _node_json(
        "const d=require('./docs/diary/stage3a/stage3a-data.js');"
        "console.log(JSON.stringify({schema:d.schema_version,evidence:d.evidence_mode,"
        "ids:d.scenarios.map(x=>x.id),synthetic:d.patients.every(x=>x.synthetic===true)}));"
    )

    assert data == {
        "schema": "bernie.stage3a.study-fixtures.v1",
        "evidence": "authored_synthetic_fixture",
        "ids": [f"S3A-{index:02d}" for index in range(1, 15)],
        "synthetic": True,
    }


def test_stage3a_deterministic_interpreter_preserves_answer_proposal_and_block_states():
    results = _node_json(
        "const d=require('./docs/diary/stage3a/stage3a-data.js');"
        "const c=require('./docs/diary/stage3a/stage3a-core.js');"
        "const cases=["
        "['S3A-01',\"What time and date is Margaret Thompson's appointment in six months with Dr Shera?\"],"
        "['S3A-05','Prepare an appointment for Margaret Thompson with Dr Shera on Friday week after 2 pm.'],"
        "['S3A-07',\"Show me Margaret's upcoming appointments.\"],"
        "['S3A-08','Confirm the old appointment proposal again.'],"
        "['S3A-06','Confirm it.']];"
        "console.log(JSON.stringify(cases.map(x=>{const r=c.interpretTask(x[0],x[1],d);"
        "return {kind:r.kind,code:r.code,projection:r.projection?.id||null};})));"
    )

    assert results == [
        {
            "kind": "answer",
            "code": "appointment_found",
            "projection": "projection-margaret-six-months",
        },
        {
            "kind": "proposal",
            "code": "proposal_ready_no_write",
            "projection": "projection-proposal-margaret-shera",
        },
        {
            "kind": "clarification",
            "code": "patient_identity_ambiguous",
            "projection": None,
        },
        {"kind": "blocked", "code": "stale_context", "projection": None},
        {
            "kind": "boundary",
            "code": "authoritative_confirmation_separate",
            "projection": None,
        },
    ]


def test_stage3a_appointment_projections_are_chronological():
    results = _node_json(
        "const d=require('./docs/diary/stage3a/stage3a-data.js');"
        "const c=require('./docs/diary/stage3a/stage3a-core.js');"
        "const practitioner=c.interpretTask('S3A-03','Open Dr Shera afternoon on Friday week.',d);"
        "const patient=c.interpretTask('S3A-11','Show me all of Margaret Thompson upcoming appointments.',d);"
        "console.log(JSON.stringify({"
        "practitioner:practitioner.projection.items.map(x=>`${x.date}T${x.startsAt}`),"
        "patient:patient.projection.items.map(x=>`${x.date}T${x.startsAt}`)}));"
    )

    assert results == {
        "practitioner": [
            "2026-07-31T13:00",
            "2026-07-31T14:15",
            "2026-07-31T15:30",
        ],
        "patient": [
            "2026-07-31T14:15",
            "2026-08-14T09:00",
            "2027-01-20T14:30",
        ],
    }


def test_stage3a_scenario_baselines_and_attention_sequences_are_explicit():
    data = _node_json(
        "const d=require('./docs/diary/stage3a/stage3a-data.js');"
        "console.log(JSON.stringify({"
        "gridDates:Object.fromEntries(d.scenarios.filter(x=>x.gridDate).map(x=>[x.id,x.gridDate])),"
        "attention:Object.fromEntries(d.scenarios.filter(x=>x.attentionSteps).map(x=>[x.id,x.attentionSteps])),"
        "fixtureIds:d.events.map(x=>x.fixture_id),"
        "eventSummary:d.currentReads['read-margaret-friday-week-v2'].summary}));"
    )

    assert data["gridDates"] == {
        "S3A-01": "2027-01-20",
        "S3A-02": "2027-01-20",
        "S3A-03": "2026-07-31",
        "S3A-04": "2026-07-31",
        "S3A-10": "2026-07-31",
        "S3A-11": "2026-07-31",
    }
    assert data["attention"] == {
        "S3A-12": ["fixture-relevant-reschedule"],
        "S3A-13": [
            "fixture-unrelated-roster",
            "fixture-foreign-practice",
            "fixture-rolled-back",
        ],
        "S3A-14": [
            "fixture-relevant-reschedule",
            "fixture-replay-reschedule",
            "fixture-delayed-reschedule",
        ],
    }
    assert len(data["fixtureIds"]) == len(set(data["fixtureIds"])) == 6
    assert "Friday 31 July 2026" in data["eventSummary"]


def test_stage3a_attention_filter_surfaces_once_and_never_interrupts():
    results = _node_json(
        "const d=require('./docs/diary/stage3a/stage3a-data.js');"
        "const c=require('./docs/diary/stage3a/stage3a-core.js');"
        "const s=c.createAttentionState();"
        "const out=d.events.map(e=>c.evaluateAttentionEvent(e,s,{practiceId:d.practice.id},d));"
        "console.log(JSON.stringify(out.map(x=>({visible:x.visible,attention:x.attention,reason:x.reasonCode}))));"
    )

    assert results == [
        {
            "visible": True,
            "attention": "concise",
            "reason": "relevant_committed_change_confirmed_by_fresh_read",
        },
        {
            "visible": False,
            "attention": "silent",
            "reason": "unrelated_to_retained_task",
        },
        {"visible": False, "attention": "silent", "reason": "foreign_practice"},
        {
            "visible": False,
            "attention": "silent",
            "reason": "uncommitted_or_rolled_back",
        },
        {"visible": False, "attention": "silent", "reason": "duplicate_event"},
        {
            "visible": False,
            "attention": "silent",
            "reason": "stale_or_out_of_order",
        },
    ]
    assert all(result["attention"] != "interruptive" for result in results)


def test_stage3a_counterbalance_reverses_paired_route_order():
    result = _node_json(
        "const d=require('./docs/diary/stage3a/stage3a-data.js');"
        "const c=require('./docs/diary/stage3a/stage3a-core.js');"
        "console.log(JSON.stringify({"
        "a0:c.routeOrderFor(d.scenarios[0],0,'A'),b0:c.routeOrderFor(d.scenarios[0],0,'B'),"
        "a1:c.routeOrderFor(d.scenarios[1],1,'A'),b1:c.routeOrderFor(d.scenarios[1],1,'B')}));"
    )

    assert result == {
        "a0": ["conversation", "grid"],
        "b0": ["grid", "conversation"],
        "a1": ["grid", "conversation"],
        "b1": ["conversation", "grid"],
    }


def test_stage3a_export_schema_omits_prompt_and_transcript_fields():
    app_source = APP_JS.read_text(encoding="utf-8")

    assert 'schema_version: "bernie.stage3a.study-export.v2"' in app_source
    assert 'schema_version: "bernie.stage3a.structured-observation.v2"' in app_source
    assert "contains_prompt_or_transcript_text: false" in app_source
    assert "\n      typed_request:" not in app_source
    assert "\n      prompt_text:" not in app_source
    assert "\n      transcript_text:" not in app_source
    assert "observations: state.observations" in app_source
    assert "observation_flags:" in app_source
    assert "grid_dates_visited:" in app_source


def test_stage3a_scenario_transition_and_recording_guards_prevent_state_leakage():
    html = HTML.read_text(encoding="utf-8")
    app_source = APP_JS.read_text(encoding="utf-8")

    assert "resetProjection();\n    resetAttention();" in app_source
    assert "configureRouteTabs(active);" in app_source
    assert "button.disabled = event.fixture_id !== nextFixtureId" in app_source
    assert "Complete the displayed event-fixture sequence before recording." in app_source
    assert "Visit the remaining required route" in app_source
    assert "Use the grid date selector to inspect every authored" in app_source
    assert "Optional structured observation flags" in html
    assert "No free text is retained" in html
    assert "Committed-change notice" in html
    assert "Separate safety check" in html


def test_stage3a_plan_keeps_fixture_and_authoritative_confirmation_evidence_separate():
    plan = PLAN.read_text(encoding="utf-8")

    assert "authored_synthetic_fixture_browser" in plan
    assert "live_local_browser_backend_postgres" in plan
    assert "The functional harness must never simulate a receipt and call it committed" in plan
    assert "Stage 3B" in plan
    assert "ambient listening" in plan
    assert "committed-event runtime" in plan
