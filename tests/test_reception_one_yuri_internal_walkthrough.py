from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs" / "diary" / "stage3b"
EVIDENCE = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-yuri-internal-walkthrough"
)


def test_yuri_walkthrough_is_a_distinct_single_acknowledgement_surface() -> None:
    expected = {
        "yuri.html",
        "stage3b-yuri.css",
        "stage3b-yuri-core.js",
        "stage3b-yuri.js",
        "stage3b-yuri-export.schema.json",
    }
    assert expected <= {path.name for path in STUDY.iterdir()}
    html = (STUDY / "yuri.html").read_text(encoding="utf-8")
    assert "Reception One - Yuri internal walkthrough" in html
    assert "connect-src 'none'" in html
    assert html.count('type="checkbox"') == 2  # acknowledgement plus ordinary-Diary fallback
    assert html.count('id="acknowledgement-check" type="checkbox"') == 1
    assert "participant-code" not in html
    assert "practice-bucket" not in html
    assert "counterbalance-arm" not in html
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html
    assert 'http://[::1]:3000/meta-grid-auth.html' in html
    assert 'id="task-title" tabindex="-1"' in html


def test_yuri_walkthrough_has_no_network_storage_provider_or_write_path() -> None:
    sources = "\n".join(
        (STUDY / name).read_text(encoding="utf-8")
        for name in [
            "yuri.html",
            "stage3b-yuri-core.js",
            "stage3b-yuri.js",
        ]
    ).lower()
    forbidden = [
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "localstorage",
        "sessionstorage",
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


def test_yuri_walkthrough_export_contract() -> None:
    script = r"""
const data = require('./docs/diary/stage3b/stage3b-data.js');
const core = require('./docs/diary/stage3b/stage3b-yuri-core.js');
const review = core.createReview(true, '2026-07-29T01:02:03.000Z');
for (const task of data.tasks) {
  core.upsertTaskReview(review, core.normalizeTaskReview({
    task_id: task.id,
    result: 'partly_worked',
    orientation: 'mixed',
    relative_value: 'not_compared',
    ordinary_diary_fallback_used: task.id === 'S3B-07',
    issue_flags: task.id === 'S3B-01' ? ['entry_not_obvious'] : [],
    product_note: task.id === 'S3B-01' ? 'The entry point needs to feel more obvious.' : ''
  }, data.tasks.map((item) => item.id), '2026-07-29T01:05:00.000Z'));
}
review.final_review = core.normalizeFinalReview({
  overall_value: 'promising_needs_revision',
  design_partner_readiness: 'not_ready',
  foreground_projection_window: 'supports',
  date_first_page_turn: 'supports',
  bureau_workflow: 'supports',
  text_before_push_to_talk: 'supports',
  product_note: 'Keep the ordinary Diary visibly present.'
}, '2026-07-29T02:00:00.000Z');
process.stdout.write(JSON.stringify(
  core.buildExport(review, data.tasks.length, '2026-07-29T02:01:00.000Z')
));
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
        (STUDY / "stage3b-yuri-export.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(payload)
    assert len(payload["task_reviews"]) == 8
    assert payload["final_review"]["design_partner_readiness"] == "not_ready"
    assert payload["summary"]["threshold_claim"] == (
        "not_applicable_internal_formative"
    )
    assert payload["exclusions"]["representative_participant_evidence"] is False
    assert payload["exclusions"]["contains_free_form_product_notes"] is True
    assert payload["exclusions"]["appointment_write_available"] is False


def test_yuri_walkthrough_acknowledgement_and_note_bounds_fail_closed() -> None:
    script = r"""
const data = require('./docs/diary/stage3b/stage3b-data.js');
const core = require('./docs/diary/stage3b/stage3b-yuri-core.js');
let failures = 0;
try { core.createReview(false); } catch (_) { failures += 1; }
try {
  core.normalizeTaskReview({
    task_id: 'S3B-01',
    result: 'worked',
    orientation: 'clear',
    relative_value: 'not_compared',
    ordinary_diary_fallback_used: false,
    issue_flags: [],
    product_note: 'x'.repeat(1201)
  }, data.tasks.map((item) => item.id));
} catch (_) { failures += 1; }
if (failures !== 2) process.exit(1);
"""
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)


def test_completed_yuri_review_is_schema_valid_and_analysis_is_bound() -> None:
    review_path = EVIDENCE / "completed-review.json"
    analysis_path = EVIDENCE / "completed-review-analysis.json"
    raw_review = review_path.read_bytes()
    review = json.loads(raw_review)
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    schema = json.loads(
        (STUDY / "stage3b-yuri-export.schema.json").read_text(encoding="utf-8")
    )

    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(review)

    assert hashlib.sha256(raw_review).hexdigest() == analysis["source_sha256"]
    assert review["session"]["review_id"] == analysis["source_review_id"]
    assert review["summary"] == {
        "tasks_available": 8,
        "tasks_recorded": 8,
        "worked": 5,
        "partly_worked": 3,
        "did_not_work": 0,
        "skipped": 0,
        "ordinary_diary_fallback_count": 0,
        "threshold_claim": "not_applicable_internal_formative",
    }
    assert analysis["final_disposition"]["design_partner_readiness"] == "not_ready"
    assert analysis["status"] == "accepted_internal_formative_result"


def test_yuri_walkthrough_runner_reuses_provider_disabled_disposable_boundary() -> None:
    source = (
        ROOT / "scripts" / "run_reception_one_yuri_walkthrough.py"
    ).read_text(encoding="utf-8")
    assert "bernie_reception_one_combined_scope_harness" in source
    assert "http://[::1]:3000/diary/stage3b/yuri.html" in source
    assert "database_readback" in source
    assert "cleanup_database" in source
    assert '"provider_used": False' in source
    assert "aiplatform" not in source.lower()
    assert "generativelanguage" not in source.lower()
