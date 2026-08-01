import html
import json
import re
from pathlib import Path
from xml.etree import ElementTree

from fastapi.testclient import TestClient

from app.services.application_auth_runtime import Surface
from scripts.raisa_shared_application_auth_office_cookie_compatibility import (
    DEVELOPMENT_ORIGIN,
    OfficeCookieCompatibilityHarnessBase,
    build_app,
)
from scripts.raisa_shared_application_auth_postgresql_office_host_compatibility import (
    PostgresOfficeCookieCompatibilityHarness,
    RESULT,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "raisa-shared-application-auth-postgresql-office-host-compatibility-plan.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-shared-application-auth-postgresql-office-host-compatibility-threat-model-delta.md"
)
RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-postgresql-office-host-compatibility-rehydration-receipt.json"
)
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "shared-application-auth-postgresql-office-host-compatibility"
)
SCRIPT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "shared-application-auth-office-cookie-compatibility"
    / "taskpane.js"
)
HARNESS_SCRIPT = (
    ROOT
    / "scripts"
    / "raisa_shared_application_auth_postgresql_office_host_compatibility.py"
)
LIVE_EVIDENCE = CONTINUITY / "live-office-backend-postgres-evidence.json"
RESIDUE_EVIDENCE = CONTINUITY / "final-residue-evidence.json"
ACCEPTANCE_EVIDENCE = CONTINUITY / "acceptance-evidence.json"
CODEQL_READBACK = CONTINUITY / "codeql-pr71-alert-545-readback.json"
CODEQL_TRIAGE = (
    ROOT / "docs" / "security" / "pr71-codeql-alert-545-triage-2026-08-01.md"
)
CODEQL_LEDGER = (
    ROOT
    / "docs"
    / "security"
    / "pr71-codeql-alert-545-validation-ledger.jsonl"
)
CLOSEOUT = (
    ROOT
    / "docs"
    / "raisa-shared-application-auth-postgresql-office-host-compatibility-closeout.md"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
COMPASS_REPORT = ROOT / "docs" / "ariadne-compass-current.md"
MANIFESTS = {
    Surface.WORD_DESKTOP: CONTINUITY / "word-desktop-manifest.xml",
    Surface.WORD_ONLINE: CONTINUITY / "word-online-manifest.xml",
}
NS = {
    "office": "http://schemas.microsoft.com/office/appforoffice/1.1",
    "ov": "http://schemas.microsoft.com/office/taskpaneappversionoverrides",
    "bt": "http://schemas.microsoft.com/office/officeappbasictypes/1.0",
}
PROXY_HEADERS = {
    "Origin": DEVELOPMENT_ORIGIN,
    "X-Forwarded-For": "203.0.113.42",
    "X-Forwarded-Proto": "https",
}


def _taskpane_material(markup: str) -> tuple[str, str]:
    bootstrap = re.search(r'data-bootstrap="([^"]*)"', markup)
    nonce = re.search(r'data-evidence-nonce="([^"]*)"', markup)
    assert bootstrap is not None and nonce is not None
    return html.unescape(bootstrap.group(1)), html.unescape(nonce.group(1))


def _post(
    client: TestClient,
    path: str,
    body: dict,
    csrf: str | None = None,
):
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
    bootstrap, evidence_nonce = _taskpane_material(page.text)
    assert len(bootstrap) >= 43
    assert len(evidence_nonce) >= 43
    assert _taskpane_material(
        client.get(
            "/office-cookie-compatibility/taskpane",
            params={"surface": surface.value},
        ).text
    ) == ("", "")

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

    first = _post(
        client,
        "/api/v1/application-auth/session/validate",
        {"surface": surface.value},
        csrf,
    )
    assert first.status_code == 200
    assert first.json()["surface"] == surface.value

    rotation = _post(
        client,
        "/api/v1/application-auth/session/rotate",
        {"surface": surface.value},
        csrf,
    )
    assert rotation.status_code == 200
    csrf = rotation.json()["csrf_token"]

    second = _post(
        client,
        "/api/v1/application-auth/session/validate",
        {"surface": surface.value},
        csrf,
    )
    assert second.status_code == 200

    logout = _post(
        client,
        "/api/v1/application-auth/session/logout",
        {"surface": surface.value},
        csrf,
    )
    assert logout.status_code == 204

    fresh_csrf = _post(
        client,
        "/api/v1/application-auth/csrf",
        {"surface": surface.value},
    )
    assert fresh_csrf.status_code == 200
    denied = _post(
        client,
        "/api/v1/application-auth/session/validate",
        {"surface": surface.value},
        fresh_csrf.json()["csrf_token"],
    )
    assert denied.status_code == 401
    assert denied.json() == {"detail": "application_authentication_failed"}

    return evidence_nonce, {
        "csrf_issued": True,
        "session_created": True,
        "first_validation_passed": True,
        "rotation_passed": True,
        "second_validation_passed": True,
        "logout_passed": True,
        "post_logout_denied": True,
    }


def test_frozen_plan_threat_and_receipt_preserve_the_five_source_boundary():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))

    assert "frozen implementation and acceptance contract" in plan
    assert "0b3fe1f965c1171a436676762d6101818b437bae" in plan
    assert "GitHub Pages deployment" in plan
    assert "does not permit" in threat or "must not" in threat
    assert receipt["status"] == "passed"
    assert receipt["worker_dispatch_permitted"] is False
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert receipt["source_evidence"]["git_refs_and_worktree"][
        "concurrent_branding_assets_present_untracked_untouched_and_excluded"
    ]


def test_fresh_restricted_manifests_are_exact_origin_and_surface_bound():
    ids: set[str] = set()
    for surface, path in MANIFESTS.items():
        root = ElementTree.parse(path).getroot()
        addin_id = root.findtext("office:Id", namespaces=NS)
        assert addin_id and addin_id not in ids
        ids.add(addin_id)
        assert root.findtext("office:Permissions", namespaces=NS) == "Restricted"
        source = root.find("office:DefaultSettings/office:SourceLocation", NS)
        assert source is not None
        assert source.attrib["DefaultValue"] == (
            f"{DEVELOPMENT_ORIGIN}/office-cookie-compatibility/taskpane"
            f"?surface={surface.value}"
        )
        app_domain = root.findtext("office:AppDomains/office:AppDomain", namespaces=NS)
        assert app_domain == DEVELOPMENT_ORIGIN
        assert "bootstrap" not in path.read_text(encoding="utf-8").lower()
    assert ids.isdisjoint(
        {
            "c2eb45a2-9364-4e74-985e-7a3850d82751",
            "71814d1a-9a22-44cc-9d0f-c733815f73d9",
        }
    )


def test_shared_taskpane_and_postgresql_harness_have_no_forbidden_fallback():
    taskpane = SCRIPT.read_text(encoding="utf-8")
    harness = HARNESS_SCRIPT.read_text(encoding="utf-8")
    compact = (taskpane + harness).lower()
    for forbidden in (
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "document.cookie",
        "word.run",
        "getaccesstoken",
        "authorization\"",
        "bearer ",
    ):
        assert forbidden not in compact
    assert "roleScopedPostgresApplicationAuthRuntime".lower() in compact
    assert "create_application_auth_engine" in harness
    assert "PostgresTransportDenialAuditSink" in harness
    assert "include_router" not in harness
    assert issubclass(
        PostgresOfficeCookieCompatibilityHarness,
        OfficeCookieCompatibilityHarnessBase,
    )
    assert "super().__init__(" in harness


def test_live_evidence_residue_and_closeout_are_closed_and_exact():
    live = json.loads(LIVE_EVIDENCE.read_text(encoding="utf-8"))
    residue = json.loads(RESIDUE_EVIDENCE.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE_EVIDENCE.read_text(encoding="utf-8"))
    codeql = json.loads(CODEQL_READBACK.read_text(encoding="utf-8"))
    codeql_ledger = json.loads(CODEQL_LEDGER.read_text(encoding="utf-8"))
    codeql_triage = CODEQL_TRIAGE.read_text(encoding="utf-8")
    closeout = CLOSEOUT.read_text(encoding="utf-8")
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    report = COMPASS_REPORT.read_text(encoding="utf-8")

    assert live["result"] == RESULT
    assert live["passed"] is True
    assert live["database"]["row_counts"] == {
        "principal_generations": 2,
        "parent_sessions": 2,
        "surface_sessions": 4,
        "exchange_grants": 0,
        "audit_events": 16,
    }
    assert live["database"]["lifecycle_audit_event_count"] == 14
    assert live["database"]["retained_post_logout_denial_count"] == 2
    assert live["database"]["revoked_surface_session_count"] == 4
    assert live["database"]["practice_scope_exact"] is True
    assert live["database"]["raw_persisted_value_match_count"] == 0
    assert live["durable_secret_or_target_match_count"] == 0
    assert live["cleanup"]["passed"] is True
    assert all(
        live["results"][surface.value]["terminal_status"] == "passed"
        for surface in MANIFESTS
    )

    assert residue["passed"] is True
    assert set(residue["task_processes"].values()) == {False}
    assert set(residue["listeners"].values()) == {False}
    assert residue["postgresql"]["disposable_database_absent"] is True
    assert residue["postgresql"]["disposable_login_role_absent"] is True
    assert residue["postgresql"]["disposable_capability_role_absent"] is True
    assert set(residue["external_side_effects"].values()) == {0}

    assert acceptance["passed"] is True
    assert acceptance["verification"]["focused_tests"] == 5
    assert acceptance["verification"]["expanded_tests"] == 176
    assert acceptance["verification"][
        "continuity_compass_and_handover_tests"
    ] == 29
    assert acceptance["deviations"][0]["disposition"] == "paused_not_failed"
    assert acceptance["gates"]["pr71_codeql_alert_545_structural_repair"] == (
        "passed_fixed_without_dismissal"
    )
    assert codeql["alert"]["native_id"] == 545
    assert codeql["alert"]["security_severity"] is None
    assert codeql["native_readback"]["state"] == "fixed"
    assert codeql["native_readback"]["dismissed_at"] is None
    assert codeql["native_readback"]["open_pr_alert_count"] == 0
    assert set(codeql["native_mutations"].values()) == {0}
    assert codeql_ledger["verdict"] == "confirmed_quality"
    assert codeql_ledger["disposition"] == "fixed_by_fresh_codeql_analysis"
    assert "without a security-severity level" in codeql_triage
    assert "PRs 70 and 71 were not merged" in closeout
    assert "GitHub Pages" in closeout
    assert "docs/branding/raisa/" in closeout
    assert graph["graph_revision"] == 188
    assert graph["nodes"][-1]["id"] == (
        "raisa-shared-application-auth-postgresql-office-host-compatibility"
    )
    assert compass["map_revision"] == 169
    assert compass["source_graph_revision"] == 188
    assert compass["current_position"]["node_id"] == graph["nodes"][-1]["id"]
    assert "Continuity 188 / Compass 169" in report

    rendered = json.dumps(
        {"live": live, "residue": residue, "acceptance": acceptance},
        sort_keys=True,
    )
    for forbidden in (
        "postgresql://",
        "bootstrap_credential",
        "evidence_nonce",
        "Set-Cookie",
        "emr4_application_auth_login_",
        "emr4_application_auth_runtime_",
        "emr4_auth_transport_acceptance_",
    ):
        assert forbidden not in rendered


def test_two_surface_lifecycles_use_postgresql_capability_role_and_clean_up():
    harness = PostgresOfficeCookieCompatibilityHarness(output_path=None)
    try:
        assert not hasattr(harness, "store")
        assert not hasattr(harness, "auth_audit")
        assert not hasattr(harness, "denial_audit")
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

        live = harness.evidence()
        assert live["passed"] is False
        assert live["database"]["passed"] is True
        assert live["database"]["row_counts"] == {
            "principal_generations": 2,
            "parent_sessions": 2,
            "surface_sessions": 4,
            "exchange_grants": 0,
            "audit_events": 16,
        }
        assert live["database"]["role_and_pool"]["passed"] is True
        assert live["database"]["practice_scope_exact"] is True
        assert live["database"]["raw_persisted_value_match_count"] == 0
        assert live["bootstrap_registry_counts"] == {
            "available": 0,
            "reserved": 0,
            "consumed": 2,
        }

        final = harness.close()
        assert final["result"] == RESULT
        assert final["passed"] is True
        assert final["cleanup"]["passed"] is True
        assert final["durable_secret_or_target_match_count"] == 0
        assert set(final["side_effects"].values()) == {0}
        rendered = json.dumps(final, sort_keys=True)
        for forbidden in (
            "bootstrap_credential",
            "evidence_nonce",
            "Set-Cookie",
            "postgresql://",
            "emr4_application_auth_login_",
            "emr4_application_auth_runtime_",
            "emr4_auth_transport_acceptance_",
        ):
            assert forbidden not in rendered
    finally:
        harness.close()
