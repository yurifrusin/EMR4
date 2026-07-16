from pathlib import Path

from app.services.bernie.lc4v6_postrun_validation import validate_consumed_attempt


STATE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "orchestration"
    / "agent_inbox"
    / "codex"
)


def test_permanently_consumed_lc4v6_attempt_is_valid() -> None:
    result = validate_consumed_attempt(STATE_ROOT)
    assert result.valid, result.errors
