from __future__ import annotations

import json
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs" / "diary" / "stage3b"


def test_stage3b_files_and_frozen_boundary() -> None:
    expected = {
        "index.html",
        "stage3b.css",
        "stage3b-data.js",
        "stage3b-core.js",
        "stage3b.js",
        "stage3b-study-export.schema.json",
    }
    assert expected <= {path.name for path in STUDY.iterdir()}
    html = (STUDY / "index.html").read_text(encoding="utf-8")
    css = (STUDY / "stage3b.css").read_text(encoding="utf-8")
    assert "connect-src 'none'" in html
    assert "No real patient data" in html
    assert "no appointment write" in html.lower()
    assert "textarea" not in html.lower()
    assert "contenteditable" not in html.lower()
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html
    assert 'id="task-title" tabindex="-1"' in html
    assert "[hidden] { display: none !important; }" in css


def test_stage3b_sidecar_has_no_network_storage_provider_or_write_path() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in STUDY.glob("*")
        if path.suffix in {".html", ".js"}
    ).lower()
    forbidden = [
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "localstorage",
        "sessionstorage",
        "window.open",
        "document.cookie",
        "indexeddb",
        "generativelanguage.googleapis.com",
        "aiplatform.googleapis.com",
        "gemini_api_key",
        "google_api_key",
        "google_application_credentials",
        "/appointments/confirm",
        "/appointments/create",
        "method: \"post\"",
        "method: 'post'",
    ]
    assert not [token for token in forbidden if token in sources]


def test_stage3b_core_contract_and_scoring() -> None:
    script = r"""
const data = require('./docs/diary/stage3b/stage3b-data.js');
const core = require('./docs/diary/stage3b/stage3b-core.js');
const session = core.createSession({
  participant_code: 'P01',
  practice_bucket: 'practice-a',
  counterbalance_arm: 'A',
  consent_voluntary: true,
  consent_synthetic: true,
  consent_no_recording: true,
  consent_no_write: true
}, data, '2026-07-24T12:00:00.000Z');
for (const task of data.tasks) {
  core.upsertObservation(session, core.normalizeObservation({
    route_visits: {
      reception_one: core.assignedRoute(task, 'A') === 'reception_one',
      ordinary_diary: core.assignedRoute(task, 'A') === 'ordinary_diary'
    },
    elapsed_ms: core.assignedRoute(task, 'A') === 'reception_one' ? 40000 : 60000,
    task_outcome: 'completed',
    correctness: 'correct',
    state_comprehension: 'clear',
    confidence: 'high',
    assistance_count: 0,
    ordinary_diary_fallback: false,
    safe_ambiguity: task.id === 'S3B-06' ? 'safe_clarification' : 'not_applicable',
    proposal_boundary: task.id === 'S3B-05' ? 'understood_not_committed' : 'not_applicable',
    issue_flags: []
  }, session, task, '2026-07-24T12:01:00.000Z'));
}
process.stdout.write(JSON.stringify(core.buildExport(session, '2026-07-24T12:20:00.000Z')));
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    schema = json.loads(
        (STUDY / "stage3b-study-export.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(payload)
    assert len(payload["observations"]) == 8
    assert payload["score"]["safety_gate"]["status"] == "passed"
    assert payload["score"]["thresholds"]["grid_free_completion"]["status"] == "passed"
    assert payload["score"]["thresholds"]["safe_ambiguity_recovery"]["status"] == "passed"
    assert payload["score"]["thresholds"]["low_interruption_notice_precision_recall"]["status"] == "not_measured"
    assert payload["exclusions"]["contains_prompt_or_transcript_text"] is False
    assert payload["exclusions"]["appointment_write_available"] is False


def test_stage3b_consent_and_allowlists_fail_closed() -> None:
    script = r"""
const data = require('./docs/diary/stage3b/stage3b-data.js');
const core = require('./docs/diary/stage3b/stage3b-core.js');
let failures = 0;
try {
  core.createSession({
    participant_code: 'Sarah',
    practice_bucket: 'practice-a',
    counterbalance_arm: 'A',
    consent_voluntary: true,
    consent_synthetic: true,
    consent_no_recording: true,
    consent_no_write: true
  }, data);
} catch (_) { failures += 1; }
try {
  core.createSession({
    participant_code: 'P01',
    practice_bucket: 'practice-a',
    counterbalance_arm: 'A',
    consent_voluntary: false,
    consent_synthetic: true,
    consent_no_recording: true,
    consent_no_write: true
  }, data);
} catch (_) { failures += 1; }
if (failures !== 2) process.exit(1);
"""
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)


def test_stage3b_definition_is_counterbalanced_and_synthetic() -> None:
    script = r"""
const data = require('./docs/diary/stage3b/stage3b-data.js');
if (data.schema_version !== 'reception_one.stage3b.study_definition.v1') process.exit(1);
if (data.evidence_mode !== 'authored_synthetic') process.exit(2);
if (data.tasks.length !== 8) process.exit(3);
if (data.referenceDate !== '2026-07-27') process.exit(7);
if (!data.tasks.some(t => t.routeByArm.A !== t.routeByArm.B)) process.exit(4);
if (!data.tasks.every(t => ['reception_one','ordinary_diary'].includes(t.routeByArm.A))) process.exit(5);
if (!data.tasks.every(t => ['reception_one','ordinary_diary'].includes(t.routeByArm.B))) process.exit(6);
"""
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)


def test_stage3b_product_task_acceptance_is_read_only() -> None:
    source = (
        ROOT
        / "scripts"
        / "reception_one_stage3b_product_task_acceptance.py"
    ).read_text(encoding="utf-8")
    assert "route_interception" in source
    assert "api_interception" in source
    assert "appointment_confirmation_activated" in source
    assert "meta-grid-proposal-handoff" in source
    assert '"/confirm"' in source
    assert '"/sessions"' in source
    assert "handoff.click" not in source
    assert "handoff_available = handoff.is_enabled()" in source
