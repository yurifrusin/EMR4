# Bernie Stage 1 Tranche B protected-access stop

**Decision:** `blocked_for_user_decision`

Tranche B stopped before candidate selection, receptionist confirmation, or any
appointment write. A broad test search used exclusion globs that did not exclude a
Windows protected-holdout path and returned protected holdout content to the
terminal. Under the frozen Stage 1 stop rules, that is a protected-evidence boundary
breach even though it was inadvertent.

The returned material was not inspected further, summarized, inferred from, used
for product reasoning, used for a code change, or copied into Stage 1 evidence. The
in-app Browser tab was closed and the loopback FastAPI and static Diary processes
were stopped immediately. The exact disposable synthetic database is preserved for
incident continuity.

## Preserved zero-write state

The last verified database baseline was 0 appointments, 0 appointment audits, and
0 appointment-command idempotency rows. The Browser had submitted the frozen
instruction on `D=2026-07-20`, but no candidate was selected, no visible
confirmation action occurred, no `confirm-bernie` request was sent, and no receipt
was created. Provider calls, cloud operations, and external transmissions remained
zero.

Before the incident, the real non-intercepted Diary → FastAPI → isolated PostgreSQL
path authenticated successfully, resolved Margaret Thompson and Dr Alex Shera,
resolved the 14:00-15:45 interval, and found seven candidate slots. The UI still
failed closed before candidate selection because the typed outcome classified the
future pinned reference date as `context_reference_date_stale`. That is a
reproducible unchanged-product Stage 1 defect, but no correction was started because
the later protected-access stop superseded execution.

Two earlier harness setup failures were mechanical and contained entirely within
fixture setup: the first created an empty database before an import-path error, and
the second created schema but rolled back every row after a fixture flush-order
error. Each exact disposable database was removed only after proving respectively
zero public tables and zero rows. The third setup passed the frozen synthetic-only
inventory and all pre-browser checks.

No Tranche B resumption or Tranche C correction is authorized in this context. A
resumed run requires Yuri's direction, a fresh clean execution context, full
mandatory rehydration, a new five-source Ariadne receipt, and exact protected-safe
test-path selection.

The canonical machine-readable record is
`docs/bernie-stage1-tranche-b-protected-access-stop.json`.
