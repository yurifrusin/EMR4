"""Runtime isolation guards for the Bernie interpretation harness tooling."""

from pathlib import Path


APP_ROOT = Path("app")


def _app_python_sources():
    return sorted(APP_ROOT.rglob("*.py"))


def test_runtime_app_code_does_not_import_interpretation_harness_tooling():
    serialized = "\n".join(
        path.read_text(encoding="utf-8")
        for path in _app_python_sources()
    )

    for fragment in [
        "bernie_interpretation_harness_report",
        "bernie_interpretation_runtime_gate_check",
        "bernie_interpretation_readiness_check",
        "bernie-interpretation-harness-runtime-gate",
        "bernie_interpretation_harness",
    ]:
        assert fragment not in serialized


def test_runtime_app_code_does_not_reference_interpretation_fixture_paths():
    serialized = "\n".join(
        path.read_text(encoding="utf-8").casefold()
        for path in _app_python_sources()
    )

    for fragment in [
        "tests/fixtures/bernie_interpretation_harness",
        "tests\\fixtures\\bernie_interpretation_harness",
        "projected_frame_contracts.json",
        "authored_utterance_actions.json",
        "adversarial_utterance_actions.json",
        "clarification_actions.json",
        "receptionist_phrase_actions.json",
    ]:
        assert fragment not in serialized


def test_runtime_app_code_does_not_reference_historical_diary_gate_material():
    serialized = "\n".join(
        path.read_text(encoding="utf-8").casefold()
        for path in _app_python_sources()
    )

    for fragment in [
        "h15_semantic_candidates",
        "h_series_profiles",
        "historical_diary_semantic_candidate_builder",
        "local_data",
        "historical-diary-trove",
    ]:
        assert fragment not in serialized
