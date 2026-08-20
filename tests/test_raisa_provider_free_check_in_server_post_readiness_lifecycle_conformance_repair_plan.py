from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-check-in-server-post-readiness-exit-state-and-"
    "stdin-lifecycle-conformance-repair-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-check-in-server-post-readiness-exit-"
    "state-and-stdin-lifecycle-conformance-repair-threat-model-delta.md"
)


def test_plan_freezes_exact_operation_and_full_git_sources() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    assert (
        "`raisa-provider-free-check-in-server-post-readiness-exit-state-and-"
        "stdin-lifecycle-conformance-repair`" in text
    )
    assert "`2ebb05ebaf28cc4978e1f21bf8a7340fb6ee44bd`" in text
    assert "`905184b76f576006232fcfdc78da71d98fcf0ca0`" in text
    assert "`03b94136c9c6cd82d5a8098705f263ba34a20de4`" in text
    assert "full 40-character commit" in text


def test_plan_keeps_attempt_006_and_provider_execution_closed() -> None:
    normalized = " ".join(PLAN.read_text(encoding="utf-8").split())
    assert "Attempt 006 is not authorised" in normalized
    assert "provider-disabled" in normalized
    assert "zero model, provider, network, Docker or database request" in normalized
    assert "Dedicated check-in remains default-off" in normalized
    assert "generic status does not gain `Arrived`" in normalized


def test_plan_freezes_stdin_and_closed_diagnostic_semantics() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for token in (
        "open_after_delivery",
        "closed_before_verification",
        "projection_valid",
        "state_error_empty",
        "attachment_process",
        "attachment_stdin",
    ):
        assert token in text
    assert "close the parent stdin handle exactly once" in text
    assert "No raw `State.Error`" in text


def test_plan_freezes_split_native_mount_coordinates_and_generator_controls() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for token in (
        "PRESET_DISCOVERY_PASSED",
        "PRESET_RESOLUTION_PASSED",
        "PRESET_STANDING_PASSED",
        "PRESET_SCOPE_BINDING_PASSED",
        "EFFECTIVE_TOOL_VIEW_PASSED",
        "PRESET_SUBSTAGE_INSTRUMENTATION_UNAVAILABLE",
        "dependency manifest",
        "baseline and terminal SHA-256 maps",
        "schema-owned artifact role",
    ):
        assert token in text
    assert "length-limited renderer" in normalized


def test_threat_delta_preserves_closed_surfaces() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    assert "No attempt 006" in text
    assert "No raw exception or model/provider boundary is trusted" in text
    assert "protected-ref movement is authorised" in text
