#!/usr/bin/env python3
"""Run the first cost-bounded explicit-selection occupied Bureau retry."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from scripts import reception_one_bureau_live_isolated_planner_evaluation as base
from scripts import reception_one_extended_proposal_runtime_acceptance as selection
from scripts import reception_one_vertex_cost_budget as cost_budget


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-cost-bounded-occupied-retry"
)
AUTHORITY_PATH = OUTPUT / "occupied-authority.json"
PREFLIGHT_PATH = OUTPUT / "occupied-preflight-evidence.json"
PROVIDER_FREE_PATH = OUTPUT / "provider-free-evidence.json"
ISOLATION_PATH = OUTPUT / "real-isolation-evidence.json"
PRE_RESIDUE_PATH = OUTPUT / "pre-attempt-residue-evidence.json"
EVIDENCE_PATH = OUTPUT / "occupied-ui-route-evidence.json"
FAILURE_PATH = OUTPUT / "occupied-ui-route-failure-evidence.json"
CLEANUP_PATH = OUTPUT / "occupied-ui-cleanup-evidence.json"
POST_RESIDUE_PATH = OUTPUT / "occupied-final-residue-evidence.json"
SCREENSHOT_PATH = OUTPUT / "occupied-explicit-selection-result.png"
COST_POLICY_PATH = OUTPUT / "cost-policy.json"
COST_LEDGER_PATH = OUTPUT / "cumulative-cost-ledger.json"
RESULT_PATH = OUTPUT / "occupied-cost-bounded-result.json"
LOCKED_DATABASE = (
    "gp_pms_reception_one_cost_retry_4f2d8a31_20260731"
)
RUNTIME_TAG = "reception-one-cost-retry-4f2d8a31"
REFERENCE_DATE = "2026-08-03"
INSTRUCTION = (
    "Extend Margaret Thompson's appointment with Dr Alex Shera "
    "to 45 minutes."
)
SELECTED_APPOINTMENT_ID = selection.SELECTED_APPOINTMENT_ID
GRAPH_REVISION = 163
COMPASS_REVISION = 144
RESERVATION_ID = "bureau-cost-bounded-occupied-retry-001"


class CostBoundedOccupiedRetryError(RuntimeError):
    """A sanitized cost, selection, route, proofreader or evidence failure."""


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _configure_base() -> None:
    base.OUTPUT = OUTPUT
    base.AUTHORITY_PATH = AUTHORITY_PATH
    base.PREFLIGHT_PATH = PREFLIGHT_PATH
    base.PROVIDER_FREE_PATH = PROVIDER_FREE_PATH
    base.ISOLATION_PATH = ISOLATION_PATH
    base.PRE_RESIDUE_PATH = PRE_RESIDUE_PATH
    base.EVIDENCE_PATH = EVIDENCE_PATH
    base.FAILURE_PATH = FAILURE_PATH
    base.CLEANUP_PATH = CLEANUP_PATH
    base.POST_RESIDUE_PATH = POST_RESIDUE_PATH
    base.SCREENSHOT_PATH = SCREENSHOT_PATH
    base.LOCKED_DATABASE = LOCKED_DATABASE
    base.RUNTIME_TAG = RUNTIME_TAG
    base.RUNTIME_DIR = (
        base.Path(base.tempfile.gettempdir()) / f"emr4-{RUNTIME_TAG}"
    )
    base.REFERENCE_DATE = REFERENCE_DATE
    base.INSTRUCTION = INSTRUCTION
    base.GRAPH_REVISION = GRAPH_REVISION
    base.COMPASS_REVISION = COMPASS_REVISION
    base._browser_request = _browser_request


def _browser_request() -> tuple[dict[str, Any], dict[str, Any]]:
    network: list[dict[str, str]] = []
    route_request_hashes: list[str] = []
    submitted_modes: list[str] = []
    selection_bound_in_request: list[bool] = []
    selected_before_submit = False
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        page = context.new_page()

        def record_request(request) -> None:
            parsed = urlsplit(request.url)
            network.append(
                {
                    "method": request.method.upper(),
                    "hostname": parsed.hostname or "",
                    "path": parsed.path,
                }
            )
            if (
                request.method.upper() == "POST"
                and parsed.path
                == "/api/v1/appointments/proposals/reception-one/compose"
            ):
                body = request.post_data_json or {}
                submitted_modes.append(str(body.get("planner_mode", "")))
                route_request_hashes.append(base._canonical_hash(body))
                selection_bound_in_request.append(
                    isinstance(body.get("selected_appointment_id"), str)
                    and bool(body.get("selected_appointment_id"))
                )

        page.on("request", record_request)
        page.goto(
            f"{base.STATIC_URL}/meta-grid-auth.html",
            wait_until="domcontentloaded",
        )
        page.wait_for_url("**/diary/diary.html?reference_date=2026-07-27**")
        page.goto(
            f"{base.STATIC_URL}/diary/diary.html"
            "?smoke=true"
            "&meta_grid_open=true"
            "&reception_one_demo=appointment_sheet"
            "&standalone_diary=true"
            f"&reference_date={REFERENCE_DATE}"
            "&product_context_live_local=true"
            "&bureau_runtime_ui=true"
            f"&extended_selected_appointment_id={SELECTED_APPOINTMENT_ID}",
            wait_until="networkidle",
        )
        selected = page.locator(
            f'[data-appointment-id="{SELECTED_APPOINTMENT_ID}"]'
        )
        selected.wait_for(state="visible", timeout=20_000)
        selected.click()
        selected_before_submit = (
            selected.get_attribute("aria-selected") == "true"
        )
        if not selected_before_submit:
            raise CostBoundedOccupiedRetryError(
                "appointment_selection_not_bound"
            )
        planner = page.get_by_test_id("meta-grid-planner-mode")
        planner.wait_for(state="visible")
        planner.select_option("isolated_vertex")
        request_box = page.get_by_label(
            "What would you like to find or prepare?",
            exact=True,
        )
        request_box.fill(INSTRUCTION)
        with page.expect_response(
            lambda response: (
                response.request.method.upper() == "POST"
                and response.url.split("?", 1)[0].endswith(
                    "/api/v1/appointments/proposals/reception-one/compose"
                )
            ),
            timeout=240_000,
        ) as response_info:
            request_box.press("Enter")
        response = response_info.value
        try:
            payload = response.json()
        except ValueError as error:
            raise CostBoundedOccupiedRetryError(
                "route_response_invalid"
            ) from error
        if not isinstance(payload, dict):
            raise CostBoundedOccupiedRetryError(
                "route_response_invalid"
            )
        provenance_text = None
        if (
            response.status == 200
            and payload.get("result") == "proposal_ready"
        ):
            provenance = page.get_by_test_id(
                "meta-grid-planner-provenance"
            )
            provenance.wait_for(state="visible", timeout=20_000)
            provenance_text = provenance.inner_text()
        page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)
        context.close()
        browser.close()

    route_calls = [
        item
        for item in network
        if (
            item["method"] == "POST"
            and item["path"]
            == "/api/v1/appointments/proposals/reception-one/compose"
        )
    ]
    external_hosts = sorted(
        {
            item["hostname"]
            for item in network
            if item["hostname"]
            not in {"::1", "127.0.0.1", "localhost", ""}
        }
    )
    return payload, {
        "http_status": response.status,
        "submitted_modes": submitted_modes,
        "route_call_count": len(route_calls),
        "route_request_hashes": route_request_hashes,
        "external_hosts": external_hosts,
        "request_interception_used": False,
        "rendered_provenance": provenance_text,
        "exact_appointment_row_clicked": True,
        "aria_selected_verified_before_submit": selected_before_submit,
        "selected_appointment_id_present_in_request": (
            selection_bound_in_request == [True]
        ),
        "selected_appointment_id_retained": False,
    }


def _external_audit_path() -> Path | None:
    candidates = sorted(
        OUTPUT.glob(
            "runtime-*/occupied-turn-001-external-audit.json"
        )
    )
    if len(candidates) == 1:
        return candidates[0]
    return None


def _purpose_hash() -> str:
    return base._canonical_hash(
        {
            "data_class": "authored_synthetic",
            "goal": "resize",
            "duration_minutes": 45,
            "exact_appointment_selected": True,
            "instruction_sha256": base._canonical_hash(
                {"instruction": INSTRUCTION}
            ),
            "provider": base.EXPECTED_BINDING,
            "continuity_binding": {
                "graph_revision": GRAPH_REVISION,
                "compass_revision": COMPASS_REVISION,
            },
        }
    )


def _text_residue_free() -> bool:
    needle = SELECTED_APPOINTMENT_ID
    for path in OUTPUT.rglob("*"):
        if (
            path.is_file()
            and path.suffix.lower()
            in {".json", ".jsonl", ".md", ".txt", ".log"}
            and needle in path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        ):
            return False
    return True


def run() -> dict[str, Any]:
    _configure_base()
    if RESULT_PATH.exists() or COST_LEDGER_PATH.exists():
        raise CostBoundedOccupiedRetryError(
            "occupied_retry_output_preexisted"
        )
    if not PRE_RESIDUE_PATH.exists():
        base.run_pre_attempt_residue()
    base._controls()
    cost_budget.reserve_call(
        policy_path=COST_POLICY_PATH,
        ledger_path=COST_LEDGER_PATH,
        reservation_id=RESERVATION_ID,
        purpose_hash=_purpose_hash(),
    )
    evidence: dict[str, Any] | None = None
    failure: Exception | None = None
    try:
        evidence = base.run_occupied()
    except Exception as error:
        failure = error
    external = _external_audit_path()
    admitted = bool(
        evidence
        and evidence.get("result")
        == "reception_one_bureau_live_isolated_planner_occupied_pass"
    )
    if external is None:
        cost_ledger = cost_budget.block_unknown_usage(
            policy_path=COST_POLICY_PATH,
            ledger_path=COST_LEDGER_PATH,
            reservation_id=RESERVATION_ID,
            reason_code="provider_external_audit_missing",
        )
        failure = failure or CostBoundedOccupiedRetryError(
            "provider_usage_unknown"
        )
    else:
        cost_ledger = cost_budget.settle_call(
            policy_path=COST_POLICY_PATH,
            ledger_path=COST_LEDGER_PATH,
            reservation_id=RESERVATION_ID,
            external_audit_path=external,
            admitted=admitted,
        )
    selection_ok = bool(
        evidence
        and evidence.get("browser", {}).get(
            "exact_appointment_row_clicked"
        )
        is True
        and evidence.get("browser", {}).get(
            "aria_selected_verified_before_submit"
        )
        is True
        and evidence.get("browser", {}).get(
            "selected_appointment_id_present_in_request"
        )
        is True
        and evidence.get("browser", {}).get(
            "selected_appointment_id_retained"
        )
        is False
    )
    text_residue_free = _text_residue_free()
    passed = (
        admitted
        and failure is None
        and selection_ok
        and text_residue_free
        and cost_ledger.get("terminal_success") is True
        and cost_ledger.get("accounted_cost", 1) < 1
        and cost_ledger.get("outstanding_reservation") == 0
    )
    result = {
        "schema_version": (
            "reception.one.bureau.cost_bounded_occupied_retry.result.v1"
        ),
        "result": (
            "reception_one_bureau_cost_bounded_occupied_retry_pass"
            if passed
            else "reception_one_bureau_cost_bounded_occupied_retry_failed_closed"
        ),
        "data_class": "authored_synthetic",
        "selection": {
            "exact_appointment_row_clicked": selection_ok,
            "aria_selected_verified_before_submit": selection_ok,
            "selected_appointment_id_present_in_request": selection_ok,
            "selected_appointment_id_retained": False,
            "raw_database_identifier_text_absent": text_residue_free,
        },
        "occupied_route_result": (
            evidence.get("result") if evidence else None
        ),
        "runtime_audit_ref": (
            evidence.get("route_release", {}).get("runtime_audit_ref")
            if evidence
            else None
        ),
        "provider_calls_this_attempt": (
            1 if external is not None else None
        ),
        "cost": {
            "cumulative_ceiling": cost_ledger.get("ceiling"),
            "accounted_cost": cost_ledger.get("accounted_cost"),
            "outstanding_reservation": cost_ledger.get(
                "outstanding_reservation"
            ),
            "calls_accounted_including_predecessor": (
                cost_ledger.get("calls_accounted")
            ),
            "fresh_calls_accounted": cost_ledger.get(
                "fresh_calls_accounted"
            ),
            "terminal_success": cost_ledger.get("terminal_success"),
            "ledger_terminal_hash": cost_ledger.get(
                "terminal_event_hash"
            ),
        },
        "retry_performed_within_dialogue": False,
        "fallback_performed": False,
        "appointment_confirmation_performed": False,
        "appointment_write_performed": False,
        "database_truth_unchanged": bool(
            evidence and evidence.get("database_unchanged") is True
        ),
        "post_attempt_residue_clear": bool(
            evidence
            and evidence.get("post_attempt_residue_clear") is True
        ),
        "reason_code": (
            None
            if passed
            else (
                str(failure).split(":", 1)[0]
                if failure is not None
                else "occupied_contract_not_admitted"
            )
        ),
        "candid_limit": (
            "This result can prove only one authored-synthetic "
            "UI-to-route-to-proofreader proposal through the configured and "
            "observed Sydney Vertex locational endpoint. It does not prove "
            "Australian physical or sovereign processing, production fitness "
            "or safety for real patient, health or clinical data."
        ),
    }
    result["evidence_hash"] = base._canonical_hash(result)
    _write(RESULT_PATH, result)
    if not passed:
        raise CostBoundedOccupiedRetryError(
            str(result["reason_code"])
        ) from failure
    return result


def main() -> int:
    try:
        result = run()
    except (
        CostBoundedOccupiedRetryError,
        cost_budget.CostBudgetError,
        base.OccupiedUiError,
    ) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_bureau_cost_bounded_"
                        "occupied_retry_failed_closed"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": result["result"],
                "provider_calls": result[
                    "provider_calls_this_attempt"
                ],
                "accounted_cost_usd": result["cost"][
                    "accounted_cost"
                ],
                "writes": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
