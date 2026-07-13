import json
import os
import subprocess
import sys
from pathlib import Path

from orchestration_harness.deepcode_artifact import parse_artifact_marker
from scripts.ariadne_deepcode_liveness import _process_state, capture_snapshot, classify_liveness


def test_terminal_marker_parser_accepts_markdown_presentation_but_keeps_status_strict():
    assert parse_artifact_marker("notes\n## STATUS: complete\n", "completion")["valid"] is True
    assert parse_artifact_marker("notes\n**STATUS: complete**\n", "completion")["valid"] is True
    assert parse_artifact_marker("notes\nSTATUS: completed\n", "completion")["valid"] is False


def test_terminal_marker_parser_rejects_prose_earlier_conflicts_and_incomplete_artifacts():
    assert parse_artifact_marker("The expected STATUS: complete is documented here.\n", "completion")["valid"] is False
    assert parse_artifact_marker("STATUS: complete\nSTATUS: failed\n", "completion")["valid"] is False
    assert parse_artifact_marker("STATUS: complete\nMore work remains.\n" * 5, "completion")["valid"] is False


def test_terminal_marker_parser_preserves_pipe_decision_compatibility():
    body = "| Decision | **`DECISION: pass`** |\n\nEvidence follows.\n"
    parsed = parse_artifact_marker(body, "decision")

    assert parsed == {"valid": True, "marker": "DECISION: PASS", "reason": "terminal_marker_observed"}


def test_liveness_elapsed_time_does_not_classify_unchanged_state_as_failure(tmp_path: Path):
    before = capture_snapshot(tmp_path, Path("artifact.md"), Path("receipt.json"), Path("outbox"))
    after = dict(before)
    after["observed_at_epoch"] = before["observed_at_epoch"] + 3600

    result = classify_liveness(before, after)

    assert result["status"] == "idle_observed"
    assert result["changed_signals"] == []


def test_liveness_changed_file_and_artifact_signals_mean_progress_or_completion(tmp_path: Path):
    watched = tmp_path / "watched.txt"
    watched.write_text("before\n", encoding="utf-8")
    before = capture_snapshot(tmp_path, Path("artifact.md"), Path("receipt.json"), Path("outbox"), watched_files=[watched])
    watched.write_text("after\n", encoding="utf-8")
    after = capture_snapshot(tmp_path, Path("artifact.md"), Path("receipt.json"), Path("outbox"), watched_files=[watched])

    progressing = classify_liveness(before, after)
    assert progressing["status"] == "progressing"
    assert "files" in progressing["changed_signals"]

    (tmp_path / "artifact.md").write_text("## DECISION: pass\n", encoding="utf-8")
    completed = capture_snapshot(tmp_path, Path("artifact.md"), Path("receipt.json"), Path("outbox"))
    assert classify_liveness(after, completed)["status"] == "completed"


def test_liveness_git_signal_change_is_progress(tmp_path: Path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Synthetic Test"], check=True)
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "baseline"], check=True)
    before = capture_snapshot(tmp_path, Path("artifact.md"), Path("receipt.json"), Path("outbox"))
    tracked.write_text("after\n", encoding="utf-8")
    after = capture_snapshot(tmp_path, Path("artifact.md"), Path("receipt.json"), Path("outbox"))

    result = classify_liveness(before, after)

    assert result["status"] == "progressing"
    assert "git" in result["changed_signals"]


def test_liveness_reports_missing_process_without_terminating_anything():
    current = {
        "artifact": {"valid_marker": False},
        "processes": [{"pid": 99999999, "present": False}],
    }

    result = classify_liveness(None, current)

    assert result["status"] == "process_missing"


def test_liveness_reports_current_process_present():
    assert _process_state(os.getpid())["present"] is True


def test_transcript_is_redacted_and_bounded(tmp_path: Path):
    packet = tmp_path / "packet.md"
    packet.write_text("Synthetic packet.\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ariadne_deepcode_pty.py",
            "--cwd",
            str(tmp_path),
            "--packet",
            "packet.md",
            "--artifact",
            "artifact.md",
            "--outbox",
            "outbox",
            "--receipt",
            "receipt.json",
            "--fixture",
            "diagnostic_burst",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    receipt = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))
    transcript_path = tmp_path / receipt["terminal_transcript"]["path"]
    transcript = transcript_path.read_text(encoding="utf-8")

    assert result.returncode == 0
    assert "super-secret-token" not in transcript
    assert "sk-secret" not in transcript
    assert "[REDACTED]" in transcript
    assert len(transcript.encode("utf-8")) <= 65536
    assert len(transcript.splitlines()) <= 256
    assert receipt["terminal_transcript"]["redacted"] is True
    assert receipt["terminal_transcript"]["byte_truncated"] is True or receipt["terminal_transcript"]["event_count_truncated"] is True
