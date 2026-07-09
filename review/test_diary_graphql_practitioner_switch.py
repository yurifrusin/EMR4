"""
Route-intercepted browser evidence for the Diary practitioner-directory GraphQL
switch.

These checks deliberately keep the committed runtime default off. The enabled
path is exercised by serving a test-only copy of diary.js with the source
constant flipped before the browser loads the page.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency not installed
    pytest.skip(
        "playwright not installed (pip install playwright && playwright install chromium)",
        allow_module_level=True,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DIARY_JS = DOCS_DIR / "diary" / "diary.js"
REVIEW_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.e30.c2ln"
harness.assert_valid_review_token(REVIEW_AUTH_TOKEN)


def _rest_rows(default_location=None):
    if default_location == "omit":
        location = None
    else:
        location = default_location or {"id": "loc-1", "name": "Main Clinic"}
    return [
        {
            "id": "prac-rest-1",
            "displayName": "Dr Rest Fallback",
            "roleLabel": "GP",
            "active": True,
            "defaultLocation": location,
            "provider_number": "PN-SECRET-CANARY",
            "prescriber_number": "PR-SECRET-CANARY",
            "ahpra_number": "AHPRA-SECRET-CANARY",
            "hpi_i": "HPII-SECRET-CANARY",
            "email": "secret@example.invalid",
            "phone": "555-SECRET",
        }
    ]


def _route_diary_api(page, *, graphql_status=200, graphql_body=None, rest_rows=None):
    captured = {
        "rest_requests": [],
        "graphql_requests": [],
        "methods": [],
    }

    def handle_api(route):
        request = route.request
        url = request.url
        captured["methods"].append(request.method)

        if "/api/v1/graphql" in url:
            post_data = request.post_data or ""
            try:
                body = json.loads(post_data)
            except json.JSONDecodeError:
                body = {}
            captured["graphql_requests"].append(
                {
                    "method": request.method,
                    "url": url,
                    "body": body,
                    "authorization": request.headers.get("authorization", ""),
                }
            )
            route.fulfill(
                status=graphql_status,
                content_type="application/json",
                body=json.dumps(graphql_body or {"errors": [{"extensions": {"code": "FORBIDDEN"}}]}),
            )
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "GraphQL Switch Evidence Practice",
                "slot_defaults": {"start": "09:00", "end": "10:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Legacy Template",
                    "practitioner_id": "prac-rest-1",
                    "practitioner_ahpra": "MED0001234567",
                }],
            }))
        elif "/api/v1/practice/practitioners" in url:
            captured["rest_requests"].append(
                {
                    "method": request.method,
                    "url": url,
                    "authorization": request.headers.get("authorization", ""),
                }
            )
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(rest_rows if rest_rows is not None else _rest_rows()),
            )
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps([{"id": "loc-1", "name": "Main Clinic", "is_active": True}]),
            )
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "surface": "bernie_staff_review",
                "enabled": False,
                "eligible": False,
                "reason": "graphql_switch_route_intercepted_evidence",
            }))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    page.route("**/api/v1/**", handle_api)
    return captured


def _serve_enabled_graphql_script(page):
    source = DIARY_JS.read_text(encoding="utf-8", errors="replace")
    assert source.count("const ENABLE_GRAPHQL_PRACTITIONERS = false;") == 1
    enabled_source = source.replace(
        "const ENABLE_GRAPHQL_PRACTITIONERS = false;",
        "const ENABLE_GRAPHQL_PRACTITIONERS = true;",
    )
    page.route(
        "**/diary/diary.js*",
        lambda route: route.fulfill(
            status=200,
            content_type="application/javascript",
            body=enabled_source,
        ),
    )


def _open_diary_and_selector(page, base_url):
    page.goto(base_url + "/diary/diary.html")
    harness.bootstrap_auth(page, REVIEW_AUTH_TOKEN)
    page.reload()
    page.wait_for_selector("#diary-grid-container:not(.hidden)", state="visible", timeout=10000)
    page.evaluate("""
        () => window.openBookingModalForCreate({
            room_label: "Room 1",
            assignment: "Dr Legacy Template",
            practitioner_id: "prac-rest-1",
            practitioner_ahpra: "MED0001234567"
        }, "09:00")
    """)
    page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)


def test_default_off_practitioner_switch_uses_rest_without_graphql_request():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        captured = _route_diary_api(page)

        _open_diary_and_selector(page, base_url)

        assert captured["graphql_requests"] == []
        assert len(captured["rest_requests"]) == 1
        rest_request = captured["rest_requests"][0]
        assert rest_request["method"] == "GET"
        assert "activeOnly=true" in rest_request["url"]
        assert "limit=200" in rest_request["url"]
        assert rest_request["authorization"].startswith("Bearer ")
        assert not any(method in {"POST", "PUT", "PATCH", "DELETE"} for method in captured["methods"])
        assert page.locator("#booking-practitioner option").evaluate_all(
            "(options) => options.map(option => option.textContent)"
        ) == ["Dr Rest Fallback (Main Clinic)"]

        page_text = page.locator("body").text_content()
        for forbidden in ("SECRET", "AHPRA-SECRET", "HPII-SECRET", "secret@example.invalid", "555-SECRET"):
            assert forbidden not in page_text
        browser.close()


def test_enabled_graphql_forbidden_response_falls_back_to_rest_selector_rows():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _serve_enabled_graphql_script(page)
        captured = _route_diary_api(
            page,
            graphql_body={"errors": [{"message": "denied", "extensions": {"code": "FORBIDDEN"}}]},
        )

        _open_diary_and_selector(page, base_url)

        assert len(captured["graphql_requests"]) == 1
        graphql_request = captured["graphql_requests"][0]
        assert graphql_request["method"] == "POST"
        assert graphql_request["authorization"].startswith("Bearer ")
        body = graphql_request["body"]
        assert "query GetPractitioners" in body["query"]
        assert body["variables"] == {"activeOnly": True, "limit": 200, "offset": 0}

        assert len(captured["rest_requests"]) == 1
        assert "activeOnly=true" in captured["rest_requests"][0]["url"]
        assert "limit=200" in captured["rest_requests"][0]["url"]
        assert page.locator("#booking-practitioner option").evaluate_all(
            "(options) => options.map(option => ({ value: option.value, text: option.textContent }))"
        ) == [{"value": "prac-rest-1", "text": "Dr Rest Fallback (Main Clinic)"}]
        browser.close()


def test_enabled_graphql_bad_user_input_response_falls_back_to_rest_selector_rows():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _serve_enabled_graphql_script(page)
        captured = _route_diary_api(
            page,
            graphql_body={"errors": [{"message": "bad input", "extensions": {"code": "BAD_USER_INPUT"}}]},
        )

        _open_diary_and_selector(page, base_url)

        assert len(captured["graphql_requests"]) == 1
        assert len(captured["rest_requests"]) == 1
        assert page.locator("#booking-practitioner option").evaluate_all(
            "(options) => options.map(option => option.textContent)"
        ) == ["Dr Rest Fallback (Main Clinic)"]
        browser.close()


def test_enabled_graphql_transport_failure_falls_back_to_single_rest_request():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _serve_enabled_graphql_script(page)
        captured = _route_diary_api(page, graphql_status=503, graphql_body={"detail": "unavailable"})

        _open_diary_and_selector(page, base_url)

        assert len(captured["graphql_requests"]) == 1
        assert len(captured["rest_requests"]) == 1
        assert captured["rest_requests"][0]["method"] == "GET"
        assert not any(method in {"PUT", "PATCH", "DELETE"} for method in captured["methods"])
        browser.close()


def test_enabled_graphql_practice_null_returns_empty_without_rest_fallback():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _serve_enabled_graphql_script(page)
        captured = _route_diary_api(page, graphql_body={"data": {"practice": None}})

        _open_diary_and_selector(page, base_url)

        assert len(captured["graphql_requests"]) == 1
        assert captured["rest_requests"] == []
        assert page.locator("#booking-practitioner option").evaluate_all(
            "(options) => options.map(option => ({ value: option.value, text: option.textContent }))"
        ) == [{"value": "MED0001234567", "text": "Dr Legacy Template (Room 1)"}]
        browser.close()


def test_enabled_graphql_default_location_null_preserves_row_without_rest_fallback():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _serve_enabled_graphql_script(page)
        captured = _route_diary_api(
            page,
            graphql_body={
                "data": {
                    "practice": {
                        "practitioners": [
                            {
                                "id": "prac-rest-1",
                                "displayName": "Dr GraphQL Null Location",
                                "roleLabel": "GP",
                                "active": True,
                                "defaultLocation": None,
                                "providerNumber": "PN-SECRET-CANARY",
                                "email": "secret@example.invalid",
                            }
                        ]
                    }
                }
            },
        )

        _open_diary_and_selector(page, base_url)

        assert len(captured["graphql_requests"]) == 1
        assert captured["rest_requests"] == []
        assert page.locator("#booking-practitioner option").evaluate_all(
            "(options) => options.map(option => ({ value: option.value, text: option.textContent }))"
        ) == [{"value": "prac-rest-1", "text": "Dr GraphQL Null Location"}]
        page_text = page.locator("body").text_content()
        for forbidden in ("SECRET", "secret@example.invalid"):
            assert forbidden not in page_text
        browser.close()
