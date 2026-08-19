# Check-in server-attachment observability repair report

Date: 2026-08-20

Status: `accepted`

## Result

The relay-free rehearsal now keeps its captured PostgreSQL server attachment
under one owner until the final `finally` teardown. Post-readiness observation
is split into two fail-closed coordinates: a non-exact running state produces
`environment/server_not_running_after_readiness` with no detail, while an exact
running state followed by identity failure produces
`environment/server_identity_mismatch_after_readiness` with only sorted safe
predicate names or `inspect_shape`.

The exact implementation source is
`cfc7eb472aaaa4fdf7ffef35b07a65a2729073c5`. The repaired harness SHA-256 is
`62a18d9ce2a29eb417f491c8ce341416f03183375f042f8c41bcb1f4674df77c`.
Focused provider-free tests pass 19/19 and descendant-compatible relay-free
regressions pass 53/53. One fresh Gemini 3.7 Flash/high veto executed the same
72 tests and eleven commands at exact candidate
`9f9984e0575beb7b300035fdb74433f5bef32028`, returned `pass`, found zero P0-P2
issues and left the worktree clean.

No Docker object, PostgreSQL process, database, SQL transaction, product
runtime or patient/appointment/clinical/protected data was used.

## DeepSeek native-Harness result

The single admitted rc.7 worker launch failed closed before DeepSeek was
called. The broker became ready, but provider calls, requests, model steps,
tool calls, tests and file changes all remained zero; cleanup was exact and
automatic retries remained zero.

The controller mounted filesystem tools inside the bounded agent preset and
then passed `read`, `glob` and `edit` to `tools.restrict()`. In rc.7 that method
filters inherited global tools and rejects scope-local names. The resulting
composition exception was collapsed to generic `CUSTOM_RUNNER_FAILURE`. This
is an orchestrator/Harness composition and terminal-coordinate defect, not a
DeepSeek reasoning failure. The consumed attempt is immutable and will not be
retried or resumed.

## Test-boundary interpretation

Three broad relay-free tests intentionally bind older harness bytes and
correctly rejected the descendant repair. They remain unchanged historical
source-pin checks, not candidate regressions. The plan-freeze test similarly
passed at the frozen planning source and is not satisfiable against the
deliberately changed harness path. Those checks were not weakened. The clean
candidate boundary is the focused harness suite plus the seven
descendant-compatible relay-free suites.

## Honest efficacy reading

The clockwork WorkOrder, one-run latch, no-database admission and broker event
chain worked: the faulty profile composition consumed no DeepSeek tokens,
database time or product authority. The missing gear was an effective-tool
composition check before provider dispatch, and the generic terminal code made
diagnosis less direct than it should have been.

Ten orchestration repair events are retained in `efficacy-reading.json`,
including sparse dependency closure, an exact filename lapse, an unrecoverable
test terminal, one lint correction and source-pin misclassification. They did
not alter the accepted candidate, but they show that command/evidence
dependency closure still needs to become machine-derived rather than carried
in orchestrator memory.

The ninth event was a useful clockwork guard trip: the first read-only closeout
check rejected a semantically chosen predecessor because it was not the exact
current graph/Compass tail. The corrected intent uses the machine-read
predecessor; no canonical write occurred on the rejected check.

The tenth event occurred after clockwork publication: a sequential PowerShell
commit command did not stop when `git diff --cached --check` reported one
trailing blank line. The commit was still local, the file was corrected, the
gate was rerun and the commit was amended before push. Future commit gates must
branch explicitly on the check exit code.

## Next gate

No attempt 005 is admitted. The next operation is
`deepseek-native-harness-provider-free-effective-tool-composition-and-terminal-coordinate-guard`.
It must assemble the exact rc.7 preset provider-free, prove that the effective
tool view is exactly `read`, `glob`, `edit`, avoid the global/scope-local
restriction mismatch, and emit stable sanitized pre-provider coordinates. It
must make zero provider calls and requires no occupied DeepSeek launch.
