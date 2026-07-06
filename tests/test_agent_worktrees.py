from scripts.agent_worktrees import (
    HANDOFF_REF,
    build_parser,
    create_codex_review_packet,
    read_task_status,
    task_completion_notes,
)


def test_review_packet_copies_worker_completion_notes(tmp_path):
    task = tmp_path / "worker-task.md"
    task.write_text(
        """# worker-task

## Completion Notes

- Files changed:
  - `seed.py`
- Verification run:
  - `pytest tests/test_diary_roster.py` -> 18 passed
- Remaining risks:
  - Test DB teardown can deadlock under rapid reruns.
""",
        encoding="utf-8",
    )

    notes = task_completion_notes(task)
    path = create_codex_review_packet(
        "claude",
        "worker-task",
        "claude/current",
        "Ready for review",
        notes,
        tmp_path,
    )

    text = path.read_text(encoding="utf-8")
    assert "## Worker Completion Notes" in text
    assert "`seed.py`" in text
    assert "18 passed" in text
    assert "teardown can deadlock" in text


def test_placeholder_completion_notes_are_treated_as_empty(tmp_path):
    task = tmp_path / "worker-task.md"
    task.write_text(
        """# worker-task

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
""",
        encoding="utf-8",
    )

    assert task_completion_notes(task) == ""


def test_read_task_status_tolerates_legacy_non_utf8_bytes(tmp_path):
    task = tmp_path / "legacy-packet.md"
    task.write_bytes(
        b"""# legacy-packet

| Item | Value |
|---|---|
| Status | queued |

Legacy smart dash byte: \x97
"""
    )

    assert read_task_status(task) == "queued"


def test_realign_defaults_to_handoff_ref():
    parser = build_parser()

    args = parser.parse_args(["realign", "--agent", "claude"])

    assert args.ref == HANDOFF_REF
    assert args.no_push is False


def test_realign_accepts_explicit_ref_override():
    parser = build_parser()

    args = parser.parse_args(["realign", "--agent", "claude", "--ref", "custom/ref", "--no-push"])

    assert args.ref == "custom/ref"
    assert args.no_push is True
