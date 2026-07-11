# S4d D1 Deep Code Adapter Settings Test Packet

## Authority

You are DeepSeek worker lane D1. Own only:

- `tests/test_ariadne_deepcode_adapter_settings.py`
- your completion artifact at
  `orchestration/agent_inbox/codex/review-deepcode-s4d-d1-adapter-settings.md`

Do not edit any other file, run commands, dispatch agents, change settings,
commit, push, or claim integration authority.

## Task

Add focused settings tests that pin the committed Deep Code adapter contract:
default `deepseek-v4-flash` / high, exceptional Pro/max use, real-TTY requirement,
non-TTY refusal as adapter unavailability rather than model unavailability,
durable artifact authority, and permission approval not granting integration.
Include at least one negative assertion.

## Completion

Write the owned test file and then the completion artifact. The artifact must
begin `DECISION: pass` or `DECISION: revision_required`, list files changed,
and state that no commands, commits, pushes, or out-of-scope writes occurred.
The PTY adapter event and receipt are separate untrusted transport evidence.
