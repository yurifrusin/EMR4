# Raisa local-only historical Diary document-story time-coordinate recovery rehearsal — report

Date: 2026-08-24

Timestamp: 2026-08-24T05:28:25.6834754+10:00 (Australia/Brisbane)

Result: `blocked_by_fixed_900_second_controller_timeout`

Reviewed source: `2e6974218f8a133e220d84684af432867d53fcd8`

## Conclusion

The coordinate mapper passed its authored-synthetic safety and correctness
floor, but the sole historical content run did not return before the frozen
900-second controller ceiling. It therefore produced no mapping aggregate and
cannot support a claim either for or against the usefulness of the recovered
time axis.

This was a clean fail-closed result. The run terminal prevents retry, no source
value or private coordinate output was emitted, the manifest and projection
are absent, and the exact Word process created by the run was removed after
the parent timeout interrupted automatic cleanup. The pre-existing user Word
process remains responding and untouched.

## What the result teaches

The next defect is operational rather than semantic. The controller needs a
typed timeout result, exact parent-owned child-process cleanup and count-only
throughput evidence. Coordinate extraction also needs an authored-synthetic
performance rehearsal before another archive content run is considered. That
work can proceed without historical data, providers, models or the first-use
scenario gate.

## Verification and authority

All 175 relevant provider-free historical-Diary controls pass, with Ruff,
compileall, PowerShell parsing, source-boundary scans and Git diff checks. Two
contained pre-access interface lapses affected only local test invocation and
a prose assertion; neither read archive content nor changed the empirical run.

No historical-derived fixture, scenario, replay, corpus, memory or product
test exists. The first-use gate remains closed. No provider, model, product,
database, ordinary-practice, deployment, release, Pages, protected evidence or
protected-ref authority opens.
