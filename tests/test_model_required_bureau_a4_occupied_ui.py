"""Provider-free contract tests for the occupied A4 UI evidence harness."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from fastapi.testclient import TestClient

from scripts import model_required_bureau_a4_occupied_ui_acceptance as acceptance
from scripts import model_required_bureau_a4_selector_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/model_required_bureau_a4_occupied_ui_acceptance.py"


def _release() -> dict[str, object]:
    observed = datetime(2026, 8, 5, 1, 2, 3, tzinfo=timezone.utc)
    context = contracts.materialize_execution_context(
        contracts.load_object(contracts.CONTEXT_PATH), observed_at=observed
    )
    body = contracts.canonical_model_body_fixture(contracts.LANE_RAYLEEN)
    candidate = contracts.wrap_provider_body(
        contracts.LANE_RAYLEEN, body, context
    )
    proof = contracts.proofread(
        contracts.LANE_RAYLEEN,
        candidate,
        context,
        proof_time=observed + timedelta(seconds=1),
    )
    assert proof["verdict"] == "admitted"
    return proof["released"]


def test_occupied_release_endpoint_is_exact_and_no_store() -> None:
    release = _release()
    response_packet = release["response"]
    frame = response_packet["data"]["rayleenWaitingRoom"]
    app, counters = acceptance._build_app(response_packet)
    request = {
        "locationId": frame["locationId"],
        "projectionKind": "FULL_QUEUE",
        "practitionerId": None,
        "waitingAreaId": None,
        "focusAppointmentId": None,
    }
    with TestClient(app, base_url="https://127.0.0.1") as client:
        accepted = client.post("/acceptance/occupied-release", json=request)
        assert accepted.status_code == 200
        assert accepted.json() == response_packet
        assert accepted.headers["cache-control"] == "no-store"
        assert counters["release_reads"] == 1
        rejected = client.post(
            "/acceptance/occupied-release",
            json={**request, "projectionKind": "LONGEST_WAIT"},
        )
        assert rejected.status_code == 400
        assert counters["release_reads"] == 1


def test_diary_bootstrap_is_default_off_local_and_model_release_only() -> None:
    release = _release()
    app, _counters = acceptance._build_app(release["response"])
    with TestClient(app, base_url="https://127.0.0.1") as client:
        html = client.get("/diary/diary.html")
        bootstrap = client.get("/acceptance/bootstrap.js")
    assert html.status_code == 200
    assert '<script src="/acceptance/bootstrap.js"></script>' in html.text
    assert 'diary.js?v=199' in html.text
    assert bootstrap.status_code == 200
    assert "__EMR4_RAYLEEN_WAITING_ROOM__" in bootstrap.text
    assert 'fetch("/acceptance/occupied-release"' in bootstrap.text
    assert "readFixedWaitingRoom" in bootstrap.text


def test_occupied_harness_keeps_all_ordinary_diary_reads_on_loopback() -> None:
    release = _release()
    origin = "https://127.0.0.1:9443"
    app, _counters = acceptance._build_app(
        release["response"], api_origin=origin
    )
    with TestClient(app, base_url=origin) as client:
        diary_js = client.get("/diary/diary.js")
        graphql = client.post("/api/v1/graphql", json={"query": "query { x }"})
        hosting_policy = client.get("/hosting-policy.js?v=1")
        favicon = client.get("/favicon.ico")
    assert diary_js.status_code == 200
    assert f'const NGROK_URL   = "{origin}";' in diary_js.text
    assert "property-cinch-backfield.ngrok-free.dev" not in diary_js.text
    assert graphql.json() == {"data": {"practice": {"practitioners": []}}}
    assert hosting_policy.status_code == 200
    assert favicon.status_code == 204


def test_expired_model_selection_can_only_receive_freshness_revalidation() -> None:
    original = contracts.ARTIFACT_ROOT / "occupied-selector-recovery-evidence.json"
    assert original.is_file()
    observed = datetime(2026, 8, 5, 3, 4, 5, tzinfo=timezone.utc)
    with tempfile.TemporaryDirectory(
        prefix="a4-ui-revalidation-test-", dir=contracts.ARTIFACT_ROOT
    ) as directory:
        root = Path(directory)
        context_path = root / "context.json"
        evidence_path = root / "evidence.json"
        evidence = acceptance._revalidate_occupied_selection_for_ui(
            original_evidence_path=original,
            context_output_path=context_path,
            evidence_output_path=evidence_path,
            observed_at=observed,
        )
        validated, release, bound_context = acceptance._validate_occupied_evidence(
            evidence_path
        )
    assert validated == evidence
    assert bound_context == context_path.resolve()
    assert evidence["candidate_runtime_provider_call_count"] == 2
    assert evidence["provider_calls_during_revalidation"] == 0
    assert evidence["selector_still_unique_and_grounded"] is True
    assert evidence["selection_changed"] is False
    frame = release["response"]["data"]["rayleenWaitingRoom"]
    assert frame["generatedAt"] == "2026-08-05T03:04:05Z"
    assert frame["expiresAt"] == "2026-08-05T03:06:05Z"
    assert frame["projection"]["focusAppointmentId"] == (
        "a4000000-0000-4000-8000-000000000011"
    )


def test_harness_uses_real_loopback_https_without_route_interception() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert "ignore_https_errors=True" in source
    assert '"route_interception": False' in source
    assert ".route(" not in source
    assert "page.goto(" in source
    assert "sync_playwright()" in source
    assert "provider_calls_during_ui\": 0" in source
    assert "database_access_during_ui\": 0" in source
    assert "command_count\": 0" in source
    assert "write_count\": 0" in source


def test_occupied_ui_exact_evidence_label_is_frozen() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert source.count("occupied_authored_synthetic_live_local_product_read_ui") == 3
    assert "model_required_bureau_a4_occupied_product_read_ui_pass" in source
    assert "proofreader_admitted_display_projection" in source
