"""Contract tests for Deep Code mailbox settings and PTY lifecycle controls."""

from pathlib import Path

import yaml

from orchestration_harness.deepcode_mailbox import build_notify_event

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "orchestration" / "harness_settings" / "deepcode_mailbox_profile.yaml"
RUNNER_PATH = ROOT / "orchestration" / "deepcode_pty" / "runner.mjs"


def _profile() -> dict:
    return yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))


def _runner() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def test_outbox_is_local_uncommitted_and_untrusted():
    outbox = _profile()["outbox"]

    assert outbox["local_only_relative_path"].startswith("local_data/")
    assert outbox["committed_output_prohibited"] is True
    assert outbox["event_trust"] == "untrusted_worker_output_requires_packet_artifact_validation"


def test_notify_event_uses_the_committed_untrusted_label():
    event = build_notify_event(
        {"STATUS": "completed", "DURATION": "1", "BODY": "untrusted", "TITLE": "worker"}
    )

    assert event["trust"] == _profile()["outbox"]["event_trust"]
    assert event["body"] == "untrusted"


def test_write_scope_requires_disposable_worktree_and_semantic_packet_enforcement():
    permissions = _profile()["permissions"]

    assert permissions["preauthorized_write_scope"] == "entire_deepcode_process_cwd"
    assert permissions["containment_requirement"] == "disposable_packet_scoped_worker_worktree"
    assert permissions["packet_scope_is_semantic_not_cli_enforced"] is True
    assert permissions["base_allow"] == [
        "read-in-cwd",
        "query-git-log",
        "write-in-cwd",
        "mutate-git-log",
    ]
    assert permissions["local_git_mutation_scope"] == "disposable_worker_candidate_commits_only"
    assert permissions["worker_push_and_integration_authority"] == "prohibited"


def test_denied_capabilities_are_exact_and_do_not_overlap_allowed_capabilities():
    permissions = _profile()["permissions"]
    expected = {
        "read-out-cwd",
        "write-out-cwd",
        "delete-in-cwd",
        "delete-out-cwd",
        "network",
        "mcp",
    }

    assert set(permissions["base_deny"]) == expected
    assert set(permissions["base_allow"]).isdisjoint(expected)
    assert permissions["base_default_mode"] == "askAll"
    assert permissions["unknown_operation_requires_interactive_prompt"] is True


def test_automated_pty_event_replaces_notify_hook_and_remains_untrusted():
    lifecycle = _profile()["pty_lifecycle"]

    assert lifecycle == {
        "adapter": "deepcode_pty_adapter",
        "automated_completion_event": True,
        "event_trust": "untrusted_transport_completion_requires_artifact_validation",
        "deepcode_notify_hook_required_for_automated_sessions": False,
        "controlled_exit_required": True,
    }


def test_runner_emits_event_only_after_artifact_turn_exit_and_cleanup_guards():
    source = _runner()
    guard = (
        "artifactObserved && exitSent && turnCompletionObserved "
        "&& processCleanupConfirmed && !permissionPrompt"
    )

    assert guard in source
    assert 'schema_version: "ariadne.deepcode_pty_event.v1"' in source
    assert 'source: "deepcode_pty_adapter"' in source
    assert "const forcedCleanup = exitDeadlineReached" in source


def test_runner_detects_permission_screen_and_fails_closed():
    source = _runner()

    assert "/permission required/i.test(terminalWindow)" in source
    assert "/do you want to proceed\\?/i.test(terminalWindow)" in source
    assert 'reason = "unexpected_permission_prompt"' in source
    assert 'child.write("\\x03")' in source


def test_runner_receipt_never_claims_terminal_output_was_persisted():
    source = _runner()

    assert "terminal_output_persisted: false" in source
    assert "process_cleanup_confirmed: processCleanupConfirmed" in source
    assert "forced_cleanup: forcedCleanup" in source
