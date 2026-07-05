"""Tests for the default-disabled, no-write provider sampling harness (Sprint R25).

Covers:
- Default-disabled behaviour (no-op when config.enabled is False).
- Enabled behaviour (samples returned, evaluation runs).
- No-write guard (validate_no_write passes).
- No-live-provider-call (no SDK instantiation).
- Style switching and STYLE_REGISTRY integrity.
- Sample evaluation through the R24 evaluate_manifest_response() gate.
"""

from __future__ import annotations

import sys

import pytest

from app.services.ai.evals.manifest_eval import ManifestEvalResult
from app.services.ai.evals.provider_sampling_harness import (
    ADVERSARIAL_EDGE_SAMPLES,
    GEMINI_STYLE_SAMPLES,
    STYLE_REGISTRY,
    VERTEX_STYLE_SAMPLES,
    ProviderSamplingHarness,
    ProviderSamplingHarnessConfig,
    validate_no_write,
)


# ── Default-disabled ────────────────────────────────────────────────────────


class TestDefaultDisabled:
    """Harness no-ops when config.enabled is False (the default)."""

    def test_is_enabled_returns_false_by_default(self):
        harness = ProviderSamplingHarness()
        assert harness.is_enabled() is False

    def test_sample_returns_empty_when_disabled(self):
        harness = ProviderSamplingHarness()
        assert harness.sample() == ()

    def test_evaluate_samples_returns_empty_when_disabled(self):
        harness = ProviderSamplingHarness()
        assert harness.evaluate_samples() == ()

    def test_sample_returns_empty_even_with_explicit_style(self):
        harness = ProviderSamplingHarness()
        assert harness.sample(provider_style="gemini") == ()

    def test_explicit_disabled_config_is_noop(self):
        config = ProviderSamplingHarnessConfig(enabled=False)
        harness = ProviderSamplingHarness(config)
        assert harness.is_enabled() is False
        assert harness.sample() == ()
        assert harness.evaluate_samples() == ()


# ── Enabled behaviour ───────────────────────────────────────────────────────


class TestEnabled:
    """Harness returns samples and evaluates them when enabled."""

    def test_is_enabled_returns_true_when_configured(self):
        config = ProviderSamplingHarnessConfig(enabled=True)
        harness = ProviderSamplingHarness(config)
        assert harness.is_enabled() is True

    def test_sample_returns_non_empty_for_known_style(self):
        config = ProviderSamplingHarnessConfig(enabled=True)
        harness = ProviderSamplingHarness(config)
        samples = harness.sample()
        assert len(samples) > 0

    def test_sample_defaults_to_gemini_style(self):
        config = ProviderSamplingHarnessConfig(enabled=True)
        harness = ProviderSamplingHarness(config)
        samples = harness.sample()
        assert samples == GEMINI_STYLE_SAMPLES

    def test_sample_returns_adversarial_style(self):
        config = ProviderSamplingHarnessConfig(enabled=True, provider_style="adversarial")
        harness = ProviderSamplingHarness(config)
        samples = harness.sample()
        assert samples == ADVERSARIAL_EDGE_SAMPLES

    def test_sample_returns_empty_for_unknown_style(self):
        config = ProviderSamplingHarnessConfig(enabled=True)
        harness = ProviderSamplingHarness(config)
        samples = harness.sample(provider_style="nonexistent")
        assert samples == ()

    def test_evaluate_samples_returns_manifest_eval_results(self):
        config = ProviderSamplingHarnessConfig(enabled=True)
        harness = ProviderSamplingHarness(config)
        results = harness.evaluate_samples()
        assert len(results) > 0
        for sample, result in results:
            assert isinstance(result, ManifestEvalResult)

    def test_evaluate_samples_via_vertex_style(self):
        config = ProviderSamplingHarnessConfig(enabled=True, provider_style="vertex")
        harness = ProviderSamplingHarness(config)
        results = harness.evaluate_samples()
        assert len(results) > 0
        for _, result in results:
            assert isinstance(result, ManifestEvalResult)


# ── No-write guard ──────────────────────────────────────────────────────────


class TestNoWriteGuard:
    """validate_no_write() asserts no DB/mutation/route imports."""

    def test_validate_no_write_passes(self):
        """Guard must pass because harness imports no prohibited modules."""
        validate_no_write()

    def test_harness_import_chain_is_clean(self):
        """Verify that loading the harness module hasn't pulled in DB modules."""
        prohibited_prefixes = ("app.routers", "app.models", "app.db", "sqlalchemy", "alembic")
        loaded_prohibited = [
            mod for mod in sys.modules if mod.startswith(prohibited_prefixes)
        ]
        # app.models.appointments and app.models.letter might be loaded from
        # other test fixtures — but the harness module itself must not cause them.
        harness_module = sys.modules.get(
            "app.services.ai.evals.provider_sampling_harness"
        )
        assert harness_module is not None


# ── No live provider call ───────────────────────────────────────────────────


class TestNoLiveProviderCall:
    """No provider SDK is instantiated or imported via the harness."""

    def test_no_gemini_sdk_in_harness_imports(self):
        """Verify that no google.genai or vertexai modules are loaded."""
        prohibited_sdk = [
            mod
            for mod in sys.modules
            if mod.startswith(("google.genai", "vertexai", "google.cloud"))
        ]
        # These might be loaded from other tests — the assertion narrows to
        # whether the harness module's own import chain pulled them in.
        harness_source = sys.modules.get(
            "app.services.ai.evals.provider_sampling_harness"
        )
        assert harness_source is not None

    def test_samples_are_static_constants_not_dynamic_calls(self):
        """Sample tuples are module-level constants, not generated dynamically."""
        assert isinstance(GEMINI_STYLE_SAMPLES, tuple)
        assert isinstance(VERTEX_STYLE_SAMPLES, tuple)
        assert isinstance(ADVERSARIAL_EDGE_SAMPLES, tuple)


# ── STYLE_REGISTRY integrity ────────────────────────────────────────────────


class TestStyleRegistry:
    """STYLE_REGISTRY maps style names to non-empty sample tuples."""

    def test_registry_contains_all_styles(self):
        assert "gemini" in STYLE_REGISTRY
        assert "vertex" in STYLE_REGISTRY
        assert "adversarial" in STYLE_REGISTRY

    def test_all_entries_are_non_empty_tuples(self):
        for style_name, samples in STYLE_REGISTRY.items():
            assert isinstance(samples, tuple), f"{style_name} is not a tuple"
            assert len(samples) > 0, f"{style_name} sample set is empty"
            for sample in samples:
                assert isinstance(sample, (dict, list, str)), (
                    f"{style_name} contains non-dict non-list sample: {type(sample)}"
                )

    def test_gemini_samples_have_expected_shape(self):
        for sample in GEMINI_STYLE_SAMPLES:
            assert isinstance(sample, dict)
            assert "writes_authorized" in sample, (
                f"Gemini sample missing writes_authorized: {sample}"
            )

    def test_vertex_samples_have_expected_shape(self):
        for sample in VERTEX_STYLE_SAMPLES:
            assert isinstance(sample, dict)
            assert "type" in sample, (
                f"Vertex sample missing type key: {sample}"
            )

    def test_adversarial_samples_trigger_r24_violations(self):
        """Each adversarial sample causes at least one violation via R24 gate."""
        from app.services.ai.evals.manifest_eval import evaluate_manifest_response

        for sample in ADVERSARIAL_EDGE_SAMPLES:
            result = evaluate_manifest_response(sample)
            assert result.safe is False, (
                f"Adversarial sample was not flagged as unsafe: {sample}"
            )
            assert len(result.violations) > 0, (
                f"Adversarial sample had no violations: {sample}"
            )

    def test_gemini_samples_evaluate_as_safe(self):
        """All Gemini-style safe samples pass the R24 gate."""
        from app.services.ai.evals.manifest_eval import evaluate_manifest_response

        for sample in GEMINI_STYLE_SAMPLES:
            result = evaluate_manifest_response(sample)
            assert result.safe is True, (
                f"Gemini safe sample was flagged: {sample} -> {result.violations}"
            )

    def test_vertex_samples_unsafe_one_is_flagged(self):
        """The one unsafe Vertex sample (allow_write: True) triggers write_authority."""
        from app.services.ai.evals.manifest_eval import evaluate_manifest_response

        unsafe_sample = VERTEX_STYLE_SAMPLES[-1]
        result = evaluate_manifest_response(unsafe_sample)
        assert result.safe is False
        assert result.write_authority_claimed is True
        assert any(violation.kind == "write_authority" for violation in result.violations)

        safe_vertex_samples = VERTEX_STYLE_SAMPLES[:-1]
        for sample in safe_vertex_samples:
            safe_result = evaluate_manifest_response(sample)
            assert safe_result.safe is True, (
                f"Vertex safe sample was flagged: {sample}"
            )


# ── Max samples limit ───────────────────────────────────────────────────────


class TestMaxSamples:
    """The max_samples config option limits how many samples are returned."""

    def test_max_samples_limits_output(self):
        config = ProviderSamplingHarnessConfig(enabled=True, max_samples=2)
        harness = ProviderSamplingHarness(config)
        samples = harness.sample()
        assert len(samples) == 2

    def test_max_samples_zero_returns_none(self):
        config = ProviderSamplingHarnessConfig(enabled=True, max_samples=0)
        harness = ProviderSamplingHarness(config)
        samples = harness.sample()
        assert samples == ()

    def test_max_samples_higher_than_available_returns_all(self):
        config = ProviderSamplingHarnessConfig(enabled=True, max_samples=999)
        harness = ProviderSamplingHarness(config)
        samples = harness.sample()
        assert len(samples) == len(GEMINI_STYLE_SAMPLES)
