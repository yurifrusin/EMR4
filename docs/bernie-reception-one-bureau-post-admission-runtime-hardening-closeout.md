# Reception One Bureau post-admission runtime hardening closeout

Status: accepted provider-free development result
Recorded: 2026-07-31
Result: `reception_one_bureau_post_admission_runtime_hardening_pass`

## Result

The Bureau now treats its planner provenance as part of the proposal admission
contract, not as decorative metadata. A proposal is displayed only when:

- the returned planner exactly matches the planner selected for that request;
- the proofreader disposition is exactly `admit`;
- Standard reports exactly zero provider calls and no runtime-audit reference;
  or
- Isolated model reports exactly one provider call and one bounded opaque
  runtime-audit reference.

A mismatch in planner, proofreader disposition, call count or audit-reference
shape fails closed before patient/practitioner binding or proposal rendering.

Changing planner after an admitted result immediately discards the
planner-scoped proposal, provenance and audit reference. The authored-synthetic
request text remains in the composer for convenience, but the UI requires the
operator to select the exact appointment and submit again. No stale result is
relabelled under the new planner.

## Evidence

The route-intercepted Chromium acceptance exercised six local typed fixtures:

- one valid Standard admission;
- one valid Isolated model admission;
- one planner mismatch;
- one proofreader mismatch;
- one provider-call-count mismatch; and
- one malformed audit-reference mismatch.

Both valid fixtures used the same renderer. Both planner switches cleared the
proposal, provenance and audit reference. All four malformed tuples rendered
no proposal or partial draft.

Evidence:

- `orchestration/continuity/reception-one-bureau-post-admission-runtime-hardening/browser-acceptance-evidence.json`;
- `orchestration/continuity/reception-one-bureau-post-admission-runtime-hardening/standard-admitted.png`;
- `orchestration/continuity/reception-one-bureau-post-admission-runtime-hardening/isolated-admitted.png`; and
- `orchestration/continuity/reception-one-bureau-post-admission-runtime-hardening/planner-change-cleared.png`.

The screenshots were visually inspected. The admitted Isolated fixture shows
the exact bounded provenance line; the cleared state shows no proposal or
provenance and gives a direct fresh-selection instruction.

## Verification

- 113 focused Bureau, dual-planner, overflow, availability-reconciliation,
  functional meta-grid, live-local, API Spine and Compass tests pass.
- The repository-only Ariadne verifier passes 266 tests.
- The browser fixture made zero provider calls, zero credential reads, zero
  database reads/writes and zero appointment confirmation/writes.
- Browser traffic was loopback-only apart from the deliberately blocked
  Office.js bootstrap resource.
- JavaScript syntax, Python compilation, Ruff, JSON parsing, Continuity,
  Compass, rendered Compass and `git diff --check` pass.

## Candid boundary

This proves provider-free client-side admission binding, shared typed
presentation and stale-state clearing over authored-synthetic fixtures. It
does not create or replay a provider result and does not prove a new backend,
database, production or real-data path. The accepted earlier Standard
live-local result and occupied Sydney Vertex result remain the evidence for
those separate paths.

No provider, ADC, product-derived or patient data, historical Diary material,
confirmation, write, participant, voice, Word, production, deployment or
release boundary was opened.

Continuity graph revision 167 and Compass map revision 148 bind this accepted
result and rendered orientation. The next material decision is the exact Word
Online development-access shape; no Word wiring is authorised by this
closeout.
