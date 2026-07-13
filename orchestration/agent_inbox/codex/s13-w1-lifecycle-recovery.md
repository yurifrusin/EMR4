# S13 W1 Lifecycle Recovery

The first detached PTY launch returned a supervisor PID but exited before it
created a receipt, mailbox event, completion artifact, or artifact owner lock.
The non-destructive liveness observer recorded `process_missing` from the
absent supervisor process; elapsed time was not used.

Root cause: the disposable/staging worktree did not contain the ignored,
lockfile-pinned `orchestration/deepcode_pty/node_modules/node-pty` dependency.
The shared integration worktree did contain it, but the runner resolves the
module relative to its own script/worktree.

Recovery is limited to `npm ci` in the staging adapter directory. It changes no
tracked file and does not change the packet, worker ownership, model,
authority, scope, or artifact path. Before the same-lane retry, Terra verifies
that the first process is absent and the completion artifact lock is absent.

Metrics at recovery: one worker launch attempt, one lifecycle defect, zero
worker retries completed, zero marker corrections, zero invalid integrations,
zero manifest variances, zero duplicated-context events, and zero Conductor or
verifier consultations.
