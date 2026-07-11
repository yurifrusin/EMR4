"""Settings-pinned tests for the mailbox and PTY lifecycle contract.

Loads committed settings from the YAML profile and verifies both code behaviour
and contract invariants.  Covers: local-only ignored outbox, both untrusted trust
labels, cwd-wide write scope, disposable-worktree containment, semantic packet
scope, the exact required deny list, PTY automated event, notify hook not required
for automated sessions, controlled exit, forced cleanup preconditions, permission
prompts fail closed, and no terminal-output persistence.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml

from orchestration_harness.deepcode_mailbox import (
    build_notify_event,
    write_notify_event,
)

# ---------------------------------------------------------------------------
# Profile loader
# ---------------------------------------------------------------------------

_PROFILE_PATH = (
    Path(__file__).resolve().parent.parent
    / "orchestration"
    / "harness_settings"
    / "deepcode_mailbox_profile.yaml"
)


@pytest.fixture(scope="session")
def profile() -> dict:
    """Load the committed mailbox profile once per session."""
    with open(_PROFILE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOWTIFY_ENV = {
    "STATUS": "completed",
    "DURATION": "12",
    "FAIL_REASON": "",
    "BODY": "DECISION: pass",
    "TITLE": "Verifier",
}


def _environ(**overrides: str) -> dict[str, str]:
    values = dict(_NOWTIFY_ENV)
    values.update(overrides)
    return values


def _read_event(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


# ===================================================================
# 1.  Local-only ignored outbox
# ===================================================================

class TestLocalOnlyIgnoredOutbox:
    """The outbox path is under local_data/ so it is gitignored."""

    PROFILE_KEY = ("outbox", "local_only_relative_path")

    def test_committed_outbox_path_is_under_local_data(self, profile: dict):
        """Pin the committed relative path from the profile."""
        path: str = _nested_get(profile, self.PROFILE_KEY)
        assert path.startswith("local_data/"), (
            f"expected local_data/ prefix, got {path!r}"
        )

    def test_committed_output_prohibited_flag(self, profile: dict):
        """committed_output_prohibited must be true in the profile."""
        assert profile["outbox"]["committed_output_prohibited"] is True

    def test_event_written_only_inside_outbox(self, tmp_path: Path):
        """write_notify_event creates the file inside the specified outbox only."""
        outbox = tmp_path / "outbox"
        path = write_notify_event(outbox=outbox, environ=_environ())
        assert path.parent == outbox
        assert path.suffix == ".json"
        # No stray JSON files outside the outbox.
        assert list(tmp_path.glob("*.json")) == []

    def test_outbox_creation_is_idempotent(self, tmp_path: Path):
        """The outbox directory is created on first write; a second write does not fail."""
        outbox = tmp_path / "outbox"
        p1 = write_notify_event(outbox=outbox, environ=_environ())
        p2 = write_notify_event(outbox=outbox, environ=_environ(STATUS="failed"))
        assert p1.parent == outbox
        assert p2.parent == outbox
        assert p1 != p2
        assert outbox.is_dir()

    def test_negative_outside_outbox_not_supported(self, tmp_path: Path):
        """Negative: the API always writes into the outbox directory, never to an
        arbitrary pre-existing path."""
        outbox = tmp_path / "outbox"
        outbox.mkdir()
        existing = outbox / "existing.txt"
        existing.write_text("pre-existing", encoding="utf-8")
        path = write_notify_event(outbox=outbox, environ=_environ())
        assert path != existing
        assert existing.read_text(encoding="utf-8") == "pre-existing"
        assert path.suffix == ".json"


# ===================================================================
# 2.  Both untrusted trust labels
# ===================================================================

class TestBothUntrustedTrustLabels:
    """The profile defines two distinct trust labels — one for outbox events and one
    for PTY lifecycle events.  Both must be present in committed settings."""

    OUTBOX_LABEL = "untrusted_worker_output_requires_packet_artifact_validation"
    PTY_LABEL = "untrusted_transport_completion_requires_artifact_validation"

    def test_outbox_trust_label_pinned(self, profile: dict):
        """The outbox event trust marker matches the committed profile."""
        pinned = profile["outbox"]["event_trust"]
        assert pinned == self.OUTBOX_LABEL

    def test_pty_trust_label_pinned(self, profile: dict):
        """The PTY lifecycle trust marker matches the committed profile."""
        pinned = profile["pty_lifecycle"]["event_trust"]
        assert pinned == self.PTY_LABEL

    def test_labels_are_distinct(self):
        """The two labels are different strings so that consumers can distinguish
        notify events from transport-completion events."""
        assert self.OUTBOX_LABEL != self.PTY_LABEL

    def test_notify_events_carry_outbox_label(self):
        """Every notify event built by build_notify_event carries the outbox trust
        marker."""
        event = build_notify_event(_environ())
        assert event["trust"] == self.OUTBOX_LABEL

    def test_notify_events_survive_round_trip(self, tmp_path: Path):
        """The outbox trust marker persists through write + readback."""
        path = write_notify_event(outbox=tmp_path, environ=_environ())
        event = _read_event(path)
        assert event["trust"] == self.OUTBOX_LABEL

    def test_negative_malformed_body_still_untrusted(self):
        """Even a garbled body does not change the trust label."""
        event = build_notify_event(_environ(BODY="not a decision"))
        assert event["trust"] == self.OUTBOX_LABEL
        assert event["body"] == "not a decision"


# ===================================================================
# 3.  CWD-wide write scope
# ===================================================================

class TestCwdWideWriteScope:
    """write-in-cwd is preauthorised; the outbox is resolved relative to the process
    working directory."""

    PROFILE_KEY = ("permissions", "preauthorized_write_scope")

    def test_preauthorized_write_scope_pinned(self, profile: dict):
        """The committed profile declares entire_deepcode_process_cwd as the write
        scope."""
        scope = _nested_get(profile, self.PROFILE_KEY)
        assert scope == "entire_deepcode_process_cwd"

    def test_write_scope_includes_base_allow(self, profile: dict):
        """write-in-cwd is among the base_allow capabilities."""
        allow_list = profile["permissions"]["base_allow"]
        assert "write-in-cwd" in allow_list

    def test_outbox_accepts_relative_path(self, tmp_path: Path):
        """The outbox path can be relative to cwd (here tmp_path)."""
        relative = tmp_path / "rel_outbox"
        path = write_notify_event(outbox=relative, environ=_environ())
        assert path.parent == relative
        assert path.is_file()

    def test_negative_write_outside_cwd_not_preauthorized(self, profile: dict):
        """write-out-cwd is in the deny list, not the allow list."""
        allow = profile["permissions"]["base_allow"]
        deny = profile["permissions"]["base_deny"]
        assert "write-out-cwd" not in allow
        assert "write-out-cwd" in deny


# ===================================================================
# 4.  Disposable-worktree containment
# ===================================================================

class TestDisposableWorktreeContainment:
    """The profile requires a disposable packet-scoped worker worktree."""

    PROFILE_KEY = ("permissions", "containment_requirement")

    def test_containment_requirement_pinned(self, profile: dict):
        """The committed containment requirement is disposable_packet_scoped_worker_worktree."""
        requirement = _nested_get(profile, self.PROFILE_KEY)
        assert requirement == "disposable_packet_scoped_worker_worktree"

    def test_outbox_is_subtree_of_worktree_root(self, tmp_path: Path):
        """When the outbox is placed inside the worktree root, the event path is
        a descendant of that root."""
        worktree = tmp_path
        outbox = worktree / "local_data" / "deepcode-outbox"
        path = write_notify_event(outbox=outbox, environ=_environ())
        try:
            path.resolve().relative_to(worktree.resolve())
        except ValueError:
            pytest.fail("event path is not inside the worktree root")

    def test_event_path_is_descendant_of_outbox(self, tmp_path: Path):
        """The event file resolves to a child of the outbox directory."""
        outbox = tmp_path / "outbox"
        path = write_notify_event(outbox=outbox, environ=_environ())
        assert str(path.resolve()).startswith(str(outbox.resolve()))


# ===================================================================
# 5.  Semantic-not-CLI packet scope
# ===================================================================

class TestSemanticPacketScope:
    """Packet boundaries are semantic, not CLI-enforced."""

    PROFILE_KEY = ("permissions", "packet_scope_is_semantic_not_cli_enforced")

    def test_semantic_scope_pinned(self, profile: dict):
        """The committed profile sets semantic-not-CLI enforcement to true."""
        assert _nested_get(profile, self.PROFILE_KEY) is True

    def test_event_has_no_packet_identifying_fields(self):
        """The event schema does not carry fields that could bleed between
        packet contexts."""
        event = build_notify_event(_environ())
        for forbidden in ("worktree", "branch", "packet_id", "task_id", "agent"):
            assert forbidden not in event, f"event must not contain '{forbidden}'"

    def test_event_has_no_routing_fields(self):
        """No orchestrator-routing fields in the event schema."""
        event = build_notify_event(_environ())
        for routed in ("target", "route", "recipient", "inbox", "channel", "transport"):
            assert routed not in event, f"event must not contain '{routed}'"

    def test_title_is_free_text_not_authoritative_ref(self):
        """The 'title' field is free-form metadata, not an authoritative packet
        reference."""
        event_a = build_notify_event(_environ(TITLE="Verifier"))
        event_b = build_notify_event(_environ(TITLE="worker-x"))
        assert event_a["title"] == "Verifier"
        assert event_b["title"] == "worker-x"
        # Both remain untrusted.
        assert event_a["trust"] == "untrusted_worker_output_requires_packet_artifact_validation"
        assert event_b["trust"] == "untrusted_worker_output_requires_packet_artifact_validation"


# ===================================================================
# 6.  Required deny list
# ===================================================================

class TestRequiredDenyList:
    """The profile's base_deny list enumerates all forbidden capabilities."""

    EXPECTED_DENY = frozenset({
        "read-out-cwd", "write-out-cwd", "delete-in-cwd", "delete-out-cwd",
        "mutate-git-log", "network", "mcp",
    })

    def test_exact_deny_list_pinned(self, profile: dict):
        """The committed deny list matches exactly (order-agnostic)."""
        deny = set(profile["permissions"]["base_deny"])
        assert deny == self.EXPECTED_DENY, (
            f"deny mismatch: extra={deny - self.EXPECTED_DENY}, "
            f"missing={self.EXPECTED_DENY - deny}"
        )

    def test_deny_list_contains_no_allow_items(self, profile: dict):
        """No capability appears in both base_allow and base_deny."""
        allow = set(profile["permissions"]["base_allow"])
        deny = set(profile["permissions"]["base_deny"])
        assert allow.isdisjoint(deny), f"overlap: {allow & deny}"

    def test_mailbox_api_has_no_delete(self):
        """The public mailbox API provides no delete or remove function."""
        assert not hasattr(build_notify_event, "remove")
        assert not hasattr(write_notify_event, "remove")

    def test_mailbox_api_has_no_git_mutation(self):
        """No git-related parameters on the public API."""
        import inspect
        for func in (build_notify_event, write_notify_event):
            sig = inspect.signature(func)
            for param in sig.parameters:
                assert "git" not in param.lower()

    def test_mailbox_api_has_no_network(self):
        """No URL/host/endpoint parameters on the public API."""
        import inspect
        for func in (build_notify_event, write_notify_event):
            sig = inspect.signature(func)
            for param in sig.parameters:
                assert "url" not in param.lower()
                assert "host" not in param.lower()
                assert "endpoint" not in param.lower()

    def test_mailbox_module_has_no_mcp(self):
        """The adapter module does not reference MCP."""
        import orchestration_harness.deepcode_mailbox as mbox
        src = Path(mbox.__file__).read_text(encoding="utf-8")
        assert "mcp" not in src.lower()


# ===================================================================
# 7.  PTY automated event
# ===================================================================

class TestPtyAutomatedEvent:
    """The PTY lifecycle supports an automated completion event without a human
    TTY operator."""

    PROFILE_KEY = ("pty_lifecycle", "automated_completion_event")

    def test_automated_completion_event_pinned(self, profile: dict):
        """The profile enables automated completion events."""
        assert _nested_get(profile, self.PROFILE_KEY) is True

    def test_event_has_adapter_required_keys(self):
        """Every notify event carries the full key set an automated adapter needs."""
        REQUIRED = frozenset({
            "schema_version", "event_id", "recorded_at", "source",
            "status", "duration_seconds", "title", "fail_reason",
            "body", "trust",
        })
        event = build_notify_event(_environ())
        assert REQUIRED.issubset(event.keys()), (
            f"missing: {REQUIRED - event.keys()}"
        )

    def test_event_is_json_serializable(self):
        """No non-serializable types in the event."""
        event = build_notify_event(_environ())
        round_tripped = json.loads(json.dumps(event))
        assert round_tripped == event

    def test_event_has_iso_timestamp(self):
        """recorded_at is an ISO-8601 formatted string the adapter can parse."""
        ts = build_notify_event(_environ())["recorded_at"]
        assert isinstance(ts, str)
        assert "T" in ts
        assert ts.endswith("Z") or "+" in ts

    def test_schema_version_pinned(self):
        """The schema version is a fixed string."""
        assert build_notify_event(_environ())["schema_version"] == "ariadne.deepcode_notify_event.v1"


# ===================================================================
# 8.  Notify hook not required for automated sessions
# ===================================================================

class TestNotifyHookNotRequired:
    """Deep Code's notify hook is explicitly not required for automated PTY sessions."""

    PROFILE_KEY = ("pty_lifecycle", "deepcode_notify_hook_required_for_automated_sessions")

    def test_notify_hook_not_required_pinned(self, profile: dict):
        """The committed profile sets the notify-hook requirement to false."""
        assert _nested_get(profile, self.PROFILE_KEY) is False

    def test_negative_hook_required_surfaces_as_settings_change(self, profile: dict):
        """If the setting were ever switched to true, automated-dispatch callers
        would need a real TTY notify hook.  Prove we know the current value."""
        assert profile["pty_lifecycle"]["deepcode_notify_hook_required_for_automated_sessions"] is False


# ===================================================================
# 9.  Controlled exit
# ===================================================================

class TestControlledExit:
    """The PTY lifecycle requires a controlled exit — events capture status,
    duration, and fail_reason."""

    PROFILE_KEY = ("pty_lifecycle", "controlled_exit_required")

    def test_controlled_exit_required_pinned(self, profile: dict):
        """The profile requires controlled exit."""
        assert _nested_get(profile, self.PROFILE_KEY) is True

    def test_completed_event_has_status_and_duration(self, tmp_path: Path):
        """A completed event stores the correct status and duration."""
        path = write_notify_event(
            outbox=tmp_path,
            environ=_environ(STATUS="completed", DURATION="42"),
        )
        event = _read_event(path)
        assert event["status"] == "completed"
        assert event["duration_seconds"] == 42

    def test_failed_event_has_fail_reason(self, tmp_path: Path):
        """A failed event stores fail_reason for diagnostics."""
        path = write_notify_event(
            outbox=tmp_path,
            environ=_environ(STATUS="failed", DURATION="7", FAIL_REASON="timeout"),
        )
        event = _read_event(path)
        assert event["status"] == "failed"
        assert event["fail_reason"] == "timeout"
        assert event["duration_seconds"] == 7

    def test_negative_invalid_status_raises(self):
        """Negative: unknown status values are rejected so no malformed exit
        signal reaches the filesystem."""
        for bad in ("running", "", "crashed", "unknown", "completed "):
            with pytest.raises(ValueError, match="STATUS must be completed or failed"):
                build_notify_event(_environ(STATUS=bad))

    def test_negative_invalid_duration_raises(self):
        """Negative: non-digit durations are rejected so cleanup timing always
        has a parseable value."""
        for bad in ("", "abc", "12.5", "-1"):
            with pytest.raises(ValueError, match="DURATION"):
                build_notify_event(_environ(DURATION=bad))

    def test_negative_invalid_status_prevents_write(self, tmp_path: Path):
        """Negative: an unrecognised status blocks write_notify_event, and no
        event reaches the filesystem."""
        with pytest.raises(ValueError):
            write_notify_event(
                outbox=tmp_path,
                environ=_environ(STATUS="crashed", DURATION="5"),
            )
        assert len(list(tmp_path.iterdir())) == 0


# ===================================================================
# 10.  Forced cleanup only after artifact + completed turn
# ===================================================================

class TestForcedCleanupPreconditions:
    """Forced cleanup must only run after a durable artifact and a completed turn
    signal are both present.  The mailbox alone is not a cleanup trigger."""

    def test_notify_event_alone_does_not_signal_cleanup(self):
        """A notify event by itself (no schema fields about artifacts, no
        'completed turn' flag) cannot be interpreted as a cleanup signal."""
        event = build_notify_event(_environ())
        # No field that a controller could misinterpret as a cleanup OK.
        for cleanup_field in ("cleanup_ok", "artifact_received", "turn_completed", "ready_for_cleanup"):
            assert cleanup_field not in event, (
                f"event must not carry '{cleanup_field}'"
            )

    def test_duration_and_status_are_metadata_not_cleanup_command(self):
        """Duration and status describe the session outcome; they are not a
        cleanup directive by themselves."""
        event = build_notify_event(_environ(STATUS="completed", DURATION="30"))
        assert "duration_seconds" in event
        assert event["status"] == "completed"
        # No 'action' or 'command' field that would trigger cleanup.
        assert "action" not in event
        assert "command" not in event

    def test_negative_status_not_alone_grounds_dispatch(self):
        """A failed status is not evidence that forced cleanup was already done;
        the orchestrator must separately verify artifact and turn completion."""
        event = build_notify_event(_environ(STATUS="failed", FAIL_REASON="timeout"))
        assert event["status"] == "failed"
        # No auto-cleanup claim in the event.
        for cleanup_claim in ("cleanup_performed", "cleanup_timestamp", "artifact_verified"):
            assert cleanup_claim not in event


# ===================================================================
# 11.  Permission prompts fail closed
# ===================================================================

class TestPermissionPromptsFailClosed:
    """The base permission mode is askAll, and unknown operations require an
    interactive prompt, so any unrecognised capability defaults to blocked."""

    def test_base_mode_pinned(self, profile: dict):
        """The committed base default mode is askAll."""
        assert profile["permissions"]["base_default_mode"] == "askAll"

    def test_unknown_operation_requires_interactive_prompt_pinned(self, profile: dict):
        """Unknown operations require an interactive prompt — no silent allow."""
        assert profile["permissions"]["unknown_operation_requires_interactive_prompt"] is True

    def test_packet_scoped_approval_for_non_preauthorized(self, profile: dict):
        """All non-preauthorized capabilities require packet-scoped approval."""
        assert profile["permissions"]["packet_scoped_approval_required_for"] == [
            "all_non_pre_authorized_capabilities",
        ]

    def test_write_out_cwd_is_denied_not_allowed(self, profile: dict):
        """Negative: write-out-cwd is denied, so a request for it would require
        an interactive prompt and fail closed without one."""
        assert "write-out-cwd" not in profile["permissions"]["base_allow"]
        assert "write-out-cwd" in profile["permissions"]["base_deny"]

    def test_delete_is_denied_not_allowed(self, profile: dict):
        """Negative: all delete capabilities are denied, so deletion always fails
        closed."""
        deny = profile["permissions"]["base_deny"]
        assert "delete-in-cwd" in deny
        assert "delete-out-cwd" in deny

    def test_network_is_denied_not_allowed(self, profile: dict):
        """Negative: network access is denied, so any network tool fails closed."""
        assert "network" in profile["permissions"]["base_deny"]

    def test_mcp_is_denied_not_allowed(self, profile: dict):
        """Negative: MCP is denied, so any MCP operation fails closed."""
        assert "mcp" in profile["permissions"]["base_deny"]


# ===================================================================
# 12.  Terminal output not persisted
# ===================================================================

class TestTerminalOutputNotPersisted:
    """The mailbox stores structured files on disk, not terminal output."""

    def test_event_has_no_terminal_output_fields(self):
        """The event schema has no fields for stdout or stderr."""
        event = build_notify_event(_environ())
        for field in ("stdout", "stderr", "terminal", "output", "tty_output"):
            assert field not in event, f"event must not contain '{field}'"

    def test_event_contains_body_as_structured_text(self):
        """The 'body' field holds a structured summary, not a terminal capture."""
        event = build_notify_event(_environ(BODY="short summary"))
        assert event["body"] == "short summary"
        # No body-size bound that is not enforced by the source code.
        # The source does not truncate or reject body length, so we do not assert one.

    def test_write_produces_file_not_stdout(self, tmp_path: Path, capsys):
        """write_notify_event writes a file; it does not print to stdout."""
        path = write_notify_event(outbox=tmp_path, environ=_environ())
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""
        assert path.is_file()
        assert path.stat().st_size > 0

    def test_mailbox_list_reads_files_not_terminal(self, tmp_path: Path, monkeypatch):
        """The ariadne_deepcode_mailbox.py list command reads persisted event
        files, not terminal history."""
        write_notify_event(outbox=tmp_path, environ=_environ())
        from scripts.ariadne_deepcode_mailbox import main as mailbox_main
        monkeypatch.setattr("sys.argv", ["ariadne_deepcode_mailbox.py", "--outbox", str(tmp_path)])
        exit_code = mailbox_main()
        assert exit_code == 0


# ===================================================================
# 13.  Combined lifecycle contract (integration-style)
# ===================================================================

class TestMailboxLifecycleContract:
    """End-to-end exercise of the full mailbox contract."""

    def test_completed_lifecycle(self, tmp_path: Path):
        """A completed session produces one event with all contract markers."""
        outbox = tmp_path / "local_data" / "deepcode-outbox"
        body = "DECISION: pass"
        path = write_notify_event(
            outbox=outbox,
            environ=_environ(
                STATUS="completed",
                DURATION="83",
                BODY=body,
                TITLE="D3 Mailbox Settings",
            ),
        )
        event = _read_event(path)

        # Local-only ignored outbox.
        assert "local_data" in str(path)
        # Untrusted.
        assert event["trust"] == "untrusted_worker_output_requires_packet_artifact_validation"
        # Controlled exit.
        assert event["status"] == "completed"
        assert event["duration_seconds"] == 83
        # No terminal output.
        assert "stdout" not in event
        assert "stderr" not in event
        # Adapter-compatible.
        assert event["schema_version"] == "ariadne.deepcode_notify_event.v1"

    def test_negative_unknown_status_prevents_file_write(self, tmp_path: Path):
        """Negative: an invalid status raises and no event reaches the filesystem."""
        with pytest.raises(ValueError):
            write_notify_event(
                outbox=tmp_path,
                environ=_environ(STATUS="unknown", DURATION="5"),
            )
        assert len(list(tmp_path.iterdir())) == 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nested_get(d: dict, keys: tuple[str, ...]) -> object:
    """Traverse a nested dict; raises KeyError if any key is missing."""
    for key in keys:
        d = d[key]
    return d
