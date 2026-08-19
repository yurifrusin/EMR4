# Provider-free check-in server-attachment lifetime and post-readiness observability conformance repair closeout

Date: 2026-08-20

Status: `accepted`

Reviewed candidate: `9f9984e0575beb7b300035fdb74433f5bef32028`

Implementation source: `cfc7eb472aaaa4fdf7ffef35b07a65a2729073c5`

## Accepted result

The rehearsal retains the server attachment until final teardown, observes the
server while that attachment remains owned, separates stopped-server failure
from identity mismatch, and emits only safe sorted predicate names. Final
cleanup remains the sole teardown owner and existing primary-error preservation
remains exact.

Provider-free verification passed 72/72 tests locally. A fresh isolated Gemini
3.7 Flash/high review repeated all 72 tests and eleven exact commands, returned
`pass`, found no P0-P2 defect, and kept the exact worktree clean. Attempt-004
failure/envelope hashes remain
`1ccc86c76826aa805a48a8823186f5b0eee6e0b571f6deff59ece0474f5df4d3`
and `415f054f10639c2dba2466842ad7b957ce9a66f71f48bf07abe5bfdf4e47e7d5`.

## Native-Harness conclusion

The only DeepSeek worker launch was consumed without a provider call. Its
WorkOrder, one-run latch, zero retry, broker event and cleanup controls worked;
the exact rc.7 effective tool composition did not. Scope-local preset tool
names were passed to a restriction surface that accepts inherited global tool
names, and the safe terminal record retained only generic
`CUSTOM_RUNNER_FAILURE`. This proves neither success nor failure of DeepSeek
reasoning because DeepSeek was never invoked.

## Efficiency and boundaries

Ten procedural repair events are retained rather than hidden. The important
positive result is that none consumed Docker, database, product or DeepSeek
provider work. The important negative result is that sparse dependency closure,
exact command-path selection and effective-tool composition are not yet fully
clockwork-derived.

The ninth event is the first closeout `--check` rejecting a semantic lineage
parent that was not the exact clockwork tail. The correction binds the
machine-read graph/Compass predecessor; the rejection performed no write.

The tenth event was a local PowerShell command chain continuing to commit after
`git diff --cached --check` reported one trailing blank line. The unpushed
commit was corrected, rechecked and amended; future commit gates must branch on
the check exit code rather than rely on sequential command behavior.

No ordinary-practice command, generic-status `Arrived`, action grammar,
first-party client, waiting-area behavior, product/API contract, product data,
production runtime, deployment, release or Pages changed. Local/origin
`master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and all unrelated
untracked files remain preserved.

No attempt 005 is authorised. The next provider-free operation builds the
effective-tool composition and stable terminal-coordinate guard before any
later occupied DeepSeek worker.

The usual non-PHI Pushover closeout notification succeeded with request
`05131aab-9513-46b0-9a49-ceaeb7ee3335`.
