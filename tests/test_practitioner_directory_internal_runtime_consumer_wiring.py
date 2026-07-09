from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
APPROVAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-internal-runtime-consumer-approval.json"
)


def _js() -> str:
    return DIARY_JS.read_text(encoding="utf-8")


def test_diary_selector_uses_approved_route_through_api_fetch():
    js = _js()

    assert 'apiFetch("/practice/practitioners?activeOnly=true&limit=200")' in js
    assert 'fetch(`${API_BASE}/practice/practitioners' not in js
    assert "activePractitionerDirectory = normalizePractitionerDirectory" in js


def test_diary_selector_consumes_display_safe_practitioner_fields_only():
    section = _js().split("function normalizePractitionerDirectory", 1)[1].split(
        "function resolvePractitionerSelection", 1
    )[0]

    assert "row.id" in section
    assert "row.displayName" in section
    assert "row.defaultLocation" in section
    for forbidden in (
        "provider_number",
        "prescriber_number",
        "ahpra_number",
        "hpi_i",
        "email",
        "phone",
        "address",
    ):
        assert forbidden not in section


def test_diary_selector_prefers_route_directory_and_keeps_legacy_fallback():
    js = _js()
    dropdown = js.split("function populatePractitionerDropdown", 1)[1].split(
        "function populateTypeDropdown", 1
    )[0]

    assert "activePractitionerDirectory.length > 0" in dropdown
    assert "canUseDirectorySelection" in dropdown
    assert "opt.value = practitioner.id" in dropdown
    assert "opt.textContent = practitioner.defaultLocationName" in dropdown
    assert "activeTemplate.columns.forEach" in dropdown
    assert "opt.value = col.practitioner_ahpra" in dropdown


def test_diary_save_resolves_route_id_or_legacy_ahpra_selection():
    js = _js()

    assert "function resolvePractitionerSelection" in js
    assert "activePractitionerDirectory.find" in js
    assert "return ahpraToPractitionerMap[selected] || null" in js
    assert "const practitionerSelection = document.getElementById(\"booking-practitioner\").value" in js
    assert "const practitioner = resolvePractitionerSelection(practitionerSelection)" in js
    assert "practitioner_id: practitioner.id" in js


def test_approval_packet_names_this_only_runtime_consumer():
    import json

    payload = json.loads(APPROVAL.read_text(encoding="utf-8"))

    assert payload["authorized_runtime_consumers"] == [
        "office_addin_diary_booking_practitioner_selector"
    ]
    assert payload["approved_consumer"][0]["consumption_mode"] == "http_through_existing_route"
