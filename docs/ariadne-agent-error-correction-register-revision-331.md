# Ariadne agent error and correction register — revision 331

Date: 2026-08-17

Timestamp: 2026-08-17T11:33:30.0272329+10:00 (Australia/Brisbane)

Status: contained; independent veto remains unsatisfied

## Revision

Revision 331 records 380 bounded known incidents. No incident is open.

- AER-0380 preserves two fresh-project Antigravity transports against exact
  clean candidate `f6e5e96dc86a1bb3319692a6ac656fbb756b49df`. Each ended with
  exit code 1, empty stderr, no receipt and no terminal model decision.
- The exact worktree remained clean and unchanged after both attempts. The
  failures are transport observations, not a Gemini rejection and not evidence
  for or against the candidate's semantic correctness.
- The configured single same-head, same-model, same-packet retry is consumed.
  No silent fallback or further retry is admitted. The candidate therefore
  remains deterministically admitted but not independently accepted.

## Boundary

No Raisa product, API, database, migration, provider product call, credential,
deployment, release, Pages or protected ref changed. `docs/branding/` and every
unrelated untracked file remain preserved.
