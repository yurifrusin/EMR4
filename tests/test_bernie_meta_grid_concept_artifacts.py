"""Deterministic guards for the provider-neutral Bernie meta-grid concept tranche."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re

import pytest


ROOT = Path("orchestration/prototypes/bernie-meta-grid-concept")
PLAN = Path("docs/bernie-meta-grid-concept-tranche-plan.md")
DESIGN = Path("docs/bernie-fluid-meta-grid-concept-design.md")
SCHEMA = ROOT / "projection-contract.schema.json"
EXAMPLES = ROOT / "projection-examples.json"
FIXTURES = ROOT / "fixtures.js"
HTML = ROOT / "index.html"
CSS = ROOT / "styles.css"
APP = ROOT / "app.js"
BROWSER_EVIDENCE = ROOT / "browser-acceptance-evidence.json"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_fixture_bundle():
    text = FIXTURES.read_text(encoding="utf-8")
    prefix = "window.META_GRID_FIXTURES = "
    assert text.startswith(prefix)
    assert text.rstrip().endswith(";")
    return json.loads(text[len(prefix) :].rstrip()[:-1])


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class TestMetaGridConceptScope:
    def test_required_artifacts_exist_outside_published_docs_surface(self):
        for path in (
            PLAN,
            DESIGN,
            SCHEMA,
            EXAMPLES,
            FIXTURES,
            HTML,
            CSS,
            APP,
            BROWSER_EVIDENCE,
        ):
            assert path.is_file(), f"Missing meta-grid artifact: {path}"
            assert path.read_bytes(), f"Empty meta-grid artifact: {path}"

        assert ROOT.parts[0] == "orchestration"
        assert "docs" not in ROOT.parts

    def test_plan_freezes_provider_runtime_and_write_boundaries(self):
        text = PLAN.read_text(encoding="utf-8").lower()
        required = {
            "provider-neutral",
            "authored synthetic",
            "no appointment writes",
            "graphql mutation",
            "event runtime",
            "stage 3b",
            "deployment",
            "representative staff",
        }
        missing = sorted(term for term in required if term not in text)
        assert not missing, f"Plan missing boundary terms: {missing}"

    def test_design_preserves_mixed_api_spine(self):
        text = DESIGN.read_text(encoding="utf-8").lower()
        required = {
            "non-authoritative",
            "graphql",
            "rest/openapi",
            "idempotency",
            "audit",
            "receipt",
            "event cannot",
            "fresh scoped read",
        }
        missing = sorted(term for term in required if term not in text)
        assert not missing, f"Design missing API Spine terms: {missing}"


class TestProjectionContract:
    def test_schema_validates_all_demonstrated_projection_fixtures(self):
        jsonschema = pytest.importorskip("jsonschema")
        schema = _load_json(SCHEMA)
        validator = jsonschema.Draft202012Validator(
            schema,
            format_checker=jsonschema.FormatChecker(),
        )
        bundle = _load_fixture_bundle()

        errors = []
        for key, projection in bundle["projections"].items():
            for error in validator.iter_errors(projection):
                errors.append((key, list(error.absolute_path), error.message))
        assert not errors, f"Projection contract errors: {errors}"

    def test_examples_are_synthetic_and_validate(self):
        jsonschema = pytest.importorskip("jsonschema")
        schema = _load_json(SCHEMA)
        examples = _load_json(EXAMPLES)
        assert examples["contains_real_patient_or_practice_data"] is False
        assert examples["evidence_mode"] == "authored_synthetic_local_static_prototype"

        validator = jsonschema.Draft202012Validator(
            schema,
            format_checker=jsonschema.FormatChecker(),
        )
        for example in examples["projections"]:
            validator.validate(example)

    def test_projection_families_cover_the_frozen_concept_population(self):
        bundle = _load_fixture_bundle()
        families = {projection["family"] for projection in bundle["projections"].values()}
        assert {
            "focused_schedule_lane",
            "patient_timeline",
            "availability_slots",
            "aligned_comparison",
            "change_context",
            "proposal_review",
            "ordinary_overview",
            "clarification",
        } <= families

    def test_appointment_and_slot_items_are_chronological(self):
        bundle = _load_fixture_bundle()
        ordered_kinds = {
            "appointment",
            "available_slot",
            "comparison_slot",
            "proposal_summary",
        }
        for key, projection in bundle["projections"].items():
            starts = [
                _parse_datetime(item["starts_at"])
                for item in projection["items"]
                if item["kind"] in ordered_kinds and item["starts_at"]
            ]
            assert starts == sorted(starts), f"{key} items are not chronological"

    def test_comparison_has_one_shared_temporal_and_location_basis(self):
        comparison = _load_fixture_bundle()["projections"]["comparison"]
        scope = comparison["scope"]
        assert scope["date_from"] == scope["date_to"]
        assert scope["time_from"] == "08:00"
        assert scope["time_to"] == "12:00"
        assert scope["location_ids"] == ["synthetic-location-brisbane"]
        assert scope["duration_minutes"] == 30
        assert len(scope["practitioner_ids"]) == 2
        assert {item["comparison_group"] for item in comparison["items"]} == {
            "Dr Michael Shera",
            "Dr Anika Patel",
        }

    def test_every_projection_denies_client_write_authority(self):
        bundle = _load_fixture_bundle()
        for key, projection in bundle["projections"].items():
            boundary = projection["action_boundary"]
            assert boundary["appointment_write_authority"] is False, key
            assert boundary["operational_command_available"] is False, key

        proposal = bundle["projections"]["proposal"]
        assert proposal["state"] == "proposal_not_committed"
        assert proposal["action_boundary"]["posture"] == "proposal_only"
        assert all(
            projection["state"] != "committed_receipt"
            for projection in bundle["projections"].values()
        )


class TestAttentionFixtureContract:
    def test_event_fixtures_are_minimal_synthetic_control_records(self):
        bundle = _load_fixture_bundle()
        fixtures = bundle["event_fixtures"]
        assert bundle["authored_synthetic"] is True
        assert bundle["contains_real_patient_or_practice_data"] is False
        assert {fixture["classification"] for fixture in fixtures} == {
            "relevant_committed",
            "unrelated",
            "replay",
            "stale_revision",
        }
        prohibited_keys = {
            "patient_name",
            "phone_number",
            "date_of_birth",
            "medicare_number",
            "appointment_reason_text",
            "raw_instruction",
            "transcript",
            "provider_output",
        }
        for fixture in fixtures:
            assert prohibited_keys.isdisjoint(fixture)

    def test_replay_uses_stable_event_identity_and_stale_revision_is_older(self):
        fixtures = _load_fixture_bundle()["event_fixtures"]
        relevant = next(item for item in fixtures if item["classification"] == "relevant_committed")
        replay = next(item for item in fixtures if item["classification"] == "replay")
        stale = next(item for item in fixtures if item["classification"] == "stale_revision")
        assert replay["event_id"] == relevant["event_id"]
        assert replay["aggregate_revision"] == relevant["aggregate_revision"]
        assert stale["aggregate_revision"] < relevant["aggregate_revision"]


class TestStaticLabSafetyAndAccessibility:
    def test_lab_has_no_network_persistence_or_telemetry_primitive(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in (HTML, APP, FIXTURES)
        ).lower()
        prohibited = {
            "fetch(",
            "xmlhttprequest",
            "websocket",
            "eventsource",
            "navigator.sendbeacon",
            "serviceworker",
            "localstorage",
            "sessionstorage",
            "indexeddb",
            "document.cookie",
            "/api/",
        }
        hits = sorted(term for term in prohibited if term in combined)
        assert not hits, f"Static concept lab contains runtime primitive(s): {hits}"

    def test_html_uses_only_local_assets_and_non_submitting_form(self):
        text = HTML.read_text(encoding="utf-8")
        assert 'action="' not in text.lower()
        assert not re.search(r'(?:src|href)=["\']https?://', text, re.IGNORECASE)
        assert '<script src="fixtures.js"></script>' in text
        assert '<script src="app.js"></script>' in text
        assert '<link rel="stylesheet" href="styles.css">' in text

    def test_accessible_shell_and_explicit_state_language_are_present(self):
        html = HTML.read_text(encoding="utf-8").lower()
        app = APP.read_text(encoding="utf-8").lower()
        for landmark in ("<header", "<nav", "<aside", "<main", "<footer"):
            assert landmark in html
        assert 'aria-live="polite"' in html
        assert 'href="#projection-canvas"' in html
        assert 'aria-controls="evidence-panel"' in html
        assert 'id="evidence-heading" tabindex="-1"' in html
        assert "proposal — not committed" in app
        assert "selection only — nothing booked" in app
        assert "clarification needed" in app
        assert "committed-change notice" in app
        assert "confirm in authoritative diary — unavailable in concept lab" in app

    def test_css_encodes_touch_focus_tablet_and_reduced_motion_constraints(self):
        css = CSS.read_text(encoding="utf-8").lower()
        assert "min-height: 44px" in css
        assert ":focus-visible" in css
        assert "@media (max-width: 900px)" in css
        assert "@media (max-width: 620px)" in css
        assert "prefers-reduced-motion" in css
        root_history_rule = css[css.index(".root-history button") :]
        assert "min-height: 44px" in root_history_rule.split("}", 1)[0]

    def test_new_root_transition_clears_transient_state(self):
        app = APP.read_text(encoding="utf-8")
        assert "function clearTransientState()" in app
        assert "state.trail = [];" in app
        assert "state.selectedItemId = null;" in app
        assert "state.deliveredEventIds = new Set();" in app
        assert "state.attentionEntries = [];" in app
        start_root = app[app.index("function startRoot") : app.index("function restoreRecentRoot")]
        assert "clearTransientState();" in start_root

    def test_selection_and_proposal_are_reversible_and_non_committing(self):
        app = APP.read_text(encoding="utf-8")
        assert "innerHTML" not in app
        assert "function localTime24(" in app
        assert "selected.scope.time_from = localTime24(" in app
        assert "selected.scope.time_to = localTime24(" in app
        assert 'event.detail === 0 ? "keyboard" : "touch"' in app
        assert "state.trail.push(clone(state.current));" in app
        assert 'selected.state = "selection_only";' in app
        assert 'proposal_not_committed' in app
        assert "confirm.disabled = true;" in app
        assert "elements.backButton.addEventListener" in app

    def test_browser_evidence_is_synthetic_bounded_and_cleaned_up(self):
        evidence = _load_json(BROWSER_EVIDENCE)
        assert evidence["result"] == "pass"
        assert evidence["evidence_mode"] == "authored_synthetic_local_static_prototype"
        assert evidence["contains_real_patient_or_practice_data"] is False
        assert evidence["runtime_integrations_exercised"] == []
        assert evidence["console_warnings_or_errors"] == 0
        assert {viewport["name"] for viewport in evidence["viewports"]} == {
            "desktop",
            "tablet_portrait",
            "tablet_landscape",
        }
        assert all(
            not viewport["horizontal_page_overflow"]
            and viewport["minimum_enabled_button_height_px"] >= 44
            for viewport in evidence["viewports"]
        )
        assert evidence["runtime_cleanup"] == {
            "browser_tabs_finalized": True,
            "local_server_pid": 62472,
            "local_server_stopped": True,
            "port_4173_free_after_stop": True,
        }
