#!/usr/bin/env python3
"""Render one proofread occupied A4 selector release in the real Diary UI."""

from __future__ import annotations

import argparse
import base64
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from playwright.sync_api import sync_playwright
import uvicorn

from scripts import model_required_bureau_a4_selector_contracts as contracts
DIARY_DIR = ROOT / "docs/diary"
IMAGES_DIR = ROOT / "docs/images"
DEFAULT_OCCUPIED_EVIDENCE = (
    contracts.ARTIFACT_ROOT / "occupied-selector-evidence.json"
)
DEFAULT_OUTPUT = (
    contracts.ARTIFACT_ROOT / "occupied-ui-browser-evidence.json"
)
DEFAULT_SCREENSHOT = (
    contracts.ARTIFACT_ROOT / "occupied-model-selected-projection.png"
)
HOST = "127.0.0.1"


class AcceptanceError(RuntimeError):
    """A fail-closed occupied UI acceptance result."""


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AcceptanceError("artifact_unreadable") from error
    if not isinstance(value, dict):
        raise AcceptanceError("artifact_object_required")
    return value


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence_hash_valid(value: dict[str, Any]) -> bool:
    expected = value.get("evidence_hash")
    material = {key: item for key, item in value.items() if key != "evidence_hash"}
    return expected == contracts.prefixed_sha256(material)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((HOST, 0))
        return int(probe.getsockname()[1])


def _jwt() -> str:
    def encoded(value: dict[str, Any]) -> str:
        return base64.urlsafe_b64encode(
            json.dumps(value, separators=(",", ":")).encode("utf-8")
        ).decode("ascii").rstrip("=")

    return ".".join(
        (
            encoded({"alg": "none", "typ": "JWT"}),
            encoded(
                {
                    "sub": "a4-occupied-authored-synthetic-receptionist",
                    "role": "Receptionist",
                    "exp": 4102444800,
                    "data_class": "authored_synthetic",
                }
            ),
            "authored-synthetic",
        )
    )


def _certificate(directory: Path) -> tuple[Path, Path]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, HOST)]
    )
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName(
                [x509.IPAddress(ipaddress.ip_address(HOST))]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    cert_path = directory / "cert.pem"
    key_path = directory / "key.pem"
    cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return cert_path, key_path


def _validate_occupied_evidence(
    path: Path,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    evidence = _load_object(path)
    is_revalidation = evidence.get("result") == (
        "model_required_bureau_a4_occupied_selector_ui_revalidation_pass"
    )
    if (
        not _evidence_hash_valid(evidence)
        or (
            evidence.get("result")
            != "model_required_bureau_a4_occupied_selector_pass"
            and not is_revalidation
        )
        or evidence.get("evidence_label")
        != "occupied_authored_synthetic_live_local_product_read_ui"
        or evidence.get("selector_admitted") is not True
        or evidence.get("candidate_runtime_provider_call_count") not in {1, 2}
        or evidence.get("patient_or_clinical_data_count") != 0
        or evidence.get("command_count") != 0
        or evidence.get("write_count") != 0
        or evidence.get("provider_tool_call_count") != 0
        or evidence.get("fallback_count") != 0
        or evidence.get("raw_prompt_retained") is not False
        or evidence.get("raw_provider_response_retained") is not False
    ):
        raise AcceptanceError("occupied_selector_evidence_invalid")
    if is_revalidation:
        release = evidence.get("ui_release")
        original_value = evidence.get("original_occupied_selector_evidence_path")
        if not isinstance(original_value, str):
            raise AcceptanceError("occupied_revalidation_lineage_missing")
        original_path = (ROOT / original_value).resolve()
        expected_original = (
            contracts.ARTIFACT_ROOT / "occupied-selector-recovery-evidence.json"
        ).resolve()
        if original_path != expected_original or not original_path.is_file():
            raise AcceptanceError("occupied_revalidation_lineage_invalid")
        original = _load_object(original_path)
        original_results = original.get("lane_results")
        original_attempt = (
            original_results[-1]
            if isinstance(original_results, list) and original_results
            else None
        )
        original_release = (
            original_attempt.get("release")
            if isinstance(original_attempt, dict)
            else None
        )
        if (
            not _evidence_hash_valid(original)
            or original.get("result")
            != "model_required_bureau_a4_occupied_selector_pass"
            or original.get("candidate_runtime_provider_call_count") != 2
            or not isinstance(original_release, dict)
            or original_attempt.get("proofreader_verdict") != "admitted"
            or evidence.get("original_occupied_selector_evidence_hash")
            != _file_hash(original_path)
            or evidence.get("original_attempt_evidence_hash")
            != original_attempt.get("evidence_hash")
            or evidence.get("original_release_hash")
            != contracts.prefixed_sha256(original_release)
            or evidence.get("provider_calls_during_revalidation") != 0
            or evidence.get("selection_changed") is not False
            or evidence.get("selector_still_unique_and_grounded") is not True
        ):
            raise AcceptanceError("occupied_revalidation_lineage_invalid")
    else:
        lane_results = evidence.get("lane_results")
        if not isinstance(lane_results, list) or not lane_results:
            raise AcceptanceError("occupied_lane_result_missing")
        attempt = lane_results[-1]
        release = attempt.get("release") if isinstance(attempt, dict) else None
    if (
        not isinstance(release, dict)
        or release.get("status") != "display_projection_only"
        or release.get("evidence_mode")
        != "proofreader_admitted_display_projection"
    ):
        raise AcceptanceError("occupied_release_not_admitted")
    context_value = evidence.get("execution_context_path")
    if not isinstance(context_value, str):
        raise AcceptanceError("execution_context_path_missing")
    context_path = (ROOT / context_value).resolve()
    try:
        context_path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise AcceptanceError("execution_context_path_outside_repository") from error
    if (
        not context_path.is_file()
        or evidence.get("execution_context_hash") != _file_hash(context_path)
        or evidence.get("execution_context_materialized_fresh") is not True
    ):
        raise AcceptanceError("execution_context_binding_invalid")
    return evidence, release, context_path


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _revalidate_occupied_selection_for_ui(
    *,
    original_evidence_path: Path,
    context_output_path: Path,
    evidence_output_path: Path,
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    if context_output_path.exists() or evidence_output_path.exists():
        raise AcceptanceError("occupied_revalidation_output_already_exists")
    original, original_release, _original_context_path = (
        _validate_occupied_evidence(original_evidence_path)
    )
    original_results = original["lane_results"]
    original_attempt = original_results[-1]
    now = observed_at or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise AcceptanceError("occupied_revalidation_time_timezone_required")
    now = now.astimezone(timezone.utc)
    fresh_context = contracts.materialize_execution_context(
        contracts.load_object(
            contracts.ARTIFACT_ROOT / "authored-synthetic-selector-context.json"
        ),
        observed_at=now,
    )
    fresh_frame = fresh_context["source_response"]["data"]["rayleenWaitingRoom"]
    elapsed_by_id = {
        item["appointmentId"]: item["integerValue"]
        for item in fresh_frame["derivedSignals"]
        if item["kind"] == "elapsed_wait_minutes"
        and type(item["integerValue"]) is int
    }
    eligible = [
        fact
        for fact in fresh_frame["backendFacts"]
        if fact["status"] == "arrived"
        and fact["appointmentId"] in elapsed_by_id
    ]
    if not eligible:
        raise AcceptanceError("occupied_revalidation_eligible_fact_missing")
    maximum = max(elapsed_by_id[fact["appointmentId"]] for fact in eligible)
    longest = [
        fact
        for fact in eligible
        if elapsed_by_id[fact["appointmentId"]] == maximum
    ]
    original_frame = original_release["response"]["data"]["rayleenWaitingRoom"]
    original_projection = original_frame["projection"]
    if (
        len(longest) != 1
        or original_projection.get("selectedCount") != 1
        or len(original_frame.get("backendFacts", [])) != 1
        or original_projection.get("focusAppointmentId")
        != longest[0]["appointmentId"]
        or original_projection.get("practitionerId")
        != longest[0]["practitionerId"]
        or original_projection.get("waitingAreaId")
        != longest[0]["waitingAreaId"]
        or original_frame["backendFacts"][0]["appointmentId"]
        != longest[0]["appointmentId"]
    ):
        raise AcceptanceError("occupied_revalidation_selection_changed")
    focus_id = longest[0]["appointmentId"]
    refreshed_response = deepcopy(fresh_context["source_response"])
    refreshed_frame = refreshed_response["data"]["rayleenWaitingRoom"]
    refreshed_frame["backendFacts"] = [
        item for item in refreshed_frame["backendFacts"]
        if item["appointmentId"] == focus_id
    ]
    refreshed_frame["derivedSignals"] = [
        item for item in refreshed_frame["derivedSignals"]
        if item["appointmentId"] == focus_id
    ]
    refreshed_frame["projection"] = deepcopy(original_projection)
    ui_release = deepcopy(original_release)
    ui_release["response"] = refreshed_response
    _write_json(context_output_path, fresh_context)
    relative_original = original_evidence_path.resolve().relative_to(ROOT.resolve())
    relative_context = context_output_path.resolve().relative_to(ROOT.resolve())
    evidence = {
        "schema_version": (
            "emr4.model_required_bureau_a4.occupied_ui_revalidation.v1"
        ),
        "result": (
            "model_required_bureau_a4_occupied_selector_ui_revalidation_pass"
        ),
        "evidence_label": "occupied_authored_synthetic_live_local_product_read_ui",
        "selector_admitted": True,
        "candidate_runtime_provider_call_count": 2,
        "provider_calls_during_revalidation": 0,
        "original_occupied_selector_evidence_path": relative_original.as_posix(),
        "original_occupied_selector_evidence_hash": _file_hash(
            original_evidence_path
        ),
        "original_attempt_evidence_hash": original_attempt["evidence_hash"],
        "original_release_hash": contracts.prefixed_sha256(original_release),
        "execution_context_path": relative_context.as_posix(),
        "execution_context_hash": _file_hash(context_output_path),
        "execution_context_materialized_fresh": True,
        "selector_still_unique_and_grounded": True,
        "selection_changed": False,
        "ui_release": ui_release,
        "patient_or_clinical_data_count": 0,
        "database_access_count": 0,
        "command_count": 0,
        "write_count": 0,
        "actuator_count": 0,
        "provider_tool_call_count": 0,
        "fallback_count": 0,
        "cloud_or_iam_mutation_count": 0,
        "deployment_count": 0,
        "protected_ref_movement_count": 0,
        "raw_prompt_retained": False,
        "raw_provider_response_retained": False,
        "credential_or_token_retained": False,
    }
    evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
    _write_json(evidence_output_path, evidence)
    return evidence


def _build_app(
    response_packet: dict[str, Any], *, api_origin: str | None = None
) -> tuple[FastAPI, dict[str, int]]:
    frame = response_packet["data"]["rayleenWaitingRoom"]
    location_id = frame["locationId"]
    practice_id = frame["practiceId"]
    counters = {"release_reads": 0}
    app = FastAPI()

    @app.get("/diary/diary.html", response_class=HTMLResponse)
    def diary_html() -> HTMLResponse:
        html = (DIARY_DIR / "diary.html").read_text(encoding="utf-8")
        marker = '<script src="diary.js?v=201" defer></script>'
        injected = '<script src="/acceptance/bootstrap.js"></script>\n  ' + marker
        if marker not in html:
            raise AcceptanceError("diary_asset_version_mismatch")
        return HTMLResponse(
            html.replace(marker, injected),
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/acceptance/bootstrap.js")
    def bootstrap_js() -> Response:
        script = f"""
(() => {{
  const locationId = {json.dumps(location_id)};
  localStorage.setItem("emr4_token", {json.dumps(_jwt())});
  localStorage.setItem("emr4_diary_active_location", locationId);
  window.__EMR4_RAYLEEN_WAITING_ROOM__ = Object.freeze({{
    enabled: true,
    practiceId: {json.dumps(practice_id)},
    sessionGeneration: 1,
    async readFixedWaitingRoom(request, options) {{
      const response = await fetch("/acceptance/occupied-release", {{
        method: "POST",
        credentials: "same-origin",
        signal: options.signal,
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify(request)
      }});
      if (!response.ok) throw new Error("fixed_read_failed");
      return response.json();
    }}
  }});
}})();
"""
        return Response(
            script,
            media_type="text/javascript",
            headers={"Cache-Control": "no-store"},
        )

    if api_origin is not None:

        @app.get("/diary/diary.js")
        def local_diary_js() -> Response:
            source = (DIARY_DIR / "diary.js").read_text(encoding="utf-8")
            marker = (
                'const NGROK_URL   = '
                '"https://property-cinch-backfield.ngrok-free.dev";'
            )
            replacement = f"const NGROK_URL   = {json.dumps(api_origin)};"
            if source.count(marker) != 1:
                raise AcceptanceError("diary_api_origin_marker_mismatch")
            return Response(
                source.replace(marker, replacement),
                media_type="text/javascript",
                headers={"Cache-Control": "no-store"},
            )

    @app.post("/acceptance/occupied-release")
    def occupied_release(request: dict[str, Any]) -> JSONResponse:
        expected = {
            "locationId": location_id,
            "projectionKind": "FULL_QUEUE",
            "practitionerId": None,
            "waitingAreaId": None,
            "focusAppointmentId": None,
        }
        if request != expected:
            return JSONResponse({"status": "rejected"}, status_code=400)
        counters["release_reads"] += 1
        return JSONResponse(response_packet, headers={"Cache-Control": "no-store"})

    @app.get("/api/v1/diary/locations")
    def locations() -> list[dict[str, str]]:
        return [{"id": location_id, "name": "Authored Synthetic Main"}]

    @app.get("/api/v1/diary/template")
    def template() -> dict[str, Any]:
        return {
            "practice_name": "Authored Synthetic A4 Practice",
            "slot_start": "08:00",
            "slot_end": "18:00",
            "slot_interval_minutes": 15,
            "columns": [],
            "footer": ["Local authored-synthetic occupied UI acceptance"],
        }

    @app.get("/api/v1/appointments")
    def appointments() -> list[Any]:
        return []

    @app.get("/api/v1/appointments/types")
    def appointment_types() -> list[Any]:
        return []

    @app.get("/api/v1/appointments/bernie/pilot-eligibility")
    def pilot_eligibility() -> dict[str, bool]:
        return {"eligible": False}

    @app.get("/api/v1/practice/practitioners")
    def practitioners() -> list[Any]:
        return []

    @app.get("/api/v1/diary/roster")
    def roster() -> dict[str, list[Any]]:
        return {"entries": []}

    @app.get("/api/v1/diary/waiting-areas")
    def waiting_areas() -> list[Any]:
        return []

    @app.post("/api/v1/graphql")
    def shared_graphql_empty() -> dict[str, Any]:
        return {"data": {"practice": {"practitioners": []}}}

    @app.get("/favicon.ico")
    def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/hosting-policy.js")
    def hosting_policy_placeholder() -> Response:
        return Response(
            "/* local authored-synthetic acceptance: no hosting actuator */\n",
            media_type="text/javascript",
            headers={"Cache-Control": "no-store"},
        )

    app.mount("/diary", StaticFiles(directory=DIARY_DIR), name="diary-static")
    if IMAGES_DIR.exists():
        app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
    return app, counters


def _wait_server(server: uvicorn.Server, thread: threading.Thread) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if server.started:
            return
        if not thread.is_alive():
            break
        time.sleep(0.05)
    raise AcceptanceError("https_server_not_ready")


def run(
    *, occupied_evidence_path: Path, output_path: Path, screenshot_path: Path
) -> dict[str, Any]:
    occupied_evidence_path = occupied_evidence_path.resolve()
    output_path = output_path.resolve()
    screenshot_path = screenshot_path.resolve()
    if output_path.exists() or screenshot_path.exists():
        raise AcceptanceError("output_already_exists")
    occupied, release, execution_context_path = _validate_occupied_evidence(
        occupied_evidence_path
    )
    response_packet = release["response"]
    frame = response_packet["data"]["rayleenWaitingRoom"]
    now = datetime.now(timezone.utc)
    generated = datetime.fromisoformat(frame["generatedAt"].replace("Z", "+00:00"))
    expires = datetime.fromisoformat(frame["expiresAt"].replace("Z", "+00:00"))
    if not generated <= now < expires:
        raise AcceptanceError("occupied_release_not_current")
    port = _free_port()
    origin = f"https://{HOST}:{port}"
    app, counters = _build_app(response_packet, api_origin=origin)
    console_errors: list[str] = []
    page_errors: list[str] = []
    http_failures: list[dict[str, Any]] = []
    request_failures: list[dict[str, Any]] = []
    observed: dict[str, Any] = {}
    temporary_path: Path | None = None
    server_stopped = False
    with tempfile.TemporaryDirectory(prefix="emr4-a4-occupied-ui-") as directory:
        temporary_path = Path(directory)
        cert_path, key_path = _certificate(temporary_path)
        server = uvicorn.Server(
            uvicorn.Config(
                app,
                host=HOST,
                port=port,
                log_level="error",
                ssl_certfile=str(cert_path),
                ssl_keyfile=str(key_path),
            )
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            _wait_server(server, thread)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 390, "height": 844},
                )
                page = context.new_page()
                page.on(
                    "console",
                    lambda message: console_errors.append(message.text)
                    if message.type == "error"
                    else None,
                )
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                page.on(
                    "response",
                    lambda response: http_failures.append(
                        {"status": response.status, "url": response.url}
                    )
                    if response.status >= 400
                    else None,
                )
                page.on(
                    "requestfailed",
                    lambda request: request_failures.append(
                        {"failure": request.failure, "url": request.url}
                    ),
                )
                page.goto(
                    origin
                    + "/diary/diary.html?standalone_diary=true"
                    "&rayleen_waiting_room=true",
                    wait_until="networkidle",
                )
                toggle = page.locator("#btn-rayleen-waiting-room")
                toggle.wait_for(state="visible")
                toggle.click()
                card = page.locator(".rayleen-waiting-room-card")
                card.wait_for(state="visible")
                expected_count = frame["projection"]["selectedCount"]
                observed["card_count"] = card.count()
                observed["provenance"] = page.locator(
                    "#rayleen-waiting-room-provenance"
                ).inner_text()
                observed["status"] = page.locator(
                    "#rayleen-waiting-room-status"
                ).inner_text()
                observed["patient_display_token"] = card.locator("h3").inner_text()
                observed["footer"] = page.locator(
                    "#rayleen-waiting-room-panel footer"
                ).inner_text()
                if (
                    observed["card_count"] != expected_count
                    or observed["provenance"]
                    != "Model-selected, proofreader admitted"
                    or observed["patient_display_token"]
                    != frame["backendFacts"][0]["patientDisplayToken"]
                    or "No booking is reserved, confirmed or changed"
                    not in observed["footer"]
                ):
                    raise AcceptanceError("occupied_dom_projection_mismatch")
                page.locator("#btn-refresh-rayleen-waiting-room").click()
                page.wait_for_function(
                    "() => document.querySelectorAll("
                    "'.rayleen-waiting-room-card').length === 1"
                )
                page.keyboard.press("Escape")
                if not page.locator("#rayleen-waiting-room-panel").evaluate(
                    "element => element.classList.contains('hidden')"
                ):
                    raise AcceptanceError("occupied_escape_close_failed")
                toggle.click()
                card.wait_for(state="visible")
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_path), full_page=True)
                observed["refresh_recovered"] = counters["release_reads"] >= 2
                observed["escape_closed"] = True
                observed["reopen_rendered"] = card.count() == 1
                context.close()
                browser.close()
        finally:
            server.should_exit = True
            thread.join(timeout=15)
            server_stopped = not thread.is_alive()
    temporary_tls_material_absent = (
        temporary_path is not None and not temporary_path.exists()
    )
    if (
        not server_stopped
        or not temporary_tls_material_absent
        or console_errors
        or page_errors
        or not all(
            observed.get(key) is True
            for key in ("refresh_recovered", "escape_closed", "reopen_rendered")
        )
    ):
        print(
            json.dumps(
                {
                    "browser_failure_diagnostics": {
                        "server_stopped": server_stopped,
                        "temporary_tls_material_absent": temporary_tls_material_absent,
                        "console_errors": console_errors,
                        "page_errors": page_errors,
                        "http_failures": http_failures,
                        "request_failures": request_failures,
                        "observed": observed,
                    }
                },
                sort_keys=True,
            )
        )
        raise AcceptanceError("occupied_browser_acceptance_failed")

    source_paths = (
        Path(__file__).resolve(),
        occupied_evidence_path,
        execution_context_path,
        ROOT / "docs/diary/diary.html",
        ROOT / "docs/diary/diary.js",
        ROOT / "docs/diary/diary.css",
        ROOT / "docs/diary/rayleen-waiting-room-projection.mjs",
    )
    evidence = {
        "schema_version": "emr4.model_required_bureau_a4.occupied_ui.v1",
        "result": "model_required_bureau_a4_occupied_product_read_ui_pass",
        "evidence_label": "occupied_authored_synthetic_live_local_product_read_ui",
        "transport": "test_only_https_playwright_no_route_interception",
        "data_class": "authored_synthetic",
        "origin_is_loopback": True,
        "route_interception": False,
        "test_only_diary_api_origin": origin,
        "diary_logic_modified_beyond_api_origin": False,
        "occupied_selector_evidence_hash": _file_hash(occupied_evidence_path),
        "execution_context_hash": _file_hash(execution_context_path),
        "release_hash": contracts.prefixed_sha256(release),
        "provider_call_count": occupied["candidate_runtime_provider_call_count"],
        "proofreader_admitted": True,
        "selector_provenance": frame["projection"]["selectorProvenance"],
        "selected_count": frame["projection"]["selectedCount"],
        "release_read_count": counters["release_reads"],
        "observed_dom": observed,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "http_failures": http_failures,
        "request_failures": request_failures,
        "screenshot": {
            "path": screenshot_path.relative_to(ROOT).as_posix(),
            "sha256": _file_hash(screenshot_path),
        },
        "source_hashes": {
            path.relative_to(ROOT).as_posix(): _file_hash(path)
            for path in source_paths
        },
        "server_stopped": server_stopped,
        "temporary_tls_material_absent": temporary_tls_material_absent,
        "provider_calls_during_ui": 0,
        "database_access_during_ui": 0,
        "command_count": 0,
        "write_count": 0,
        "deployment_count": 0,
        "protected_ref_movement_count": 0,
        "claims_not_made": [
            "production_readiness",
            "real_patient_safety",
            "australian_physical_or_sovereign_processing",
            "deployment_or_release",
        ],
    }
    evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--occupied-evidence", type=Path, default=DEFAULT_OCCUPIED_EVIDENCE
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT)
    parser.add_argument("--revalidation-context", type=Path)
    parser.add_argument("--revalidation-evidence", type=Path)
    args = parser.parse_args()
    try:
        occupied_evidence_path = args.occupied_evidence
        if (
            args.revalidation_context is not None
            or args.revalidation_evidence is not None
        ):
            if (
                args.revalidation_context is None
                or args.revalidation_evidence is None
            ):
                raise AcceptanceError("occupied_revalidation_paths_incomplete")
            _revalidate_occupied_selection_for_ui(
                original_evidence_path=args.occupied_evidence,
                context_output_path=args.revalidation_context,
                evidence_output_path=args.revalidation_evidence,
            )
            occupied_evidence_path = args.revalidation_evidence
        evidence = run(
            occupied_evidence_path=occupied_evidence_path,
            output_path=args.output,
            screenshot_path=args.screenshot,
        )
    except (AcceptanceError, OSError) as error:
        print(
            json.dumps(
                {
                    "result": "model_required_bureau_a4_occupied_ui_blocked",
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_call_count": evidence["provider_call_count"],
                "selected_count": evidence["selected_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
