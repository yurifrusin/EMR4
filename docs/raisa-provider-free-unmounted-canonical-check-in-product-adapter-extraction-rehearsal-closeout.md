# Provider-free unmounted canonical check-in product-adapter extraction rehearsal closeout

Date: 2026-08-18

Timestamp: 2026-08-18T10:22:21+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `8de886c5148b3259428c8c517674f10ea92d937e`

Result:
`raisa_provider_free_unmounted_canonical_check_in_product_adapter_extraction_rehearsal_pass`

## Outcome

The reusable deterministic ordinary-arrival seam now exists as the unmounted
`compose_product_check_in` adapter. It accepts only the dedicated typed
check-in confirmation family and retains the exact domain distinction selected
by the predecessor review: check-in is the authoritative command and
`Arrived` is its resulting database state, not an interchangeable bare status
assignment.

The adapter enforces active same-practice Receptionist authority at ingress
and again inside the injected command session. It classifies idempotency and
one-use evidence before effect, locks exact appointment truth, admits only
`Booked|Confirmed -> Arrived`, verifies the frozen current-state, command,
target-area and freshness contract, and permits only compatible waiting-area
assignment or preservation. Move and removal remain separate and closed.

An accepted effect composes exactly one attributable audit record, one
patient-free `diary.appointment_checked_in.v1` event, one bounded private
receipt, idempotency completion, commit and fresh readback. Pre-commit failures
roll back; commit/readback uncertainty cannot release a false success. Exact
canonical replay returns the stored result without a second lock or effect.

The existing default-off A5.1 route is unchanged and does not import or call
the adapter. No practice was enabled; no route, database, source, watcher,
provider or first-party client was opened.

## Verification

- 85/85 focused adapter cases pass, including 68 named hostile mutations;
- 101/101 adapter, plan and convergence checks pass;
- 152/152 provider-free API checks and the complete 590-check provider-free
  admission packet pass;
- the canonical fast profile passes 200 tests, Ruff, compilation of 218
  maintained Python sources, Diary JavaScript syntax and Git whitespace;
- all twelve frozen route/config/schema/model/service/report/OpenAPI inputs
  retain their canonical-LF SHA-256 bindings; and
- the final corrected eight-command Gemini 3.7 Flash/high exact-candidate veto
  returns `pass` with unchanged clean HEAD.

The first Gemini process returned no admitted decision; AER-0424 adds the
missing digest-only post-transport egress-failure receipt. The next admitted
decision found no product defect and returned `revision_required` solely
because Sol had placed a conftest-dependent A5.1 runtime suite inside the
provider-free command. AER-0425 removes that member, binds the canonical parsed
manifest digest and reproduces 101/101 before the terminal pass. AER-0417
through AER-0425 preserve every bounded planning, worker, verification and
review correction in this tranche.

## Parallelism outcome

The two-file package was mechanically separable, so the DeepSeek lane was a
reasonable allocation. Its occupied run nevertheless ended after about 23
minutes as a transport non-result with no artifact or source change. Sol then
implemented the exact frozen package. Gemini provided the required independent
veto after deterministic admission. Native subagents were declined by current
developer policy; runtime inspection during closeout reported zero live child
agents despite six stale-looking Codex-panel cards.

## Efficiency and long-task finding

The plan froze at 08:58 Brisbane time and the final independent pass returned
at approximately 10:21: roughly 83 minutes. The product result is substantial,
but too much of that interval was closeout-path overhead:

- about 23 minutes were spent waiting for a DeepSeek transport non-result;
- three Antigravity process attempts were needed for one decision gate: a
  missing structured egress, then Sol's invalid fixture-dependent manifest,
  then the final pass; and
- register/receipt correction packets consumed further serial time without
  changing product semantics.

This does not show that the safety gates are unnecessary. It does show that
our remaining inefficiency is concentrated in orchestration reliability and
long-task state, not the adapter's intrinsic complexity. Controls added now
persist post-transport egress failures and require fixture classification plus
canonical manifest hashing. The next named tranche should run in a fresh Codex
task after app restart; the current task has crossed many tranches and repeated
compactions, contrary to Ariadne's fresh-context default.

## Successor

After fresh-task rehydration, the narrowest product successor is:

`raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal`

It may replace the duplicated default-off A5.1 route-local composition with a
call to the accepted adapter while keeping the same route, feature flag,
authored-synthetic practice allowlist, request/response contract and default
denial. It may not enable a practice, change general-status `Arrived`, register
an action-grammar command, wire either first-party client, add waiting-area
movement, use product/patient data or open a real database/provider/runtime.

## Claim boundary

Passing proves an authored-synthetic, in-process, unmounted adapter over
injected fakes. It does not prove HTTP convergence, PostgreSQL/RLS/concurrency,
restart or unknown-commit recovery, product-practice admission, a client
cutover, external adapter conformance, deployment or production. Local/origin
`master` and `handoff/current` remain protected at
`2e34bdad732fdab32fbf778280b3d3c70d66d602`; `docs/branding/` and all unrelated
untracked files remain preserved.
