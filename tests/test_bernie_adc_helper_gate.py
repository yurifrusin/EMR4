from __future__ import annotations

from pathlib import Path


SCRIPT = Path("scripts/use_bernie_adc.ps1")
RUN_DEV = Path("run_dev.ps1")


def test_bernie_adc_helper_keeps_fake_provider_by_default() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "[switch]$EnableLiveProvider" in source
    assert '$env:BERNIE_BOOKING_INTERPRETER_PROVIDER = "fake"' in source
    assert '$env:BERNIE_BOOKING_INTERPRETER_PROVIDER = "gemini_vertex"' in source
    assert "runtime/provider gate is currently blocked" in source
    assert "backend will fail closed" in source


def test_run_dev_diary_surface_keeps_fake_provider_by_default() -> None:
    source = RUN_DEV.read_text(encoding="utf-8")

    assert "[switch]$EnableLiveProvider" in source
    assert "-SkipAdcLoginForSurface ([bool]$SkipAdcLogin)" in source
    assert '$scriptArgs["SkipAdcLogin"] = $true' in source
    assert "if ($SkipAdcLoginForSurface)" in source
    assert '$provider = if ($EnableLiveProviderForDiary) { "gemini_vertex" } else { "fake" }' in source
    assert "-EnableLiveProvider # approved live-provider smoke only" in source
    assert "Bernie diary review with fake provider" in source
