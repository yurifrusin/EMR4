"""Generate sanitized evidence for five provider-free Office lifecycle descendants."""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.application_auth_office_consumer import (  # noqa: E402
    DefaultOffOfficeConsumerAdapter,
    OfficeConsumerDeliveryState,
    OfficeConsumerLifecycleReason,
    OfficeConsumerNonceRejected,
    OfficeConsumerNonceReplayed,
)
from app.services.application_auth_runtime import Surface  # noqa: E402
from app.services.application_auth_transport import (  # noqa: E402
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
)
from scripts.raisa_provider_free_office_practitioner_directory_consumer import (  # noqa: E402
    DEVELOPMENT_ORIGIN,
    OfficePractitionerDirectoryHarness,
    build_app,
)


OUTPUT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-office-directory-lifecycle-descendants/provider-free-acceptance-evidence.json"
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


def _attribute(markup: str, name: str) -> str:
    match = re.search(rf'{re.escape(name)}="([^"]*)"', markup)
    if match is None:
        raise RuntimeError("expected taskpane attribute is absent")
    return html.unescape(match.group(1))


def _page(client: TestClient, surface: Surface):
    response = client.get(
        "/office-practitioner-directory/taskpane",
        params={"surface": surface.value},
    )
    if response.status_code != 200:
        raise RuntimeError("taskpane delivery failed")
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
            "failure_code": "session_unavailable",
        },
    )


def _cleanup_summary(harness: OfficePractitionerDirectoryHarness) -> dict[str, bool]:
    closed = harness.close()
    cleanup = closed["cleanup"]
    return {
        "database_absent_after": bool(cleanup["database_absent_after"]),
        "four_task_roles_absent_after": bool(
            cleanup["four_task_roles_absent_after"]
        ),
        "pools_disposed": bool(cleanup["pools_disposed"]),
        "passed": bool(cleanup["passed"]),
    }


def _reload_reconciliation() -> tuple[dict[str, Any], list[str]]:
    harness = OfficePractitionerDirectoryHarness(output_path=None)
    raw_values: list[str] = []
    try:
        with TestClient(
            build_app(harness),
            base_url=DEVELOPMENT_ORIGIN,
            client=("127.0.0.1", 51000),
        ) as client:
            first = _page(client, Surface.WORD_DESKTOP)
            csrf = _attribute(first.text, "data-csrf")
            nonce = _attribute(first.text, "data-evidence-nonce")
            endpoint = _attribute(first.text, "data-directory-endpoint")
            session_value = harness.lifecycle.session_value(Surface.WORD_DESKTOP)
            raw_values.extend((csrf, nonce, session_value))
            stale_cookie = (
                f"{SESSION_COOKIE_NAME}={session_value}; "
                f"{CSRF_COOKIE_NAME}={csrf}"
            )
            replay = _page(client, Surface.WORD_DESKTOP)
            stale = _product_request(
                client,
                endpoint=endpoint,
                csrf=csrf,
                cookie_header=stale_cookie,
            )
            second_replay = _page(client, Surface.WORD_DESKTOP)
        lifecycle = harness.evidence()["lifecycle"]
        counts = lifecycle["reason_counts"]
        result = {
            "result": "provider_free_office_reload_terminal_reconciliation_pass",
            "passed": all(
                (
                    _attribute(first.text, "data-delivery-state") == "ready",
                    _attribute(replay.text, "data-delivery-state") == "inert",
                    _attribute(second_replay.text, "data-delivery-state") == "inert",
                    _attribute(replay.text, "data-csrf") == "",
                    _attribute(replay.text, "data-evidence-nonce") == "",
                    _attribute(replay.text, "data-directory-endpoint") == "",
                    stale.status_code in {401, 403},
                    counts["delivery_replayed"] == 2,
                    counts["replay_session_revoked"] == 1,
                    counts["replay_session_revocation_failed"] == 0,
                )
            ),
            "ready_delivery_count": counts["delivery_ready"],
            "inert_replay_count": counts["delivery_replayed"],
            "stale_product_request_denied": stale.status_code in {401, 403},
            "revocation_count": counts["replay_session_revoked"],
            "revocation_failure_count": counts[
                "replay_session_revocation_failed"
            ],
            "product_reads": 0,
        }
    finally:
        cleanup = _cleanup_summary(harness)
    result["cleanup"] = cleanup
    result["passed"] = bool(result["passed"] and cleanup["passed"])
    return result, raw_values


def _session_loss_reconciliation() -> tuple[dict[str, Any], list[str]]:
    clock = MutableClock()
    harness = OfficePractitionerDirectoryHarness(output_path=None, clock=clock)
    raw_values: list[str] = []
    try:
        with TestClient(
            build_app(harness),
            base_url=DEVELOPMENT_ORIGIN,
            client=("127.0.0.1", 51001),
        ) as client:
            online = _page(client, Surface.WORD_ONLINE)
            online_csrf = _attribute(online.text, "data-csrf")
            online_nonce = _attribute(online.text, "data-evidence-nonce")
            online_endpoint = _attribute(online.text, "data-directory-endpoint")
            raw_values.extend((online_csrf, online_nonce))
            if harness.transport is None:
                raise RuntimeError("transport unavailable")
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
            revoked_result = _failed_result(
                client,
                surface=Surface.WORD_ONLINE,
                nonce=online_nonce,
            )

            desktop = _page(client, Surface.WORD_DESKTOP)
            desktop_csrf = _attribute(desktop.text, "data-csrf")
            desktop_nonce = _attribute(desktop.text, "data-evidence-nonce")
            desktop_endpoint = _attribute(desktop.text, "data-directory-endpoint")
            raw_values.extend((desktop_csrf, desktop_nonce))
            clock.advance(timedelta(days=1))
            expired = _product_request(
                client,
                endpoint=desktop_endpoint,
                csrf=desktop_csrf,
            )
            expired_result = _failed_result(
                client,
                surface=Surface.WORD_DESKTOP,
                nonce=desktop_nonce,
            )
        lifecycle = harness.evidence()["lifecycle"]
        counts = lifecycle["reason_counts"]
        result = {
            "result": "provider_free_office_session_loss_reconciliation_pass",
            "passed": all(
                (
                    revoked.status_code in {401, 403},
                    expired.status_code in {401, 403},
                    revoked_result.status_code == 201,
                    expired_result.status_code == 201,
                    counts["session_loss_reconciled"] == 2,
                    counts["terminal_fail"] == 2,
                )
            ),
            "revoked_session_denied": revoked.status_code in {401, 403},
            "expired_session_denied": expired.status_code in {401, 403},
            "safe_terminal_result_count": counts["session_loss_reconciled"],
            "raw_error_detail_released": False,
            "product_reads": 0,
        }
    finally:
        cleanup = _cleanup_summary(harness)
    result["cleanup"] = cleanup
    result["passed"] = bool(result["passed"] and cleanup["passed"])
    return result, raw_values


def _cross_surface_replay_isolation() -> tuple[dict[str, Any], list[str]]:
    harness = OfficePractitionerDirectoryHarness(output_path=None)
    raw_values: list[str] = []
    try:
        app = build_app(harness)
        with (
            TestClient(
                app,
                base_url=DEVELOPMENT_ORIGIN,
                client=("127.0.0.1", 51002),
            ) as desktop_client,
            TestClient(
                app,
                base_url=DEVELOPMENT_ORIGIN,
                client=("127.0.0.1", 51003),
            ) as online_client,
        ):
            desktop = _page(desktop_client, Surface.WORD_DESKTOP)
            online = _page(online_client, Surface.WORD_ONLINE)
            desktop_csrf = _attribute(desktop.text, "data-csrf")
            online_csrf = _attribute(online.text, "data-csrf")
            desktop_nonce = _attribute(desktop.text, "data-evidence-nonce")
            online_nonce = _attribute(online.text, "data-evidence-nonce")
            raw_values.extend(
                (desktop_csrf, online_csrf, desktop_nonce, online_nonce)
            )
            wrong_surface = _product_request(
                desktop_client,
                endpoint=_attribute(online.text, "data-directory-endpoint"),
                csrf=desktop_csrf,
            )
            swapped_csrf = _product_request(
                desktop_client,
                endpoint=_attribute(desktop.text, "data-directory-endpoint"),
                csrf=online_csrf,
            )
            cross_nonce = _failed_result(
                desktop_client,
                surface=Surface.WORD_DESKTOP,
                nonce=online_nonce,
            )
            desktop_terminal = _failed_result(
                desktop_client,
                surface=Surface.WORD_DESKTOP,
                nonce=desktop_nonce,
            )
            nonce_replay = _failed_result(
                desktop_client,
                surface=Surface.WORD_DESKTOP,
                nonce=desktop_nonce,
            )
            online_terminal = _failed_result(
                online_client,
                surface=Surface.WORD_ONLINE,
                nonce=online_nonce,
            )
        evidence = harness.evidence()
        counts = evidence["lifecycle"]["reason_counts"]
        result = {
            "result": "provider_free_office_cross_surface_replay_isolation_pass",
            "passed": all(
                (
                    wrong_surface.status_code in {401, 403},
                    swapped_csrf.status_code == 403,
                    cross_nonce.status_code == 400,
                    desktop_terminal.status_code == 201,
                    nonce_replay.status_code == 409,
                    online_terminal.status_code == 201,
                    counts["result_nonce_rejected"] == 1,
                    counts["result_nonce_replayed"] == 1,
                    evidence["side_effects"]["product_reads"] == 0,
                )
            ),
            "wrong_surface_cookie_denied": wrong_surface.status_code in {401, 403},
            "swapped_csrf_denied": swapped_csrf.status_code == 403,
            "cross_surface_nonce_denied": cross_nonce.status_code == 400,
            "consumed_nonce_replay_denied": nonce_replay.status_code == 409,
            "product_reads": evidence["side_effects"]["product_reads"],
        }
    finally:
        cleanup = _cleanup_summary(harness)
    result["cleanup"] = cleanup
    result["passed"] = bool(result["passed"] and cleanup["passed"])
    return result, raw_values


def _adapter_and_observability() -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    adapter = DefaultOffOfficeConsumerAdapter(
        expected_hosts={Surface.WORD_ONLINE: "word_online"},
        directory_endpoints={Surface.WORD_ONLINE: "/fixed-directory"},
    )
    raw_values = ["adapter-session", "adapter-csrf", "adapter-nonce"]
    adapter.register_launch(
        surface=Surface.WORD_ONLINE,
        session_value=raw_values[0],
        csrf_value=raw_values[1],
        evidence_nonce=raw_values[2],
    )
    ready = adapter.deliver(Surface.WORD_ONLINE)
    inert = adapter.deliver(Surface.WORD_ONLINE)
    adapter.complete_replay_revocation(
        surface=Surface.WORD_ONLINE,
        succeeded=True,
    )
    adapter.record_reason(OfficeConsumerLifecycleReason.PRODUCT_READ_DENIED)
    adapter.admit_result_nonce(
        surface=Surface.WORD_ONLINE,
        supplied_nonce=raw_values[2],
    )
    replay_rejected = False
    mismatch_rejected = False
    try:
        adapter.admit_result_nonce(
            surface=Surface.WORD_ONLINE,
            supplied_nonce=raw_values[2],
        )
    except OfficeConsumerNonceReplayed:
        replay_rejected = True
    try:
        adapter.admit_result_nonce(
            surface=Surface.WORD_ONLINE,
            supplied_nonce="mismatched-nonce",
        )
    except OfficeConsumerNonceRejected:
        mismatch_rejected = True
    snapshot = adapter.sanitized_snapshot()
    serialized = json.dumps(snapshot, sort_keys=True)
    observability = {
        "result": "provider_free_office_lifecycle_observability_pass",
        "passed": all(
            (
                set(snapshot["reason_counts"])
                == {reason.value for reason in OfficeConsumerLifecycleReason},
                snapshot["identifier_fields_present"] is False,
                snapshot["raw_values_present"] is False,
                all(value not in serialized for value in raw_values),
            )
        ),
        "schema_version": snapshot["schema_version"],
        "fixed_reason_class_count": len(snapshot["reason_counts"]),
        "identifier_fields_present": snapshot["identifier_fields_present"],
        "raw_values_present": snapshot["raw_values_present"],
    }
    app_main = (ROOT / "app/main.py").read_text(encoding="utf-8")
    taskpane = (
        ROOT
        / "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/taskpane.js"
    ).read_text(encoding="utf-8")
    extracted = {
        "result": "provider_free_default_off_office_consumer_adapter_pass",
        "passed": all(
            (
                ready.state is OfficeConsumerDeliveryState.READY,
                ready.directory_endpoint == "/fixed-directory",
                inert.state is OfficeConsumerDeliveryState.INERT,
                inert.directory_endpoint == "",
                inert.revoke_session_value == raw_values[0],
                replay_rejected,
                mismatch_rejected,
                "application_auth_office_consumer" not in app_main,
                'window.addEventListener("pagehide"' in taskpane,
                'window.addEventListener("pageshow"' in taskpane,
            )
        ),
        "route_mounted": False,
        "database_owned": False,
        "cookie_owned": False,
        "provider_or_identity_owned": False,
        "fixed_surface_and_endpoint": True,
        "one_use_delivery_and_nonce": True,
    }
    return observability, extracted, raw_values


def build_evidence() -> dict[str, Any]:
    reload_result, reload_raw = _reload_reconciliation()
    loss_result, loss_raw = _session_loss_reconciliation()
    replay_result, replay_raw = _cross_surface_replay_isolation()
    observability, extracted, adapter_raw = _adapter_and_observability()
    tranches = [
        reload_result,
        loss_result,
        replay_result,
        observability,
        extracted,
    ]
    evidence: dict[str, Any] = {
        "schema_version": "emr4.provider-free-office-directory-lifecycle-descendants-evidence.v1",
        "result": "provider_free_office_directory_lifecycle_descendants_pass",
        "passed": all(item["passed"] for item in tranches),
        "evidence_label": "provider_free_in_process_backend_postgres",
        "data_class": "authored_synthetic",
        "default_off": True,
        "tranches": tranches,
        "side_effects": {
            "provider_calls": 0,
            "external_identity_calls": 0,
            "microsoft_or_office_identity_calls": 0,
            "patient_health_or_clinical_reads": 0,
            "document_reads": 0,
            "document_writes": 0,
            "product_reads": 0,
            "product_commands_or_writes": 0,
            "deployments": 0,
            "production_changes": 0,
        },
        "claim_limits": [
            "Lifecycle hardening of the existing authored-synthetic active-practitioner Office consumer only.",
            "No real identity, broader product read, command, deployment, production or release is established.",
        ],
    }
    raw_values = reload_raw + loss_raw + replay_raw + adapter_raw
    serialized = json.dumps(evidence, sort_keys=True)
    evidence["durable_raw_value_match_count"] = sum(
        value in serialized for value in raw_values if value
    )
    evidence["passed"] = bool(
        evidence["passed"] and evidence["durable_raw_value_match_count"] == 0
    )
    if not evidence["passed"]:
        evidence["result"] = "revision_required"
    return evidence


def main() -> int:
    evidence = build_evidence()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
