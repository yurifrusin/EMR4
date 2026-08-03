from __future__ import annotations

import ast
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

browser_acceptance = importlib.import_module(
    "scripts.raisa_provider_free_native_diary_application_session_"
    "route_intercepted_browser_acceptance"
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "raisa_provider_free_native_diary_application_session_"
    "route_intercepted_browser_acceptance.py"
)
OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-native-diary-application-session-"
    "route-intercepted-browser"
)
EVIDENCE = OUTPUT / "route-intercepted-browser-evidence.json"
PLAN = (
    ROOT
    / "docs"
    / "raisa-provider-free-native-diary-application-session-"
    "route-intercepted-browser-plan.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-provider-free-native-diary-application-session-"
    "route-intercepted-browser-threat-model-delta.md"
)
CLOSEOUT = (
    ROOT
    / "docs"
    / "raisa-provider-free-native-diary-application-session-"
    "route-intercepted-browser-closeout.md"
)
EXPECTED_MODULE_PATHS = {
    "/diary/application-session-practitioner-directory.mjs",
    "/diary/application-session-practitioner-reconciler.mjs",
}


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def _case(case_id: str) -> dict:
    cases = {case["case_id"]: case for case in _evidence()["cases"]}
    return cases[case_id]


def test_committed_evidence_reproduces_in_serial_real_chromium() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert '"status": "passed"' in completed.stdout


def test_evidence_is_exactly_route_intercepted_and_authority_closed() -> None:
    evidence = _evidence()
    assert evidence["schema_version"] == (
        "raisa.native-diary-application-session-"
        "route-intercepted-browser-evidence.v1"
    )
    assert evidence["candidate_result"] == "candidate_ready"
    assert evidence["evidence_mode"] == "route_intercepted_browser"
    assert evidence["data_class"] == "authored_synthetic"
    assert evidence["browser"]["engine"] == "chromium"
    assert evidence["browser"]["headless"] is True
    assert evidence["browser"]["static_route_fixture_paths"] == [
        "/hosting-policy.js"
    ]
    assert evidence["checks"]
    assert all(evidence["checks"].values())
    assert evidence["authority"]
    assert all(value is False for value in evidence["authority"].values())
    for case in evidence["cases"]:
        for request_tuple in case["api_request_tuples"]:
            method, path = request_tuple.split(" ", 1)
            assert browser_acceptance.ALLOWED_API_METHODS[path] == method


def test_enabled_success_loads_real_modules_and_avoids_legacy_before_transition() -> None:
    case = _case("enabled_success_and_disable_transition")
    assert EXPECTED_MODULE_PATHS <= set(case["module_paths_loaded"])
    assert case["fixed_reader_options"] == [
        "Avery Browser Synthetic (Browser Synthetic Clinic)",
        "Morgan Browser Synthetic",
    ]
    assert case["pre_transition_graphql_request_count"] == 0
    assert case["pre_transition_legacy_rest_practitioner_request_count"] == 0
    assert case["unknown_api_paths"] == []
    assert case["unexpected_api_requests"] == []
    assert case["blocked_external_hosts"] == []
    assert case["console_errors"] == []


def test_disable_transition_invalidates_held_result_then_recovers_legacy() -> None:
    case = _case("enabled_success_and_disable_transition")
    expected_legacy = ["Legacy Browser Synthetic (Browser Synthetic Clinic)"]
    assert case["post_disable_graphql_request_count"] == 1
    assert case["post_disable_legacy_rest_practitioner_request_count"] == 0
    assert case["stale_row_visible_count"] == 0
    assert case["late_stale_failure_marker_observed"] is True
    assert case["legacy_options_before_stale_resolution"] == expected_legacy
    assert case["legacy_options_after_recovery"] == expected_legacy
    assert case["graphql_request_count"] == 2
    assert case["legacy_rest_practitioner_request_count"] == 0


def test_enabled_reader_failure_is_generic_and_has_no_partial_grid() -> None:
    case = _case("enabled_reader_failure")
    assert EXPECTED_MODULE_PATHS <= set(case["module_paths_loaded"])
    assert case["fixed_reader_call_count"] == 1
    assert case["error_text"] == (
        "Failed to load diary: "
        "application_session_practitioner_directory_failure"
    )
    assert "raw_reader_failure_must_not_escape" not in case["error_text"]
    assert case["grid_container_hidden"] is True
    assert case["grid_child_count"] == 0
    assert case["graphql_request_count"] == 0
    assert case["legacy_rest_practitioner_request_count"] == 0
    assert case["unknown_api_paths"] == []
    assert case["unexpected_api_requests"] == []
    assert case["blocked_external_hosts"] == []
    assert case["console_errors"] == []


def test_feature_off_preserves_graphql_and_never_loads_composition_modules() -> None:
    case = _case("feature_off_legacy_graphql")
    assert case["bootstrap_present"] is False
    assert case["graphql_request_count"] == 1
    assert case["legacy_rest_practitioner_request_count"] == 0
    assert case["legacy_options"] == [
        "Legacy Browser Synthetic (Browser Synthetic Clinic)"
    ]
    assert case["module_paths_loaded"] == []
    assert case["unknown_api_paths"] == []
    assert case["unexpected_api_requests"] == []
    assert case["blocked_external_hosts"] == []
    assert case["console_errors"] == []


def test_source_hashes_bind_exact_browser_assets_and_policy_fixture() -> None:
    evidence = _evidence()
    assert set(evidence["source_hashes"]) == {
        "docs/diary/application-session-practitioner-directory.mjs",
        "docs/diary/application-session-practitioner-reconciler.mjs",
        "docs/diary/diary.html",
        "docs/diary/diary.js",
        "docs/taskpane/hosting-policy.js",
    }
    for relative, expected in evidence["source_hashes"].items():
        actual = f"sha256:{hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()}"
        assert actual == expected


def test_route_fixture_allowlist_binds_every_path_to_one_exact_http_method() -> None:
    assert browser_acceptance.ALLOWED_API_METHODS == {
        "/api/v1/diary/locations": "GET",
        "/api/v1/diary/template": "GET",
        "/api/v1/appointments": "GET",
        "/api/v1/appointments/types": "GET",
        "/api/v1/diary/roster": "GET",
        "/api/v1/diary/waiting-areas": "GET",
        "/api/v1/graphql": "POST",
        "/api/v1/appointments/bernie/pilot-eligibility": "GET",
    }
    admit = browser_acceptance._api_fixture_admission
    assert admit("GET", "/api/v1/appointments") == "admitted"
    assert admit("POST", "/api/v1/graphql") == "admitted"
    assert admit("OPTIONS", "/api/v1/graphql") == "cors_preflight"
    assert admit("DELETE", "/api/v1/appointments") == "wrong_method"
    assert admit("GET", "/api/v1/graphql") == "wrong_method"
    assert admit("OPTIONS", "/api/v1/unknown") == "unknown_path"


def test_harness_has_no_product_runtime_database_provider_or_internal_render_call() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not {
        "app",
        "fastapi",
        "sqlalchemy",
        "psycopg",
        "httpx",
        "requests",
        "google",
        "openai",
        "anthropic",
    } & imports
    for prohibited in (
        "app.main",
        "uvicorn",
        "loadDiary(",
        "loadPractitionerDirectory(",
        "loadApplicationSessionPractitionerDirectory(",
        "createApplicationSessionPractitionerDirectory(",
        "reconcileAndRender(",
        "renderGrid(",
    ):
        assert prohibited not in source
    assert 'page.route("**/*", handle)' in source
    assert 'ThreadingHTTPServer(("127.0.0.1", 0)' in source


def test_plan_threat_and_closeout_keep_claims_closed_and_exclude_screenshots() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PLAN, THREAT, CLOSEOUT)
    )
    assert "route_intercepted_browser" in combined
    assert "No real application-session injection" in combined
    assert "No product boundary changes" in combined
    assert "docs/branding/" in combined
    assert "Screenshots are intentionally excluded" in combined
    assert "Sol owns final acceptance" in combined
    assert "This is not live browser/backend/PostgreSQL evidence." in combined
    assert not list(OUTPUT.glob("*.png"))
