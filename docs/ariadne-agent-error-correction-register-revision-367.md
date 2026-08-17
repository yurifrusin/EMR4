# Ariadne agent error and correction register — revision 367

Date: 2026-08-18

Timestamp: 2026-08-18T09:05:05+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 367 adds AER-0418. The first pre-dispatch receipt correctly refused
worker launch because the assigned DeepSeek agent id had no explicit workspace
receipt, although the separately observed worktree was clean and at the exact
committed plan source.

The correction adds the required agent id, worktree, branch, clean-state,
current-handoff and timestamp fields to the runtime state and reruns preflight
before launch.

## Population

- incidents: 418;
- corrected or explicitly contained: 418;
- open: 0;
- latest id: `AER-0418`.

No worker, provider, product source, data, deployment or protected ref opened.
