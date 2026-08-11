# Ariadne agent error and correction register — revision 222

Date: 2026-08-11

Revision 222 records AER-0257 and brings the register to 257 bounded known
incidents.

## AER-0257 — AES-C3 outer labels did not prove inherited containment

The bounded DeepSeek AES-C3 candidate reproduced the frozen 61-scenario totals,
but Sol's deterministic review showed that several results were constructed
from the scenario family or mutation label instead of being derived from the
exact inherited evaluator and replay binding.

A stale-alias attempt still validated and returned `generation_superseded`
after its replay fixture was removed. Changing its declared inherited base to
an exact success base also validated without changing behavior. A malformed
attempt missing `scenario_id` raised `KeyError` rather than returning a closed
rejection. When a deterministic probe made the inherited C2 evaluator return
`allow`/`simulated`, one call and non-null release digests, the stale-replay and
egress branches still emitted their planned outer stop and zero-call claims.
The cumulative branches similarly did not verify every exact returned terminal
result before constructing their outer label.

This is a conceptual containment and evidence-integrity defect. The worker
self-pass and candidate are preserved but unaccepted. The frozen correction
rule permits no same-lane revision; GPT Sol owns recovery through the explicit
orchestrator recovery lease. Recovery must add exact replay identity bindings,
scenario/base coupling, fail-closed public validation, result-derived evidence
and contradictory-result regressions, then pass a fresh Gemini veto before the
incident can be marked corrected.

No real runtime, provider, credential, data, network, filesystem, database,
tool, command or protected ref was opened by the failed candidate or review.
