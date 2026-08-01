import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree

import pytest
from fastapi.testclient import TestClient

from app.services.application_auth_runtime import Surface
from scripts.raisa_shared_application_auth_office_cookie_compatibility import (
    DEVELOPMENT_ORIGIN,
    OfficeCookieCompatibilityHarness,
    build_app,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-shared-application-auth-office-cookie-compatibility-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-shared-application-auth-office-cookie-compatibility-threat-model-delta.md"
)
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "shared-application-auth-office-cookie-compatibility"
)
SCRIPT = CONTINUITY / "taskpane.js"
LIVE_EVIDENCE = CONTINUITY / "live-office-host-evidence.json"
RESIDUE_EVIDENCE = CONTINUITY / "final-residue-evidence.json"
ACCEPTANCE_EVIDENCE = CONTINUITY / "acceptance-evidence.json"
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
CLOSEOUT = (
    ROOT / "docs" / "raisa-shared-application-auth-office-cookie-compatibility-closeout.md"
)
SOL_ACCEPTANCE = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-office-cookie-compatibility-sol-acceptance.md"
)
MANIFESTS = {
    Surface.WORD_DESKTOP: CONTINUITY / "word-desktop-manifest.xml",
    Surface.WORD_ONLINE: CONTINUITY / "word-online-manifest.xml",
}
RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-office-cookie-compatibility-rehydration-receipt.json"
)
NS = {
    "office": "http://schemas.microsoft.com/office/appforoffice/1.1",
    "ov": "http://schemas.microsoft.com/office/taskpaneappversionoverrides",
    "bt": "http://schemas.microsoft.com/office/officeappbasictypes/1.0",
}
PROXY_HEADERS = {
    "Origin": DEVELOPMENT_ORIGIN,
    "X-Forwarded-For": "203.0.113.41",
    "X-Forwarded-Proto": "https",
}


def _taskpane_material(markup: str) -> tuple[str, str]:
    bootstrap = re.search(r'data-bootstrap="([^"]*)"', markup)
    nonce = re.search(r'data-evidence-nonce="([^"]*)"', markup)
    assert bootstrap is not None and nonce is not None
    return html.unescape(bootstrap.group(1)), html.unescape(nonce.group(1))


def _post(client: TestClient, path: str, body: dict, csrf: str | None = None):
    headers = dict(PROXY_HEADERS)
    if csrf:
        headers["X-EMR4-CSRF"] = csrf
    return client.post(path, json=body, headers=headers)


def _exercise_surface(
    client: TestClient,
    surface: Surface,
) -> tuple[str, dict[str, bool]]:
    page = client.get(
        "/office-cookie-compatibility/taskpane",
        params={"surface": surface.value},
    )
    assert page.status_code == 200
    assert page.headers["cache-control"] == "no-store"
    csp_directives = {
        parts[0]: parts[1:]
        for directive in page.headers["content-security-policy"].split(";")
        if (parts := directive.split())
    }
    assert csp_directives["script-src"] == [
        "'self'",
        "https://appsforoffice.microsoft.com",
    ]
    bootstrap, evidence_nonce = _taskpane_material(page.text)
    assert len(bootstrap) >= 43
    assert len(evidence_nonce) >= 43
    assert bootstrap not in repr(page.headers)

    second_page = client.get(
        "/office-cookie-compatibility/taskpane",
        params={"surface": surface.value},
    )
    assert _taskpane_material(second_page.text) == ("", "")

    csrf_response = _post(
        client,
        "/api/v1/application-auth/csrf",
        {"surface": surface.value},
    )
    assert csrf_response.status_code == 200
    assert all(
        marker in csrf_response.headers["set-cookie"].lower()
        for marker in ("secure", "httponly", "samesite=none", "partitioned")
    )
    csrf = csrf_response.json()["csrf_token"]

    login = _post(
        client,
        "/api/v1/application-auth/synthetic/session",
        {"surface": surface.value, "bootstrap_credential": bootstrap},
        csrf,
    )
    assert login.status_code == 200
    csrf = login.json()["csrf_token"]

    first_validation = _post(
        client,
        "/api/v1/application-auth/session/validate",
        {"surface": surface.value},
        csrf,
    )
    assert first_validation.status_code == 200
    assert first_validation.json()["surface"] == surface.value

    rotation = _post(
        client,
        "/api/v1/application-auth/session/rotate",
        {"surface": surface.value},
        csrf,
    )
    assert rotation.status_code == 200
    csrf = rotation.json()["csrf_token"]

    second_validation = _post(
        client,
        "/api/v1/application-auth/session/validate",
        {"surface": surface.value},
        csrf,
    )
    assert second_validation.status_code == 200

    logout = _post(
        client,
        "/api/v1/application-auth/session/logout",
        {"surface": surface.value},
        csrf,
    )
    assert logout.status_code == 204

    new_csrf = _post(
        client,
        "/api/v1/application-auth/csrf",
        {"surface": surface.value},
    )
    assert new_csrf.status_code == 200
    denied = _post(
        client,
        "/api/v1/application-auth/session/validate",
        {"surface": surface.value},
        new_csrf.json()["csrf_token"],
    )
    assert denied.status_code == 401
    assert denied.json() == {"detail": "application_authentication_failed"}

    steps = {
        "csrf_issued": True,
        "session_created": True,
        "first_validation_passed": True,
        "rotation_passed": True,
        "second_validation_passed": True,
        "logout_passed": True,
        "post_logout_denied": True,
    }
    return evidence_nonce, steps


def test_plan_threat_and_receipt_freeze_the_five_source_zero_authority_boundary():
    text = PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")
    for required in (
        "provider-free",
        "authored-synthetic",
        "installed Word",
        "Word Online",
        "Partitioned",
        "no bearer",
        "document API",
        "not a cloud",
        "real identity",
        "production",
    ):
        assert required.lower() in text.lower()

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["worker_dispatch_permitted"] is False
    assert receipt["rehydrated_from_receipt"] is True
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]


def test_task_specific_manifests_are_distinct_restricted_and_exact_origin_bound():
    identities = set()
    for surface, path in MANIFESTS.items():
        root = ElementTree.parse(path).getroot()
        identity = root.find("office:Id", NS).text
        identities.add(identity)
        assert root.find("office:Permissions", NS).text == "Restricted"
        default = root.find(
            "office:DefaultSettings/office:SourceLocation",
            NS,
        ).attrib["DefaultValue"]
        resource = root.find(
            "ov:VersionOverrides/ov:Resources/bt:Urls/bt:Url[@id='Taskpane.Url']",
            NS,
        ).attrib["DefaultValue"]
        assert default == resource
        parsed = urlparse(default)
        assert f"{parsed.scheme}://{parsed.netloc}" == DEVELOPMENT_ORIGIN
        assert parsed.path == "/office-cookie-compatibility/taskpane"
        assert parse_qs(parsed.query) == {"surface": [surface.value]}
    assert len(identities) == 2


def test_taskpane_has_no_document_storage_cookie_or_bearer_fallback():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'credentials: "include"' in source
    assert "Office.onReady" in source
    for forbidden in (
        "Word.run",
        "Office.context.document",
        "document.cookie",
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "Authorization",
        "exchange/issue",
        "exchange/redeem",
        "/api/v1/appointments",
        "/graphql",
    ):
        assert forbidden not in source


def test_harness_exposes_only_the_frozen_auth_and_task_routes():
    app = build_app()
    routes = {(method, route.path) for route in app.routes for method in route.methods}
    assert routes == {
        ("POST", "/api/v1/application-auth/csrf"),
        ("POST", "/api/v1/application-auth/synthetic/session"),
        ("POST", "/api/v1/application-auth/session/validate"),
        ("POST", "/api/v1/application-auth/session/rotate"),
        ("POST", "/api/v1/application-auth/session/logout"),
        ("POST", "/api/v1/application-auth/exchange/issue"),
        ("POST", "/api/v1/application-auth/exchange/redeem"),
        ("GET", "/office-cookie-compatibility/taskpane"),
        ("GET", "/office-cookie-compatibility/taskpane.js"),
        ("GET", "/office-cookie-compatibility/taskpane.css"),
        ("GET", "/office-cookie-compatibility/icon/{size}.png"),
        ("POST", "/office-cookie-compatibility/result"),
        ("GET", "/office-cookie-compatibility/evidence"),
    }


def test_evidence_endpoint_is_local_only_even_behind_the_loopback_tunnel():
    app = build_app()
    public_client = TestClient(
        app,
        base_url=DEVELOPMENT_ORIGIN,
        client=("127.0.0.1", 50000),
    )
    forwarded = public_client.get(
        "/office-cookie-compatibility/evidence",
        headers=PROXY_HEADERS,
    )
    assert forwarded.status_code == 404
    assert forwarded.json() == {"detail": "evidence_not_available"}

    local_client = TestClient(
        app,
        base_url="http://127.0.0.1:8001",
        client=("127.0.0.1", 50000),
    )
    local = local_client.get("/office-cookie-compatibility/evidence")
    assert local.status_code == 200
    assert local.headers["cache-control"] == "no-store"


def test_live_host_evidence_is_closed_complete_and_zero_authority():
    evidence = json.loads(LIVE_EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["result"] == "pass"
    assert evidence["data_class"] == "authored_synthetic"
    assert evidence["runtime_class"] == "provider_free_process_local_in_memory"
    assert evidence["bootstrap_registry_counts"] == {
        "available": 0,
        "reserved": 0,
        "consumed": 2,
    }
    assert evidence["sequence_deviation_disposition"]["security_effect"] == (
        "none_independent_principals_bootstraps_and_results"
    )
    for surface, host_class in (
        ("word_desktop", "installed_word"),
        ("word_online", "word_online"),
    ):
        result = evidence["results"][surface]
        assert result == {
            "surface": surface,
            "host_class": host_class,
            "terminal_status": "passed",
            "csrf_issued": True,
            "session_created": True,
            "first_validation_passed": True,
            "rotation_passed": True,
            "second_validation_passed": True,
            "logout_passed": True,
            "post_logout_denied": True,
            "result_submitted": True,
            "failure_code": "none",
        }
    assert set(evidence["side_effects"].values()) == {0}

    serialized = json.dumps(evidence, sort_keys=True).lower()
    for forbidden in (
        "bootstrap_credential",
        "evidence_nonce",
        "set-cookie",
        "authorization",
        "patient_id",
        "document_id",
        "tenant_id",
        "account_id",
    ):
        assert forbidden not in serialized


def test_acceptance_residue_and_closeout_are_truthful_and_bounded():
    acceptance = json.loads(ACCEPTANCE_EVIDENCE.read_text(encoding="utf-8"))
    residue = json.loads(RESIDUE_EVIDENCE.read_text(encoding="utf-8"))
    assert acceptance["result"] == (
        "raisa_shared_application_auth_office_cookie_compatibility_pass"
    )
    assert acceptance["passed"] is True
    assert acceptance["real_office_hosts"] == {
        "word_desktop_passed": True,
        "word_online_passed": True,
        "independent_principals": True,
        "independent_one_use_bootstraps": True,
        "post_logout_denial_passed_on_both": True,
        "remaining_application_sessions": 0,
    }
    assert acceptance["sequence_deviation"]["requires_rerun"] is False
    assert acceptance["parent_ci_reconciliation"] == {
        "stored_source_hashes_corrected": 2,
        "runtime_behavior_changed": False,
        "reason_code": "protected_pr69_acceptance_evidence_digest_drift",
    }
    assert set(acceptance["closed_side_effects"].values()) == {0}

    required_cleanup = residue["required_task_cleanup"]
    assert set(required_cleanup.values()) == {0}
    assert residue["office_host_residue"]["developer_registration_present"] is False
    assert residue["office_host_residue"]["taskpane_can_reload"] is False
    assert residue["office_host_residue"]["document_content_inspected"] is False
    assert residue["office_host_residue"]["document_content_written"] is False
    assert set(residue["external_residue"].values()) == {0}

    closeout = CLOSEOUT.read_text(encoding="utf-8")
    sol_acceptance = SOL_ACCEPTANCE.read_text(encoding="utf-8")
    for text in (closeout, sol_acceptance):
        assert "raisa_shared_application_auth_office_cookie_compatibility_pass" in text
        assert "real identity" in text.lower()
        assert "production" in text.lower()
        assert "release" in text.lower()


def test_continuity_and_compass_bind_the_terminal_result():
    node_id = "raisa-shared-application-auth-office-cookie-compatibility"
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    assert graph["graph_revision"] == 187
    assert graph["nodes"][-1]["id"] == node_id
    assert graph["nodes"][-1]["status"] == "accepted"
    node = graph["nodes"][-1]
    alert_decision = next(
        item
        for item in node["decisions"]
        if item["id"] == "register-post-snapshot-dependabot-alert-17-open-187"
    )
    assert alert_decision["status"] == "accepted"
    assert "dependabot-alert-17-readback.json" in alert_decision["source"]
    assert any("open/needs_review" in gate for gate in node["unresolved_gates"])
    assert compass["map_revision"] == 168
    assert compass["source_graph_revision"] == 187
    assert compass["current_position"]["node_id"] == node_id
    assert "shared-application-auth-office-cookie-compatibility" not in {
        item["id"] for item in compass["decision_horizon"]
    }
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"]
        == "authorize-shared-application-auth-office-cookie-compatibility"
    )
    assert "Satisfied on 2026-08-01" in decision["required_before"]
    alert_disposition = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"] == "authorize-dependabot-alert-17-native-disposition"
    )
    assert "GitHub alert-state mutation" in alert_disposition["required_before"]
    assert "native-open/needs_review" in alert_disposition["required_before"]


def test_both_surface_lifecycles_and_closed_sanitized_evidence_pass():
    harness = OfficeCookieCompatibilityHarness()
    client = TestClient(
        build_app(harness),
        base_url=DEVELOPMENT_ORIGIN,
        client=("127.0.0.1", 50000),
    )
    for surface, host_class in (
        (Surface.WORD_DESKTOP, "installed_word"),
        (Surface.WORD_ONLINE, "word_online"),
    ):
        nonce, steps = _exercise_surface(client, surface)
        submitted = client.post(
            "/office-cookie-compatibility/result",
            headers={"Origin": DEVELOPMENT_ORIGIN},
            json={
                "evidence_nonce": nonce,
                "surface": surface.value,
                "host_class": host_class,
                "terminal_status": "passed",
                **steps,
                "result_submitted": True,
                "failure_code": "none",
            },
        )
        assert submitted.status_code == 201
        assert "evidence_nonce" not in submitted.text

    evidence = harness.evidence()
    assert evidence["bootstrap_registry_counts"] == {
        "available": 0,
        "reserved": 0,
        "consumed": 2,
    }
    assert all(
        evidence["results"][surface.value]["terminal_status"] == "passed"
        for surface in MANIFESTS
    )
    assert set(evidence["side_effects"].values()) == {0}
    rendered = json.dumps(evidence, sort_keys=True)
    for forbidden in ("bootstrap_credential", "evidence_nonce", "Set-Cookie"):
        assert forbidden not in rendered


def test_wrong_surface_origin_replay_and_unbounded_evidence_fail_closed():
    harness = OfficeCookieCompatibilityHarness()
    client = TestClient(
        build_app(harness),
        base_url=DEVELOPMENT_ORIGIN,
        client=("127.0.0.1", 50000),
    )
    page = client.get(
        "/office-cookie-compatibility/taskpane",
        params={"surface": Surface.WORD_DESKTOP.value},
    )
    bootstrap, nonce = _taskpane_material(page.text)
    csrf = _post(
        client,
        "/api/v1/application-auth/csrf",
        {"surface": Surface.WORD_ONLINE.value},
    ).json()["csrf_token"]
    wrong_surface = _post(
        client,
        "/api/v1/application-auth/synthetic/session",
        {
            "surface": Surface.WORD_ONLINE.value,
            "bootstrap_credential": bootstrap,
        },
        csrf,
    )
    assert wrong_surface.status_code == 403
    assert wrong_surface.json() == {"detail": "request_not_admitted"}

    wrong_origin = client.post(
        "/api/v1/application-auth/csrf",
        headers={**PROXY_HEADERS, "Origin": "https://untrusted.example"},
        json={"surface": Surface.WORD_DESKTOP.value},
    )
    assert wrong_origin.status_code == 403

    invalid_result = client.post(
        "/office-cookie-compatibility/result",
        headers={"Origin": DEVELOPMENT_ORIGIN},
        json={
            "evidence_nonce": nonce,
            "surface": Surface.WORD_DESKTOP.value,
            "host_class": "installed_word",
            "terminal_status": "failed",
            "csrf_issued": False,
            "session_created": False,
            "first_validation_passed": False,
            "rotation_passed": False,
            "second_validation_passed": False,
            "logout_passed": False,
            "post_logout_denied": False,
            "result_submitted": True,
            "failure_code": "login_failed",
            "raw_error": "must never be admitted",
        },
    )
    assert invalid_result.status_code == 422


@pytest.mark.parametrize("surface", ["native_diary", "not_a_surface"])
def test_taskpane_rejects_every_non_office_surface(surface: str):
    client = TestClient(
        build_app(),
        base_url=DEVELOPMENT_ORIGIN,
        client=("127.0.0.1", 50000),
    )
    response = client.get(
        "/office-cookie-compatibility/taskpane",
        params={"surface": surface},
    )
    assert response.status_code in {404, 422}
