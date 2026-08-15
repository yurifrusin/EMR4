# Delete-confirm kernel DeepSeek rejection and Sol recovery lease

Date: 2026-08-15

Timestamp: 2026-08-15T12:14:08+10:00 (Australia/Brisbane)

Status: `worker_self_pass_rejected_sol_recovery_active`

## Preserved worker result

DeepSeek V4 Flash/high produced clean six-file commit
`b2d6427582737b126f6c3c8d57a59b88440ca5fc` from exact plan source
`717c1233046452abff7d83af68e9949a31cc29b5`. Its 19 focused tests, Ruff and
whitespace checks passed, and no owned-path or protected-boundary breach
occurred. The worker reported `DECISION: pass`.

That attestation is rejected and remains non-transferable. Independent Sol
review reproduced three acceptance defects:

1. the canonical packet marks confirmation valid at `01:55:04Z` although its
   own evidence expires at `01:52:49Z`;
2. the purported closed transaction contract does not enumerate exact current
   actor roles/cancellation capability or the signed-evidence field set; and
3. optional cancellation text is described but no successful null-text command
   or atomic result is represented.

These are conceptual acceptance-contract defects, not mechanical omissions.
The Flash correction loop is therefore closed and no same-lane revision is
permitted.

## Sol recovery lease

Under `docs/ariadne-orchestrator-recovery-lease.md`, Sol may adopt only the
six-file source as an untrusted candidate. The recovery remains inside the
frozen plan and will make these exact amendments:

- replace the contradictory clock values with one valid closed interval and
  make ordering/expiry a validator invariant plus hostile mutation;
- add exact immutable top-level authority, signed-evidence, reason,
  idempotency, transaction, atomic-effect, readback and compatibility-ingress
  contracts;
- bind the current mutating appointment roles and one explicit cancellation
  capability without accepting request-body authority claims;
- separate structured reason state from optional cancellation-text state and
  add one successful null-text decision and transaction schedule;
- require exact appointment/audit/receipt identity, state-version and reason
  fields in the closed contract; and
- add direct regression tests for every amendment before broader verification.

No plan meaning, product policy, mounted source, database, provider, data,
runtime, command, deployment, release or protected ref is opened. A fresh
Gemini exact-candidate veto remains mandatory after deterministic admission.
