"""Direct prospective scope checks; source author has not executed them."""

from orchestration_harness import bounded_g1b, raisa_policy


def test_interactive_operation_paths_are_exact_and_separate():
    assert bounded_g1b.operation_paths("enable_g4_stage1_interactive") == (
        bounded_g1b.G4_STAGE1_INTERACTIVE_CONTROL)
    assert bounded_g1b.operation_paths("implement_g4_stage1_interactive") == (
        bounded_g1b.G4_STAGE1_INTERACTIVE_PRODUCT)
    assert len(bounded_g1b.G4_STAGE1_INTERACTIVE_PRODUCT) == 12
    assert len(bounded_g1b.G4_STAGE1_INTERACTIVE_CONTROL) == 8
    assert bounded_g1b.G4_STAGE1_INTERACTIVE_PRODUCT.isdisjoint(
        bounded_g1b.G4_PATIENT_REQUEST_PRODUCT)


def test_old_staff_and_request_routes_remain_distinct():
    assert bounded_g1b.operation_paths("implement_g4_staff_move") == (
        bounded_g1b.G4_PRODUCT)
    assert bounded_g1b.operation_paths("implement_g4_patient_request") == (
        bounded_g1b.G4_PATIENT_REQUEST_PRODUCT)
    assert raisa_policy.g4_stage1_interactive_profile()["allowed_paths"] == list(
        raisa_policy.G4_STAGE1_INTERACTIVE_PRODUCT_PATHS)
    assert raisa_policy.g4_stage1_interactive_profile()[
        "expected_gate_status"] == "active_bounded_stage1_interactive"


def test_reviewed_source_entry_does_not_grant_runtime():
    profile = raisa_policy.g4_stage1_interactive_profile()
    assert profile["admitted_task_classes"] == ["g4_stage1_local_interactive"]
    assert "audio_capture_or_processing" not in profile["allowed_effects"]
    assert "provider_invocation" not in profile["allowed_effects"]
    assert bounded_g1b.G4_STAGE1_INTERACTIVE_SELECTED_BASE == {
        "commit": "91cd4898ed4f8a066a03d5af88661f92f4cb2b8e",
        "tree": "74d51d82b9ea191a6125609cd2bc2b36656a7443",
    }
    assert bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_EFFECT_SHA256 == (
        "d1b4220d8f2cb476f45ed1a5468b160f920f7ff1413dda102ccbcc1cf0c330a3")


def _owned_profile_map():
    from pathlib import Path
    import yaml
    overlay = Path(__file__).parents[1] / "orchestration/harness_settings/programme_recovery.yaml"
    return yaml.safe_load(overlay.read_bytes())["profiles"]


def test_interactive_profile_shape_accepts_new_and_historical_prestate():
    from orchestration_harness import configuration_core
    profiles = _owned_profile_map()
    assert "G4_STAGE1_LOCAL_INTERACTIVE" in profiles
    configuration_core.validate_shape(profiles, raisa_policy._SHAPE_79)
    historical = dict(profiles)
    historical.pop("G4_STAGE1_LOCAL_INTERACTIVE")
    configuration_core.validate_shape(historical, raisa_policy._SHAPE_79)


def test_profile_shape_rejects_unknown_profile_and_malformed_known_profile():
    from copy import deepcopy
    from orchestration_harness import configuration_core
    original = _owned_profile_map()
    unknown = deepcopy(original)
    unknown["G4_STAGE1_UNREVIEWED"] = deepcopy(original["G4_STAGE1_LOCAL_INTERACTIVE"])
    malformed = deepcopy(original)
    malformed["G4_STAGE1_LOCAL_INTERACTIVE"]["allowed_effects"] = True
    for profiles in (unknown, malformed):
        try:
            configuration_core.validate_shape(profiles, raisa_policy._SHAPE_79)
        except configuration_core.ConfigurationError as error:
            assert error.reason_code == "configuration_schema_invalid"
        else:
            raise AssertionError("Unreviewed or malformed profile was accepted")