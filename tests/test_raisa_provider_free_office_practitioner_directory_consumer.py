from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from fastapi.testclient import TestClient

from app.services.application_auth_runtime import Surface
from scripts.raisa_provider_free_office_practitioner_directory_consumer import (
    DEVELOPMENT_ORIGIN,
    LOCAL_BROWSER_PREVIEW_ORIGIN,
    RESULT,
    OfficePractitionerDirectoryHarness,
    build_app,
)


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-office-practitioner-directory-consumer"
)
PLAN = ROOT / "docs/raisa-provider-free-office-practitioner-directory-consumer-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-office-practitioner-directory-consumer-design.md"
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-office-practitioner-directory-consumer-threat-model-delta.md"
)
RECEIPT = (
    ROOT
    / "orchestration/agent_inbox/codex/raisa-provider-free-office-practitioner-directory-consumer-rehydration-receipt.json"
)
SCRIPT = CONTINUITY / "taskpane.js"
STYLE = CONTINUITY / "taskpane.css"
MANIFESTS = {
    Surface.WORD_DESKTOP: CONTINUITY / "word-desktop-manifest.xml",
    Surface.WORD_ONLINE: CONTINUITY / "word-online-manifest.xml",
}
NS = {"office": "http://schemas.microsoft.com/office/appforoffice/1.1"}
PROXY_HEADERS = {
    "Origin": DEVELOPMENT_ORIGIN,
    "X-Forwarded-For": "203.0.113.42",
    "X-Forwarded-Proto": "https",
}
QUERY = """
query Directory($activeOnly: Boolean!, $limit: Int!, $offset: Int!) {
  practice {
    practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) {
      id
      displayName
      roleLabel
      active
      defaultLocation { id name }
    }
  }
}
"""


def _attribute(markup: str, name: str) -> str:
    match = re.search(rf'{re.escape(name)}="([^"]*)"', markup)
    assert match is not None
    return html.unescape(match.group(1))


def _exercise_surface(
    client: TestClient,
    surface: Surface,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    page = client.get(
        "/office-practitioner-directory/taskpane",
        params={"surface": surface.value},
    )
    assert page.status_code == 200
    assert page.headers["cache-control"] == "no-store"
    taskpane_csp = page.headers["content-security-policy"]
    assert "frame-ancestors" in taskpane_csp
    assert "https://*.officeapps.live.com" in taskpane_csp
    assert "https://onedrive.live.com" in taskpane_csp
    assert all(
        marker in page.headers["set-cookie"].lower()
        for marker in ("secure", "httponly", "samesite=none", "partitioned")
    )
    csrf = _attribute(page.text, "data-csrf")
    nonce = _attribute(page.text, "data-evidence-nonce")
    endpoint = _attribute(page.text, "data-directory-endpoint")
    assert csrf.startswith("csrf.")
    assert len(nonce) >= 43
    reload_page = client.get(
        "/office-practitioner-directory/taskpane",
        params={"surface": surface.value},
    )
    assert _attribute(reload_page.text, "data-csrf") == ""
    assert _attribute(reload_page.text, "data-evidence-nonce") == ""

    response = client.post(
        endpoint,
        json={
            "query": QUERY,
            "variables": {"activeOnly": True, "limit": 200, "offset": 0},
            "operationName": "Directory",
        },
        headers={"Origin": DEVELOPMENT_ORIGIN, "X-EMR4-CSRF": csrf},
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert set(body) == {"data"}
    rows = body["data"]["practice"]["practitioners"]
    assert len(rows) == 2
    assert all(
        set(row)
        == {"id", "displayName", "roleLabel", "active", "defaultLocation"}
        and row["active"] is True
        for row in rows
    )
    assert not any("Inactive" in row["displayName"] for row in rows)
    rendered_values = json.dumps(rows)
    assert all(
        forbidden not in rendered_values
        for forbidden in (
            "provider_number",
            "prescriber_number",
            "ahpra_number",
            "hpi_i",
            "email",
        )
    )

    logout = client.post(
        "/api/v1/application-auth/session/logout",
        json={"surface": surface.value},
        headers={**PROXY_HEADERS, "X-EMR4-CSRF": csrf},
    )
    assert logout.status_code == 204
    host_class = (
        "installed_word"
        if surface is Surface.WORD_DESKTOP
        else "word_online"
    )
    result = client.post(
        "/office-practitioner-directory/result",
        headers={"Origin": DEVELOPMENT_ORIGIN},
        json={
            "evidence_nonce": nonce,
            "surface": surface.value,
            "host_class": host_class,
            "terminal_status": "passed",
            "directory_read_passed": True,
            "exact_projection_passed": True,
            "active_practitioner_count": 2,
            "logout_passed": True,
            "result_submitted": True,
            "failure_code": "none",
        },
    )
    assert result.status_code == 201
    assert "evidence_nonce" not in result.text
    assert result.json()["post_logout_session_denied"] is True
    return rows, result.json()


def test_plan_design_threat_and_five_source_receipt_are_frozen():
    assert PLAN.is_file() and DESIGN.is_file() and THREAT.is_file()
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    plan = PLAN.read_text(encoding="utf-8")
    assert "default-off" in plan
    assert "app.main" in plan
    assert "docs/branding/" in plan


def test_manifests_are_fresh_restricted_and_surface_bound():
    ids: set[str] = set()
    for surface, path in MANIFESTS.items():
        root = ET.parse(path).getroot()
        manifest_id = root.find("office:Id", NS)
        permissions = root.find("office:Permissions", NS)
        source = root.find("office:DefaultSettings/office:SourceLocation", NS)
        assert manifest_id is not None and manifest_id.text
        assert manifest_id.text not in ids
        ids.add(manifest_id.text)
        assert permissions is not None and permissions.text == "Restricted"
        assert source is not None
        assert source.attrib["DefaultValue"] == (
            f"{DEVELOPMENT_ORIGIN}/office-practitioner-directory/taskpane"
            f"?surface={surface.value}"
        )
        text_value = path.read_text(encoding="utf-8")
        assert "/office-practitioner-directory/" in text_value
        assert all(
            forbidden not in text_value
            for forbidden in ("bootstrap", "token=", "session=", "patient")
        )


def test_taskpane_source_is_exact_fail_closed_and_document_free():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'operationName: "Directory"' in source
    assert "activeOnly: true, limit: 200, offset: 0" in source
    assert 'credentials: "include"' in source
    assert 'headers["X-EMR4-CSRF"]' in source
    assert "ROW_KEYS" in source and "LOCATION_KEYS" in source
    assert "Office.onReady" in source
    assert "textContent" in source
    assert "replaceChildren" in source
    assert "No fallback or partial result was used" in source
    assert all(
        forbidden not in source
        for forbidden in (
            "Word.run",
            "Office.context.document",
            "localStorage",
            "sessionStorage",
            "indexedDB",
            "document.cookie",
            "Authorization",
            "patient",
            "clinical",
        )
    )
    style = STYLE.read_text(encoding="utf-8")
    assert "button:focus-visible" in style
    assert "@media (max-width: 260px)" in style
    assert "prefers-reduced-motion" in style


def test_local_browser_preview_uses_direct_loopback_transport_admission():
    source = (
        ROOT / "scripts/raisa_provider_free_office_practitioner_directory_consumer.py"
    ).read_text(encoding="utf-8")
    assert LOCAL_BROWSER_PREVIEW_ORIGIN == "https://localhost:8001"
    assert "if self.allow_local_browser_preview" in source
    assert 'else ["127.0.0.0/8", "::1/128"]' in source
    assert '"route_intercepted_browser"' in source
    assert "proxy_headers=False" in source


def test_two_surface_directory_reads_audit_logout_and_clean_up():
    harness = OfficePractitionerDirectoryHarness(output_path=None)
    try:
        with TestClient(
            build_app(harness),
            base_url=DEVELOPMENT_ORIGIN,
            client=("127.0.0.1", 50000),
        ) as client:
            for size in (16, 32, 64, 80):
                icon = client.get(
                    f"/office-practitioner-directory/icon/{size}.png"
                )
                assert icon.status_code == 200
                assert icon.headers["content-type"] == "image/png"
                assert icon.headers["cache-control"] == "no-store"
            assert (
                client.get("/office-practitioner-directory/icon/48.png").status_code
                == 404
            )
            surfaces = {
                surface.value: _exercise_surface(client, surface)
                for surface in (Surface.WORD_DESKTOP, Surface.WORD_ONLINE)
            }
        live = harness.evidence()
        assert live["passed"] is False
        assert live["database"] == {
            "fresh_owner_readback": True,
            "authorization_allowed_audit_count": 2,
            "revoked_surface_session_count": 2,
            "raw_session_or_csrf_match_count": 0,
            "target_or_product_identifier_recorded": False,
            "passed": True,
        }
        assert live["role_probes"]["passed"] is True
        assert live["side_effects"]["product_reads"] == 2
        assert set(surfaces) == {"word_desktop", "word_online"}
    finally:
        final = harness.close()

    assert final["result"] == RESULT
    assert final["passed"] is True
    assert final["cleanup"] == {
        "database_absent_after": True,
        "four_task_roles_absent_after": True,
        "pools_disposed": True,
        "passed": True,
    }
    assert final["durable_secret_or_target_match_count"] == 0
    assert final["side_effects"] == {
        "provider_calls": 0,
        "external_identity_calls": 0,
        "microsoft_or_office_identity_calls": 0,
        "product_reads": 2,
        "patient_health_or_clinical_reads": 0,
        "document_reads": 0,
        "document_writes": 0,
        "product_commands_or_writes": 0,
        "deployments": 0,
        "production_changes": 0,
    }
