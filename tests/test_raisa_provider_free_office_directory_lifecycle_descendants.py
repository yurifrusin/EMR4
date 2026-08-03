from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.services.application_auth_office_consumer import (
    DefaultOffOfficeConsumerAdapter,
    OfficeConsumerDeliveryState,
    OfficeConsumerLifecycleReason,
    OfficeConsumerNonceRejected,
    OfficeConsumerNonceReplayed,
)
from app.services.application_auth_runtime import Surface
from app.services.application_auth_transport import CSRF_COOKIE_NAME, SESSION_COOKIE_NAME
from scripts.raisa_provider_free_office_practitioner_directory_consumer import (
    DEVELOPMENT_ORIGIN,
    OfficePractitionerDirectoryHarness,
    build_app,
)


ROOT = Path(__file__).resolve().parents[1]
TASKPANE = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/taskpane.js"
)
EVIDENCE = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-office-directory-lifecycle-descendants/provider-free-acceptance-evidence.json"
)
PLAN_SLUGS = (
    "office-reload-terminal-reconciliation",
    "office-session-loss-reconciliation",
    "office-cross-surface-replay-isolation",
    "office-lifecycle-observability",
    "default-off-office-consumer-adapter",
)
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


class MutableClock:
    def __init__(self) -> None:
        self.value = datetime.now(timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, delta: timedelta) -> None:
        self.value += delta


def test_five_descendant_plans_closeouts_threat_and_evidence_are_frozen():
    for slug in PLAN_SLUGS:
        assert (ROOT / f"docs/raisa-provider-free-{slug}-plan.md").is_file()
        assert (ROOT / f"docs/raisa-provider-free-{slug}-closeout.md").is_file()
    threat = (
        ROOT
        / "docs/security/raisa-provider-free-office-directory-lifecycle-descendants-threat-model-delta.md"
    )
    assert threat.is_file()
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["result"] == (
        "provider_free_office_directory_lifecycle_descendants_pass"
    )
    assert evidence["passed"] is True
    assert evidence["evidence_label"] == (
        "provider_free_in_process_backend_postgres"
    )
    assert evidence["durable_raw_value_match_count"] == 0
    assert len(evidence["tranches"]) == 5
    assert all(item["passed"] for item in evidence["tranches"])
    assert evidence["side_effects"] == {
        "deployments": 0,
        "document_reads": 0,
        "document_writes": 0,
        "external_identity_calls": 0,
        "microsoft_or_office_identity_calls": 0,
        "patient_health_or_clinical_reads": 0,
        "product_commands_or_writes": 0,
        "product_reads": 0,
        "production_changes": 0,
        "provider_calls": 0,
    }
    for name in ("postcompaction", "preacceptance", "precommit"):
        receipt = json.loads(
            (
                ROOT
                / f"orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-{name}-receipt.json"
            ).read_text(encoding="utf-8")
        )
        assert receipt["status"] == "passed"
        assert receipt["rehydrated_from_receipt"] is True
        assert receipt["rehydration_sources"] == [
            "live_handover_current_baton",
            "current_authority_allocation",
            "active_plan_and_acceptance",
            "protected_evidence_boundaries",
            "git_refs_and_worktree",
        ]


def _attribute(markup: str, name: str) -> str:
    match = re.search(rf'{re.escape(name)}="([^"]*)"', markup)
    assert match is not None
    return html.unescape(match.group(1))


def _page(client: TestClient, surface: Surface):
    response = client.get(
        "/office-practitioner-directory/taskpane",
        params={"surface": surface.value},
    )
    assert response.status_code == 200
    return response


def _product_request(
    client: TestClient,
    *,
    endpoint: str,
    csrf: str,
    cookie_header: str | None = None,
):
    headers = {"Origin": DEVELOPMENT_ORIGIN, "X-EMR4-CSRF": csrf}
    if cookie_header is not None:
        headers["Cookie"] = cookie_header
    return client.post(
        endpoint,
        json={
            "query": QUERY,
            "variables": {"activeOnly": True, "limit": 200, "offset": 0},
            "operationName": "Directory",
        },
        headers=headers,
    )


def _failed_result(
    client: TestClient,
    *,
    surface: Surface,
    nonce: str,
    failure_code: str = "session_unavailable",
):
    return client.post(
        "/office-practitioner-directory/result",
        headers={"Origin": DEVELOPMENT_ORIGIN},
        json={
            "evidence_nonce": nonce,
            "surface": surface.value,
            "host_class": (
                "installed_word"
                if surface is Surface.WORD_DESKTOP
                else "word_online"
            ),
            "terminal_status": "failed",
            "directory_read_passed": False,
            "exact_projection_passed": False,
            "active_practitioner_count": 0,
            "logout_passed": False,
            "result_submitted": True,
            "failure_code": failure_code,
        },
    )


def test_reload_is_explicitly_inert_revokes_stale_dom_and_cannot_retry():
    harness = OfficePractitionerDirectoryHarness(output_path=None)
    try:
        app = build_app(harness)
        with TestClient(
            app,
            base_url=DEVELOPMENT_ORIGIN,
            client=("127.0.0.1", 50000),
        ) as client:
            first = _page(client, Surface.WORD_DESKTOP)
            assert _attribute(first.text, "data-delivery-state") == "ready"
            csrf = _attribute(first.text, "data-csrf")
            endpoint = _attribute(first.text, "data-directory-endpoint")
            session_value = harness.lifecycle.session_value(Surface.WORD_DESKTOP)
            stale_cookie = (
                f"{SESSION_COOKIE_NAME}={session_value}; "
                f"{CSRF_COOKIE_NAME}={csrf}"
            )

            reload_page = _page(client, Surface.WORD_DESKTOP)
            assert _attribute(reload_page.text, "data-delivery-state") == "inert"
            assert _attribute(reload_page.text, "data-csrf") == ""
            assert _attribute(reload_page.text, "data-evidence-nonce") == ""
            assert _attribute(reload_page.text, "data-directory-endpoint") == ""
            assert "Launch consumed" in reload_page.text
            assert "Max-Age=0" in reload_page.headers["set-cookie"]

            stale = _product_request(
                client,
                endpoint=endpoint,
                csrf=csrf,
                cookie_header=stale_cookie,
            )
            assert stale.status_code in {401, 403}

            replay_page = _page(client, Surface.WORD_DESKTOP)
            assert _attribute(replay_page.text, "data-delivery-state") == "inert"

        counts = harness.evidence()["lifecycle"]["reason_counts"]
        assert counts["delivery_ready"] == 1
        assert counts["delivery_replayed"] == 2
        assert counts["replay_session_revoked"] == 1
        assert counts["replay_session_revocation_failed"] == 0
        assert counts["product_read_denied"] == 1
        assert harness.evidence()["side_effects"]["product_reads"] == 0
    finally:
        closed = harness.close()
    assert closed["cleanup"]["passed"] is True


def test_expired_and_revoked_sessions_share_one_safe_terminal_ui_contract():
    clock = MutableClock()
    harness = OfficePractitionerDirectoryHarness(output_path=None, clock=clock)
    try:
        with TestClient(
            build_app(harness),
            base_url=DEVELOPMENT_ORIGIN,
            client=("127.0.0.1", 50000),
        ) as client:
            online = _page(client, Surface.WORD_ONLINE)
            online_csrf = _attribute(online.text, "data-csrf")
            online_nonce = _attribute(online.text, "data-evidence-nonce")
            online_endpoint = _attribute(online.text, "data-directory-endpoint")
            assert harness.transport is not None
            harness.transport.logout(
                surface_session_value=harness.lifecycle.session_value(
                    Surface.WORD_ONLINE
                ),
                correlation_id="correlation-lifecycle-revoked-synthetic",
            )
            revoked = _product_request(
                client,
                endpoint=online_endpoint,
                csrf=online_csrf,
            )
            assert revoked.status_code in {401, 403}
            revoked_result = _failed_result(
                client,
                surface=Surface.WORD_ONLINE,
                nonce=online_nonce,
            )
            assert revoked_result.status_code == 201

            desktop = _page(client, Surface.WORD_DESKTOP)
            desktop_csrf = _attribute(desktop.text, "data-csrf")
            desktop_nonce = _attribute(desktop.text, "data-evidence-nonce")
            desktop_endpoint = _attribute(desktop.text, "data-directory-endpoint")
            clock.advance(timedelta(days=1))
            expired = _product_request(
                client,
                endpoint=desktop_endpoint,
                csrf=desktop_csrf,
            )
            assert expired.status_code in {401, 403}
            expired_result = _failed_result(
                client,
                surface=Surface.WORD_DESKTOP,
                nonce=desktop_nonce,
            )
            assert expired_result.status_code == 201
            assert expired_result.json()["failure_code"] == "session_unavailable"

        counts = harness.evidence()["lifecycle"]["reason_counts"]
        assert counts["session_loss_reconciled"] == 2
        assert counts["terminal_fail"] == 2
        assert counts["product_read_denied"] == 2
        source = TASKPANE.read_text(encoding="utf-8")
        assert 'response.status === 401 || response.status === 403' in source
        assert "This application session has ended." in source
        assert "No fallback or partial result was used." in source
    finally:
        closed = harness.close()
    assert closed["cleanup"]["passed"] is True


def test_cookie_csrf_surface_and_result_nonce_replay_matrix_fails_closed():
    harness = OfficePractitionerDirectoryHarness(output_path=None)
    try:
        app = build_app(harness)
        with (
            TestClient(
                app,
                base_url=DEVELOPMENT_ORIGIN,
                client=("127.0.0.1", 50000),
            ) as desktop_client,
            TestClient(
                app,
                base_url=DEVELOPMENT_ORIGIN,
                client=("127.0.0.1", 50001),
            ) as online_client,
        ):
            desktop = _page(desktop_client, Surface.WORD_DESKTOP)
            online = _page(online_client, Surface.WORD_ONLINE)
            desktop_csrf = _attribute(desktop.text, "data-csrf")
            online_csrf = _attribute(online.text, "data-csrf")
            desktop_nonce = _attribute(desktop.text, "data-evidence-nonce")
            online_nonce = _attribute(online.text, "data-evidence-nonce")
            desktop_endpoint = _attribute(desktop.text, "data-directory-endpoint")
            online_endpoint = _attribute(online.text, "data-directory-endpoint")

            wrong_surface = _product_request(
                desktop_client,
                endpoint=online_endpoint,
                csrf=desktop_csrf,
            )
            assert wrong_surface.status_code in {401, 403}
            swapped_csrf = _product_request(
                desktop_client,
                endpoint=desktop_endpoint,
                csrf=online_csrf,
            )
            assert swapped_csrf.status_code == 403

            cross_nonce = _failed_result(
                desktop_client,
                surface=Surface.WORD_DESKTOP,
                nonce=online_nonce,
            )
            assert cross_nonce.status_code == 400
            desktop_terminal = _failed_result(
                desktop_client,
                surface=Surface.WORD_DESKTOP,
                nonce=desktop_nonce,
            )
            assert desktop_terminal.status_code == 201
            nonce_replay = _failed_result(
                desktop_client,
                surface=Surface.WORD_DESKTOP,
                nonce=desktop_nonce,
            )
            assert nonce_replay.status_code == 409
            online_terminal = _failed_result(
                online_client,
                surface=Surface.WORD_ONLINE,
                nonce=online_nonce,
            )
            assert online_terminal.status_code == 201

        evidence = harness.evidence()
        counts = evidence["lifecycle"]["reason_counts"]
        assert counts["product_read_denied"] == 2
        assert counts["result_nonce_rejected"] == 1
        assert counts["result_nonce_replayed"] == 1
        assert evidence["side_effects"]["product_reads"] == 0
        assert evidence["durable_secret_or_target_match_count"] == 0
    finally:
        closed = harness.close()
    assert closed["cleanup"]["passed"] is True


def test_lifecycle_observability_is_closed_sanitized_and_reason_bounded():
    adapter = DefaultOffOfficeConsumerAdapter(
        expected_hosts={Surface.WORD_DESKTOP: "installed_word"},
        directory_endpoints={Surface.WORD_DESKTOP: "/fixed"},
    )
    raw_values = ("session-secret", "csrf-secret", "nonce-secret")
    adapter.register_launch(
        surface=Surface.WORD_DESKTOP,
        session_value=raw_values[0],
        csrf_value=raw_values[1],
        evidence_nonce=raw_values[2],
    )
    adapter.deliver(Surface.WORD_DESKTOP)
    adapter.record_reason(OfficeConsumerLifecycleReason.PRODUCT_READ_DENIED)
    snapshot = adapter.sanitized_snapshot()
    assert snapshot["schema_version"] == "raisa.office_consumer_lifecycle.v1"
    assert set(snapshot["reason_counts"]) == {
        reason.value for reason in OfficeConsumerLifecycleReason
    }
    assert snapshot["identifier_fields_present"] is False
    assert snapshot["raw_values_present"] is False
    serialized = json.dumps(snapshot, sort_keys=True)
    assert all(value not in serialized for value in raw_values)
    assert all(
        forbidden not in serialized
        for forbidden in ("correlation", "principal", "practice", "cookie", "csrf")
    )


def test_default_off_adapter_is_one_use_surface_fixed_and_unmounted():
    adapter = DefaultOffOfficeConsumerAdapter(
        expected_hosts={Surface.WORD_ONLINE: "word_online"},
        directory_endpoints={Surface.WORD_ONLINE: "/fixed-directory"},
    )
    adapter.register_launch(
        surface=Surface.WORD_ONLINE,
        session_value="opaque-session",
        csrf_value="opaque-csrf",
        evidence_nonce="opaque-nonce",
    )
    ready = adapter.deliver(Surface.WORD_ONLINE)
    assert ready.state is OfficeConsumerDeliveryState.READY
    assert ready.expected_host == "word_online"
    assert ready.directory_endpoint == "/fixed-directory"
    assert ready.revoke_session_value == ""
    inert = adapter.deliver(Surface.WORD_ONLINE)
    assert inert.state is OfficeConsumerDeliveryState.INERT
    assert inert.directory_endpoint == ""
    assert inert.csrf_value == ""
    assert inert.evidence_nonce == ""
    assert inert.revoke_session_value == "opaque-session"
    adapter.complete_replay_revocation(
        surface=Surface.WORD_ONLINE,
        succeeded=False,
    )
    retry_revocation = adapter.deliver(Surface.WORD_ONLINE)
    assert retry_revocation.revoke_session_value == "opaque-session"
    adapter.complete_replay_revocation(
        surface=Surface.WORD_ONLINE,
        succeeded=True,
    )
    settled_replay = adapter.deliver(Surface.WORD_ONLINE)
    assert settled_replay.revoke_session_value == ""
    adapter.admit_result_nonce(
        surface=Surface.WORD_ONLINE,
        supplied_nonce="opaque-nonce",
    )
    with pytest.raises(OfficeConsumerNonceReplayed):
        adapter.admit_result_nonce(
            surface=Surface.WORD_ONLINE,
            supplied_nonce="opaque-nonce",
        )
    with pytest.raises(OfficeConsumerNonceRejected):
        adapter.admit_result_nonce(
            surface=Surface.WORD_ONLINE,
            supplied_nonce="wrong-nonce",
        )

    app_main = (ROOT / "app/main.py").read_text(encoding="utf-8")
    assert "application_auth_office_consumer" not in app_main
    taskpane = TASKPANE.read_text(encoding="utf-8")
    assert 'button.addEventListener("click", run, { once: true })' in taskpane
    assert 'window.addEventListener("pagehide"' in taskpane
    assert 'window.addEventListener("pageshow"' in taskpane
    assert "if (terminal || inFlight || !officeReady) return" in taskpane
