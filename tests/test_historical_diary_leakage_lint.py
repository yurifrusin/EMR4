from pathlib import Path

import pytest

from scripts.historical_diary_leakage_lint import (
    HistoricalDiaryLeakageLintError,
    assert_no_leakage,
    lint_text,
)


def reasons_for(text: str, path: str = "tests/test_h_series_example.py") -> str:
    issues = lint_text(Path(path), text)
    return " ".join(issue.reason for issue in issues)


def test_leakage_lint_accepts_policy_context_that_names_forbidden_examples():
    text = """
FORBIDDEN_PROMOTION_WORDS = {
    "booked",
    "patient arrived",
}

This policy says small_content_delta must not be interpreted as a booked appointment.
"""

    assert lint_text(Path("docs/historical-diary-policy.md"), text) == []


def test_leakage_lint_rejects_docstring_semantic_drift():
    text = '''
def test_h_series_profile_safe():
    """small_content_delta means a normal surgery day."""
'''

    assert "neutral H-series class" in reasons_for(text)


def test_leakage_lint_rejects_semantic_promotion_phrase_in_relevant_fixture():
    text = """
id: h21_profile
notes: patient arrived
"""

    assert "semantic promotion wording" in reasons_for(
        text,
        "tests/fixtures/h_series_profiles/example.yaml",
    )


def test_leakage_lint_rejects_test_names_that_combine_h_series_and_booking():
    text = "def test_h_series_profile_booking_implication():\n    pass\n"

    assert "test name combines" in reasons_for(text)


def test_leakage_lint_rejects_deterministic_uses_as_permission_switch():
    text = 'deterministic_uses: "allows stricter booking assertions"\n'

    assert "deterministic_uses must stay metadata" in reasons_for(
        text,
        "tests/fixtures/h_series_profiles/example.yaml",
    )


def test_assert_no_leakage_raises_for_file_path(tmp_path):
    lint_path = tmp_path / "test_h_series_profile.py"
    lint_path.write_text(
        'def test_h_series_profile_booking_implication():\n    pass\n',
        encoding="utf-8",
    )

    with pytest.raises(HistoricalDiaryLeakageLintError):
        assert_no_leakage([lint_path])
