from pathlib import Path


DIARY_JS = Path("docs/diary/diary.js")


def _source() -> str:
    return DIARY_JS.read_text(encoding="utf-8")


def test_dev_and_smoke_capabilities_are_local_only() -> None:
    source = _source()
    assert "function isLocalHarnessHost()" in source
    assert 'function isLocalHarnessCapabilityEnabled(param)' in source
    assert 'return isLocalHarnessCapabilityEnabled("smoke");' in source
    assert 'isLocalHarnessCapabilityEnabled("bernie_debug")' in source
    assert 'isLocalHarnessCapabilityEnabled("bernie_dev_review")' in source
    assert 'window.location.protocol === "file:"' in source


def test_ngrok_backend_selection_uses_approved_domain_suffixes() -> None:
    source = _source()
    assert "function isApprovedNgrokHostname(hostname)" in source
    assert 'window.location.hostname.includes("ngrok")' not in source
    for suffix in (".ngrok-free.dev", ".ngrok-free.app", ".ngrok.app", ".ngrok.io"):
        assert f'"{suffix}"' in source


def test_client_identifiers_never_fall_back_to_math_random() -> None:
    source = _source()
    assert "Math.random" not in source
    assert "crypto.getRandomValues" in source
    assert "Secure random identifier generation is unavailable" in source


def test_confirmation_posts_use_the_canonical_allowlist() -> None:
    source = _source()
    assert "const ALLOWED_CONFIRM_ENDPOINT_PATHS = new Set([" in source
    for path in (
        "/appointments/proposals/create/confirm",
        "/appointments/proposals/create/confirm-bernie",
        "/appointments/proposals/update/confirm",
        "/appointments/proposals/status-confirm",
        "/appointments/proposals/delete-confirm",
    ):
        assert f'"{path}"' in source
    assert source.count("apiFetch(allowlistedConfirmApiPath(") == 7
    assert "apiFetch(normalizeApiPath(confirmEndpoint)" not in source
    assert "apiFetch(normalizeApiPath(payload.confirm_endpoint)" not in source
    assert "apiFetch(normalizeApiPath(envelope.confirm_endpoint)" not in source


def test_appointment_selection_avoids_identifier_selector_construction() -> None:
    source = _source()
    assert "function findAppointmentElementById(appointmentId)" in source
    assert "CSS.escape" not in source
    assert 'document.querySelector(`[data-id="${' not in source
    assert 'document.querySelector(`.appt[data-id="${' not in source
