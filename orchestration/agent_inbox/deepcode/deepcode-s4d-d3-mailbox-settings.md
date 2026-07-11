# S4d D3 Deep Code Mailbox Settings Test Packet

## Authority

You are DeepSeek worker lane D3. Own only:

- `tests/test_ariadne_deepcode_mailbox_settings.py`
- your completion artifact at
  `orchestration/agent_inbox/codex/review-deepcode-s4d-d3-mailbox-settings.md`

Do not edit any other file, run commands, dispatch agents, change settings,
commit, push, or claim integration authority.

## Task

Add focused settings tests that pin the mailbox and PTY lifecycle contract:
local-only ignored outbox, untrusted events, cwd-wide write scope, disposable
worktree containment, semantic packet scope, required denied capabilities,
automated adapter event, controlled exit/forced cleanup recording, and no
terminal-output persistence. Include at least one negative assertion.

## Completion

Write the owned test file and then the completion artifact. The artifact must
begin `DECISION: pass` or `DECISION: revision_required`, list files changed,
and state that no commands, commits, pushes, or out-of-scope writes occurred.
The PTY adapter event and receipt are separate untrusted transport evidence.
