# DeepSeek native Harness structured diagnostic native-boot observability rehearsal

Date: 2026-08-21

## Lay summary

The new diagnostic gear has now passed around the real pinned DeepSeek Harness
entrypoint. We deliberately gave it a harmless missing local profile, so it
failed before starting a worker or contacting DeepSeek. Instead of disappearing
opaquely, it produced the exact safe, structured explanation expected, then
cleaned up completely.

This is a meaningful traceability improvement, but it is not yet evidence that
a DeepSeek worker can complete useful work. The sensible next step is to fit
this proven diagnostic gear into the bounded worker controller without making
a provider call. A later fresh occupied attempt can then be considered on a
cleaner and more controllable foundation.

The clockwork also did useful work: it stopped one malformed preexecution
receipt before launch. Two further local command-shape errors were corrected
without rerunning the Harness. The expensive native attempt therefore ran
exactly once.

## Technical summary

- Accepted source:
  `36f173d3b4b65d9a65a90cecd06d403c3b1492a2`.
- Package: `@deepseek-ai/dsh@0.1.0-rc.7`.
- Native process / retry: `1 / 0`.
- Exit / duration: `1 / 3552 ms`.
- Terminal:
  `ariadne.native_harness_pre_hmr_startup_terminal.v2`,
  `structured_entrypoint_import_rejected`.
- Safe diagnostic: one `error` node; all optional source coordinates
  `none`; no raw message, stack or path retained.
- HMR / broker / session / prompt / tool / model / provider / network:
  all zero.
- Cleanup: process absent, disposable root absent, copied package tree absent,
  raw streams absent.
- Verification: deterministic check, 64 provider-free tests, Ruff, Python
  compilation, schema/relationship checks, protected refs and diff hygiene
  pass.
- Register revision 581 records AER-0744 through AER-0749; none is open. The
  only live-governance correction used a byte-exact rollback and a durable
  monotonic rollback-lease commit before replacement publication.

Next:
`raisa-provider-free-authored-synthetic-native-harness-structured-diagnostic-bounded-worker-controller-convergence-rehearsal`.
It is provider-free and launches no Harness, worker or provider.

No product, patient, appointment, clinical or practice data was used. No
ordinary-practice, deployment, release, Pages or protected-ref authority
changed.
