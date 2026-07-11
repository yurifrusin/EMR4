from pathlib import Path

import pytest

from orchestration_harness.deepcode_mailbox import build_notify_event, write_notify_event


def _environment(**overrides: str) -> dict[str, str]:
    values = {
        "STATUS": "completed",
        "DURATION": "12",
        "FAIL_REASON": "",
        "BODY": "DECISION: pass",
        "TITLE": "Verifier",
    }
    values.update(overrides)
    return values


def test_deepcode_notify_event_is_local_untrusted_output():
    event = build_notify_event(_environment())

    assert event["source"] == "deepcode_notify"
    assert event["body"] == "DECISION: pass"
    assert event["trust"] == "untrusted_worker_output_requires_packet_artifact_validation"


@pytest.mark.parametrize("environment", [_environment(STATUS="unknown"), _environment(DURATION="many")])
def test_deepcode_notify_event_fails_closed_for_invalid_hook_state(environment: dict[str, str]):
    with pytest.raises(ValueError):
        build_notify_event(environment)


def test_deepcode_notify_event_writes_only_to_requested_local_outbox(tmp_path: Path):
    path = write_notify_event(outbox=tmp_path / "outbox", environ=_environment())

    assert path.parent == tmp_path / "outbox"
    assert path.suffix == ".json"
    assert "DECISION: pass" in path.read_text(encoding="utf-8")
