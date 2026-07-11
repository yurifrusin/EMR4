"""Tests that pin the committed Deep Code adapter contract.

These tests assert the contract values declared in ``orchestration/harness_settings/``:

* Default ``deepseek-v4-flash`` / ``high`` reasoning
* Exceptional ``deepseek-v4-pro`` (model) / ``max`` (reasoning)
* Real interactive TTY is required; non-TTY refusal is adapter unavailability,
  not model unavailability
* Durable packet artifact is the only accepted completion evidence
* Interactive permission approval is a transport decision and does NOT grant
  integration authority

Each test loads the corresponding YAML profile and asserts the pinned value.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

HARNESS_SETTINGS = Path(__file__).resolve().parent.parent / "orchestration" / "harness_settings"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_yaml(name: str) -> dict:
    path = HARNESS_SETTINGS / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing harness settings file: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# deepcode_model_profile.yaml — core model, TTY, artifact, and permission
#   contracts
# ---------------------------------------------------------------------------


class TestDeepCodeModelProfile:
    """Pin every committed field in ``deepcode_model_profile.yaml``."""

    PROFILE = _load_yaml("deepcode_model_profile.yaml")

    # -- Model defaults -------------------------------------------------

    def test_default_model_is_deepseek_v4_flash(self):
        assert self.PROFILE["models"]["default"] == "deepseek-v4-flash"

    def test_default_reasoning_is_high(self):
        assert self.PROFILE["reasoning"]["default"] == "high"

    def test_allowed_models_include_flash_and_pro(self):
        assert self.PROFILE["models"]["allowed"] == [
            "deepseek-v4-flash",
            "deepseek-v4-pro",
        ]

    def test_allowed_reasoning_includes_high_and_max(self):
        assert self.PROFILE["reasoning"]["allowed"] == ["high", "max"]

    # -- Exceptional-use-only surfaces ----------------------------------

    def test_pro_model_is_exceptional_use_only(self):
        assert self.PROFILE["models"]["exceptional_use_only"] == [
            "deepseek-v4-pro"
        ]

    def test_max_reasoning_is_exceptional_use_only(self):
        assert self.PROFILE["reasoning"]["exceptional_use_only"] == ["max"]

    # -- Interactive TTY requirement ------------------------------------

    def test_execution_mode_requires_real_tty(self):
        assert (
            self.PROFILE["execution_mode"] == "interactive_tty_required"
        )

    def test_non_tty_posture_is_adapter_unavailability_not_model(self):
        """Non-TTY refusal must be treated as adapter surface
        unavailability, never as model unavailability."""
        assert (
            self.PROFILE["non_tty_posture"]
            == "adapter_unavailable_for_current_execution_surface"
        )

    # -- Durable artifact contract --------------------------------------

    def test_completion_contract_requires_durable_artifact(self):
        assert (
            self.PROFILE["completion_contract"]
            == "durable_artifact_required_before_result_is_accepted"
        )

    # -- Permission / integration boundary -------------------------------

    def test_permission_contract_does_not_grant_integration(self):
        """Interactive permission approval authorises a transport decision,
        not integration authority."""
        assert (
            self.PROFILE["permission_contract"]
            == "interactive_prompt_or_explicit_project_policy_required"
        )

    # -------------------------------------------------------------------
    # Negative assertions — values that must NOT appear
    # -------------------------------------------------------------------

    def test_non_tty_posture_is_not_raw_model_unavailable(self):
        """Non-TTY refusal must not be classified as model unavailability,
        even under an alternative field name."""
        posture = self.PROFILE["non_tty_posture"]
        assert "model_unavailable" not in posture
        assert posture != "model_unavailable"

    def test_permission_approval_is_not_integration_authority(self):
        """The permission_contract field must not contain 'integration'."""
        assert "integration" not in self.PROFILE["permission_contract"]

    def test_exceptional_model_is_not_in_default(self):
        """Exceptional-use-only deepseek-v4-pro must not appear in the
        default model slot."""
        assert self.PROFILE["models"]["default"] != "deepseek-v4-pro"

    def test_exceptional_reasoning_is_not_in_default(self):
        """Exceptional-use-only max must not appear in the default
        reasoning slot."""
        assert self.PROFILE["reasoning"]["default"] != "max"


# ---------------------------------------------------------------------------
# worker_pool.yaml — DeepSeek resource contract
# ---------------------------------------------------------------------------


class TestWorkerPoolDeepCodeContract:
    """Pin DeepSeek resource-level settings in ``worker_pool.yaml``."""

    POOL = _load_yaml("worker_pool.yaml")

    @property
    def _deepcode_resources(self) -> list[dict]:
        return [
            w
            for w in self.POOL["workers"]
            if w.get("transport") == "cli_interactive"
        ]

    def test_two_deepcode_resources_defined(self):
        assert len(self._deepcode_resources) == 2

    def test_verifier_and_worker_resource_ids_match(self):
        ids = sorted(r["resource_id"] for r in self._deepcode_resources)
        assert ids == [
            "deepseek-flash-verifier",
            "deepseek-flash-workers",
        ]

    def test_all_deepcode_resources_require_real_tty(self):
        for resource in self._deepcode_resources:
            quirks = resource.get("transport_quirks", [])
            assert "deepcode_real_tty_required" in quirks, (
                f"{resource['resource_id']} missing real-tty quirk"
            )

    def test_all_deepcode_resources_require_durable_artifact(self):
        for resource in self._deepcode_resources:
            quirks = resource.get("transport_quirks", [])
            assert "deepcode_tui_result_artifact_required" in quirks, (
                f"{resource['resource_id']} missing artifact quirk"
            )

    def test_all_deepcode_resources_default_model_is_flash(self):
        for resource in self._deepcode_resources:
            assert resource["default_model"] == "deepseek-v4-flash", (
                f"{resource['resource_id']} defaults to "
                f"{resource['default_model']}"
            )

    def test_all_deepcode_resources_default_reasoning_is_high(self):
        for resource in self._deepcode_resources:
            assert resource["default_reasoning"] == "high", (
                f"{resource['resource_id']} defaults to "
                f"{resource['default_reasoning']}"
            )

    def test_workers_have_separate_packet_quirk(self):
        """Worker lane resources require a distinct packet per lane."""
        for resource in self._deepcode_resources:
            quirks = resource.get("transport_quirks", [])
            if resource["resource_id"] == "deepseek-flash-workers":
                assert "separate_worker_packet_required" in quirks

    def test_all_deepcode_resources_deny_integration_authority(self):
        """Permission prompts are transport decisions, not integration
        authority."""
        for resource in self._deepcode_resources:
            quirks = resource.get("transport_quirks", [])
            assert "permission_prompts_are_not_authority" in quirks, (
                f"{resource['resource_id']} missing "
                f"permission_prompts_are_not_authority quirk"
            )

    # -- Negative assertions for worker pool -----------------------------

    def test_no_deepcode_resource_defaults_to_pro(self):
        """No DeepSeek resource must default to deepseek-v4-pro."""
        for resource in self._deepcode_resources:
            assert resource["default_model"] != "deepseek-v4-pro", (
                f"{resource['resource_id']} must not default to pro"
            )

    def test_verifier_does_not_have_separate_packet_quirk(self):
        """Only the worker lane (not the verifier) requires a separate
        packet per lane."""
        for resource in self._deepcode_resources:
            quirks = resource.get("transport_quirks", [])
            if resource["resource_id"] == "deepseek-flash-verifier":
                assert "separate_worker_packet_required" not in quirks


# ---------------------------------------------------------------------------
# transport_adapters.yaml — deepcode_cli adapter boundary
# ---------------------------------------------------------------------------


class TestTransportAdapterDeepCodeContract:
    """Pin the ``deepcode_cli`` transport adapter entry."""

    ADAPTERS = _load_yaml("transport_adapters.yaml")

    @property
    def _adapter(self) -> dict:
        for a in self.ADAPTERS["adapters"]:
            if a["adapter_id"] == "deepcode_cli":
                return a
        pytest.fail("deepcode_cli adapter not found in transport_adapters.yaml")

    def test_adapter_invocation_is_deepcode_prompt_tui(self):
        assert self._adapter["invocation"] == "deepcode_prompt_tui"

    def test_adapter_has_no_integration_authority(self):
        assert (
            self._adapter["authority_boundary"]
            == "interactive_cli_transport_only_no_integration_authority"
        )

    def test_adapter_resource_ids_are_correct(self):
        assert self._adapter["resource_ids"] == [
            "deepseek-flash-verifier",
            "deepseek-flash-workers",
        ]

    def test_adapter_prompt_entrypoint_matches_profile(self):
        assert self._adapter["prompt_entrypoint"] == "deepcode -p <packet>"

    # -- Negative assertions for adapter --------------------------------

    def test_adapter_is_not_orchestrator_boundary(self):
        """The deepcode_cli adapter must not claim orchestrator-level
        authority."""
        assert (
            self._adapter["authority_boundary"]
            != "protected_orchestrator_only"
        )

    def test_adapter_is_not_codex_primary(self):
        """The deepcode_cli adapter must not be confused with the primary
        session adapter."""
        assert self._adapter["platform"] == "deep_code"
        assert "codex" not in self._adapter["adapter_id"]
