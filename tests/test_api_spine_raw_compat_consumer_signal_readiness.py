import re
from pathlib import Path

from tests.test_api_spine_legacy_compatibility_write_deprecation_map import (
    EXPECTED_COMPATIBILITY_WRITES,
)


ROOT = Path(__file__).resolve().parents[1]
READINESS_PATH = ROOT / "docs" / "api-spine" / "raw-compat-consumer-signal-readiness.md"
DEPRECATION_MAP_PATH = ROOT / "docs" / "api-spine" / "legacy-compatibility-write-deprecation-map.md"
CONFIG_PATH = ROOT / "app" / "config.py"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
RAW_COMPAT_TEST = ROOT / "tests" / "test_appointment_raw_compat.py"

EXPECTED_ROWS = {
    "POST /api/v1/appointments": {
        "handler": "create_appointment",
        "tag": "raw_compat_create",
        "sites": {"create_modal_raw_post"},
        "condition": "create fallback when `confirmEndpoint` or `confirmPayload` is absent",
    },
    "PUT /api/v1/appointments/{appointment_id}": {
        "handler": "update_appointment",
        "tag": "raw_compat_update",
        "sites": {"edit_modal_raw_put", "drag_resize_raw_put"},
        "condition": "edit-modal or drag/resize fallback when `confirmEndpoint` or `confirmPayload` is absent",
    },
    "PATCH /api/v1/appointments/{appointment_id}/status": {
        "handler": "update_appointment_status",
        "tag": "raw_compat_status",
        "sites": {
            "edit_modal_raw_status_patch",
            "create_modal_raw_status_patch",
            "status_proposal_raw_patch",
        },
        "condition": "status side-write after edit/create or fallback when signed status confirmation is unavailable",
    },
    "DELETE /api/v1/appointments/{appointment_id}": {
        "handler": "cancel_appointment",
        "tag": "raw_compat_delete",
        "sites": {"delete_modal_raw_delete"},
        "condition": "delete fallback when `confirmEndpoint` or `confirmPayload` is absent",
    },
}

SITE_FRAGMENTS = {
    "create_modal_raw_post": ('apiFetch(`/appointments`,', 'method: "POST"'),
    "edit_modal_raw_put": ('apiFetch(`/appointments/${editingAppointmentId}`,', 'method: "PUT"'),
    "drag_resize_raw_put": ('apiFetch(`/appointments/${appt.id}`,', 'method: "PUT"'),
    "edit_modal_raw_status_patch": ('apiFetch(`/appointments/${editingAppointmentId}/status`,', 'method: "PATCH"'),
    "create_modal_raw_status_patch": ('apiFetch(`/appointments/${newApptObj.id}/status`,', 'method: "PATCH"'),
    "status_proposal_raw_patch": ('apiFetch(`/appointments/${appt.id}/status`,', 'method: "PATCH"'),
    "delete_modal_raw_delete": ('apiFetch(`/appointments/${editingAppointmentId}`,', 'method: "DELETE"'),
}

REQUIRED_CLOSED_GATES = {
    "changing `appointment_raw_compat_mode`",
    "removing, renaming, blocking, or changing compatibility write routes",
    "raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement",
    "proposal-only route idempotency expansion",
    "provider prompt wiring or live provider calls",
    "provider dry-run wiring",
    "memory/RAG/GraphRAG runtime wiring",
    "H15/H-series runtime imports",
    "historical diary material access",
    "broad historical diary trove mining",
    "external patient clients",
    "runtime FGA clients",
    "GraphQL mutations",
    "direct database writes by model output",
    "model-to-database writes outside REST command handlers",
}


def _public_route(method: str, route: str) -> str:
    prefix = "/api/v1/appointments"
    return f"{method} {prefix}{route}" if route else f"{method} {prefix}"


def _inventory_rows() -> list[dict[str, object]]:
    text = READINESS_PATH.read_text(encoding="utf-8")
    section = text.split("## Consumer Signal Inventory", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "compatibility_write": cells[0].strip("`"),
                "handler": cells[1].strip("`"),
                "tag": cells[2].strip("`"),
                "signal_site": cells[3].strip("`"),
                "consumer": cells[4].strip("`"),
                "sites": set(re.findall(r"`([^`]+)`", cells[5])),
                "condition": cells[6],
                "header_consumed": cells[7].strip("`"),
                "readiness": cells[8].strip("`"),
            }
        )
    return rows


def test_readiness_inventory_covers_same_raw_writes_as_deprecation_map():
    expected_routes = {
        public_route
        for public_route, _handler, _tag, _proposals, _confirms in EXPECTED_COMPATIBILITY_WRITES
    }

    rows = _inventory_rows()
    assert {row["compatibility_write"] for row in rows} == expected_routes
    assert set(EXPECTED_ROWS) == expected_routes
    assert "compatibility_supported_until_client_parity" in DEPRECATION_MAP_PATH.read_text(encoding="utf-8")


def test_readiness_inventory_rows_match_expected_consumers_and_posture():
    for row in _inventory_rows():
        expected = EXPECTED_ROWS[row["compatibility_write"]]
        assert row["handler"] == expected["handler"]
        assert row["tag"] == expected["tag"]
        assert row["signal_site"] == f'_raw_compat_evidence_and_headers("{expected["tag"]}")'
        assert row["consumer"] == "docs/diary/diary.js"
        assert row["sites"] == expected["sites"]
        assert row["condition"] == expected["condition"]
        assert row["header_consumed"] == "console_warn"
        assert row["readiness"] == "consumer_wired_keep_audit_mode"


def test_backend_raw_compat_handlers_emit_expected_signals():
    router = APPOINTMENTS_ROUTER.read_text(encoding="utf-8")
    for expected in EXPECTED_ROWS.values():
        call = f'_raw_compat_evidence_and_headers("{expected["tag"]}")'
        assert router.count(call) == 1
        handler_index = router.index(f"def {expected['handler']}(")
        call_index = router.index(call)
        assert handler_index < call_index

    tag_occurrences = re.findall(r'"(raw_compat_(?:create|update|status|delete))"', router)
    for tag in {expected["tag"] for expected in EXPECTED_ROWS.values()}:
        assert tag_occurrences.count(tag) == 2, (
            "Each raw compat tag should appear once in the allowed evidence list "
            "and once in its handler signal call."
        )


def test_diary_frontend_contains_the_documented_raw_call_sites_only():
    text = DIARY_JS.read_text(encoding="utf-8")

    expected_fragments = {
        "apiFetch(`/appointments`,": 1,
        "apiFetch(`/appointments/${editingAppointmentId}`,": 2,
        "apiFetch(`/appointments/${appt.id}`,": 1,
        "apiFetch(`/appointments/${editingAppointmentId}/status`,": 1,
        "apiFetch(`/appointments/${newApptObj.id}/status`,": 1,
        "apiFetch(`/appointments/${appt.id}/status`,": 1,
    }
    for fragment, count in expected_fragments.items():
        assert text.count(fragment) == count

    for expected in EXPECTED_ROWS.values():
        for site in expected["sites"]:
            route_fragment, method_fragment = SITE_FRAGMENTS[site]
            assert route_fragment in text
            assert method_fragment in text


def test_frontend_consumes_deprecation_header_only_at_shared_api_fetch_boundary():
    frontend_files = [
        *list((ROOT / "docs" / "diary").glob("*.js")),
        *list((ROOT / "docs" / "taskpane").glob("*.js")),
        *list((ROOT / "EMR4 Sidebar" / "src" / "taskpane").glob("*.js")),
    ]
    assert DIARY_JS in frontend_files
    hits = []
    for path in frontend_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "deprecation" in text.lower():
            hits.append(path.relative_to(ROOT).as_posix())
    assert hits == ["docs/diary/diary.js"]

    diary = DIARY_JS.read_text(encoding="utf-8", errors="replace")
    api_fetch = diary[diary.index("async function apiFetch(") : diary.index("function normalizeApiPath(")]
    assert 'res.headers.get("deprecation")' in api_fetch
    assert "console.warn" in api_fetch
    assert "Deprecated route:" in api_fetch
    assert api_fetch.index("if (res.status === 401)") < api_fetch.index('res.headers.get("deprecation")')


def test_backend_header_modes_are_covered_but_default_stays_audit():
    config = CONFIG_PATH.read_text(encoding="utf-8")
    raw_compat_test = RAW_COMPAT_TEST.read_text(encoding="utf-8")
    readiness = READINESS_PATH.read_text(encoding="utf-8")

    assert 'appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"' in config
    assert "class TestHeaderMode" in raw_compat_test
    assert "class TestOffMode" in raw_compat_test
    assert 'resp.headers.get("deprecation") is not None' in raw_compat_test
    assert "The current decision is `keep_audit_mode`." in readiness
    assert "Do not change `appointment_raw_compat_mode` to `header`" in readiness
    assert "Do not change `appointment_raw_compat_mode` to `off`" in readiness


def test_no_production_code_overrides_raw_compat_mode():
    assignments = []
    for path in (ROOT / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"appointment_raw_compat_mode(?:\s*:\s*[^=]+)?\s*=", text):
            assignments.append((path.relative_to(ROOT).as_posix(), match.group(0)))

    assert assignments == [
        ("app/config.py", 'appointment_raw_compat_mode: Literal["audit", "header", "off"] ='),
    ]


def test_readiness_preflight_preserves_closed_gate_boundary():
    text = READINESS_PATH.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    assert "This preflight does not authorize:" in text
    for gate in REQUIRED_CLOSED_GATES:
        assert gate in text
    assert "does not prove runtime client behavior in a browser" in compact
    assert "route-intercepted smoke tests" in text
    assert "no mode change yet" in text
