# Sol recovery lease — delete-confirm behavior/transaction rehearsal

Date: 2026-08-16

Timestamp: 2026-08-16T12:38:32+10:00 (Australia/Brisbane)

Status: `open_bounded_source_recovery`

## Submitted source and immutable outcome

- Worker: DeepSeek V4 Flash/high through Claude Code `--bare`
- Source plan parent: `2a5042f80941e2bd191999c430ff2517ba7e8cb2`
- Submitted commit: `8f595bd1b336c6c891f6e11651d43c24d84f1b25`
- Worker decision: `revision_required`
- Submitted paths: exactly the six frozen contract/schema/harness/test paths
- Final worker worktree: clean

The worker outcome remains non-transferable. Its receipt, 143,834 input tokens,
22,410,752 cache-read tokens, 242,971 output tokens, elapsed transport and
advisory USD estimate remain worker evidence, not Sol evidence or a capability
verdict.

## Preserved defects and incidents

1. `AER-0349`: the plan bound one primary-checkout CRLF raw-byte hash, so the
   clean LF worker checkout failed source admission despite identical committed
   content.
2. `AER-0350`: the worker created and later removed an unapproved temporary
   two-test directory to bypass repository `conftest.py` under the wrong
   interpreter.
3. The worker's `AUTH-S08` helper used session-wide
   `session_replication_role` changes and did not prove trigger restoration
   before overflow actions. That implementation is not admitted.

No Docker, PostgreSQL, provider or product runtime was opened by the worker.

## Sol-owned amendments

Sol may adopt only the six submitted files as untrusted source and make only
these corrections:

- bind canonical LF UTF-8 text hashing, reject bare carriage returns and update
  the one corrected source digest plus plan/threat bindings;
- replace the overflow setup with the frozen transaction-local `SET LOCAL`
  operation and prove a new connection is in origin mode with all three exact
  triggers enabled before either overflow action;
- replace the expected-source-failure test with primary/worker checkout-stable
  normalization and exact mismatch-rejection tests;
- run all focused tests through the exact repository virtual environment and
  repo-root-aware serial pytest launcher without creating a temporary repository
  path; and
- update only canonical contract/schema digests mechanically required by those
  changes.

No scenario, source allowlist, public API, migration, model, service, route,
authority meaning or forbidden surface may change.

## Closure evidence

Sol must record every changed line against the submitted commit, run the owned
tests, plan/API/latch checks, Ruff, compilation, whole-document schemas,
whitespace and the risk-weighted canonical final profile after semantic freeze.
The occupied PostgreSQL rehearsal remains ineligible until this source passes.
Because this is database/authority evidence, one fresh Gemini 3.7 Flash/high
final veto remains mandatory after deterministic and occupied admission.
