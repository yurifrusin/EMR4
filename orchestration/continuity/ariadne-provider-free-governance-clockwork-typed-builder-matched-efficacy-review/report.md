# Governance clockwork typed-builder matched efficacy review

Date: 2026-08-23

Timestamp: 2026-08-23T18:13:32.8732571+10:00 (Australia/Brisbane)

Result: `retain_with_traceability_repair`

## Conclusion

Retain the typed semantic builder. Its first real closeout removed 89 of 150
like-for-like caller scalar leaves, a 59.3% reduction, while one publication,
one lease advance and zero rollback preserved the canonical safety model.

Do not call the first use flawless. It exposed two measurable evidence defects
and showed that most remaining clerical bulk now sits outside the semantic
intent in continuation runtime states and receipts.

## Corrected leaf comparison

The prior incident-bearing legacy intent has 176 leaves. Its incident
observation has 25. Subtraction produces the frozen 151 figure, but that object
still retains one incident-generated register-revision acceptance path. Removing
both the observation and its generated path produces the normalized
no-incident baseline of 150.

The representative semantic fixture has 64 leaves. The actual closeout intent
has 61 leaves, 5,502 bytes and 96 lines. Against the normalized baseline it
removes 89 caller leaves, not 90. This correction does not threaten the frozen
100-leaf ceiling or the decision to retain the interface.

## Actual execution cost

From the frozen plan commit to the publication commit, the tranche took 47
minutes 44 seconds and four commits. It changed 37 paths. One header operation
materialized three documents while recognizing two exact headers, and a second
operation read all five idempotently. One semantic dry check ran no commands.
One semantic publish ran and passed three commands, produced one generation and
advanced one lease. One idempotent readback reran no commands and moved nothing.
No rollback, product rerun, provider call or protected-ref movement occurred.

The four-file 115-test governance suite ran three times: implementation
acceptance, the closed publication command, and postpublication validation.
That is honest build cost. The review does not yet recommend removing one of
those runs because the exact replacement invariant has not been frozen.

## Traceability defect

The idempotent readback correctly detected the existing publication and skipped
verification and canonical writes. The CLI then wrote its result to the same
`clockwork-tick-evidence.json` and report paths used by the publication. The
current convenience evidence therefore records the idempotent reading and no
longer retains the publication's three output digests.

The transaction, generation, pointer and latch remain valid, so this is not
canonical corruption. It is nevertheless a real postpublication traceability
defect. The missing digests will not be reconstructed by hand. Until repaired,
closeouts should publish once and use canonical validation rather than a second
`--publish` for readback.

## Where the remaining weight moved

The compact semantic intent is 96 lines and 5,502 bytes. The same tranche added
seven runtime states and seven receipts totalling 2,334 lines and 130,653
bytes—24.3 times the intent's lines and 23.8 times its bytes. Those artifacts
serve real five-source, latch, parallelism and Git-binding safety functions,
but most of their shape is repeated repository-known structure.

This is now the largest obvious ergonomic target. After preserving publication
evidence, the existing orchestrator preflight should gain one narrow typed
serial-governance projection that derives the active latch, adapter inventory,
worker slots, context sources and machine Git snapshot. The caller should
supply only the event, planned action, assessment stage, active evidence paths
and any non-default lane decision. This must replace runtime-state repetition,
not create a new receipt layer.

## Ranked recommendation

1. Retain the typed builder and immediately repair idempotent evidence
   preservation inside the existing CLI.
2. Then prototype one typed continuation-state projection inside the existing
   preflight and measure it against 14 files / 2,334 lines.
3. Only after those two gains, map whether postpublication validation can
   replace a third full suite with exact canonical-state checks.
4. Keep worker-Harness coupling at the coarse `prepared`, `terminal`, and
   `accepted_or_recovered` readings; do not revive per-turn clock gears.

## Boundaries

No implementation changed in this review. No Harness, Claude fallback,
provider, model worker, product source, data, database, credential, environment,
runtime, deployment, release, Pages, protected evidence or protected ref was
opened.
