# S12 W1 lifecycle escalation

## Status

`escalated_to_sol_repeated_worker_defect`; S12 acceptance and protected-master
manifest preparation are stopped. This is an explicit trigger in
`tranche_executor_pilot.yaml`.

## Preserved sequence

1. Attempt 1 launched detached with supervisor `28980`; it had no shared
   Python injection and remained alive without producing an artifact or
   receipt. Its final transcript is preserved under the worker worktree's
   ignored `local_data/ariadne-harness/s12-w1-outbox/`.
2. An executor lifecycle error launched attempt 2 concurrently against the
   same artifact. On direction, attempt 1's tree (`28980`, `16972`, `93032`;
   ConPTY child `22344` was already absent) was terminated only after confirming
   the shared artifact did not exist. Attempt 2 was then the sole owner.
3. Attempt 2 wrote an artifact but its foreground supervisor was interrupted
   before a PTY receipt. The artifact is preserved as ignored
   `s12-w1-attempt2-artifact-no-receipt.md` and is not accepted.
4. A same-lane correction packet was issued. The liveness observer reported
   `process_missing` for attempt 3 even though later direct process inspection
   found supervisor `90484`, command shell `52136`, CLI `29724`, and ConPTY
   child `32536` still alive with no artifact or receipt. The observer
   misclassification is additional lifecycle evidence. The transcript remained
   unchanged; the attempt-three tree was then terminated only after its final
   transcript was preserved. No attempt-three artifact or receipt exists.

## Current safety posture

- No S12 W1 process remains and no active process owns the canonical artifact.
- No worker artifact has an accepted completed PTY receipt.
- No production, policy, provider, schema/database, deployment/release,
  external-client, H15/H-series, historical-trove, memory/RAG/GraphRAG, or
  write-authority change was made.
- `codex/s10-terra-staging` contains only the S12 plan and the same-lane
  correction packet; it contains no accepted S12 worker result or acceptance
  closeout.

## Required Sol decision

Resolve the repeated Deep Code lifecycle/receipt defect before a further W1
dispatch. Any recovery must retain one canonical artifact owner and produce a
completed receipt before S12 can run final deterministic acceptance.
