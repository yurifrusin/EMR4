# Reception One Bureau post-admission runtime hardening plan

Status: authorised provider-free development tranche
Recorded: 2026-07-31
Predecessor: `reception-one-bureau-cost-bounded-occupied-retry-002`

## Objective

Harden the one shared Bureau proposal presentation path now that both the
Standard planner and one isolated Sydney Vertex request have produced
proofreader-admitted typed proposals.

This tranche makes no provider call and reads no ADC. It uses only the
schema-admitted authored-synthetic proposal fields already permitted by the
accepted UI contract.

## Frozen behaviour

- Standard remains the visible zero-provider default.
- Isolated model remains explicit, development-only and default-off.
- Both planners terminate at the same deterministic proofreader and
  proposal-only adapter.
- The client displays no proposal unless the response says `proposal_ready`,
  the proofreader disposition is exactly `admit`, and the response planner
  exactly matches the planner requested by the user.
- Standard admission requires exactly zero provider calls.
- Isolated admission requires exactly one provider call and one bounded opaque
  runtime-audit reference.
- A planner mismatch, proofreader mismatch, call-count mismatch or malformed
  audit reference fails closed before any typed proposal is displayed.
- Changing planner mode after an admitted result immediately clears that
  planner-scoped proposal and provenance, retains the authored-synthetic
  request text for convenience, and requires a fresh exact appointment
  selection and submission.
- The client never falls back from Isolated model to Standard.

## Acceptance

1. A provider-free browser fixture shows one admitted Standard proposal through
   the ordinary shared renderer with `0 provider calls`.
2. A separate schema-admitted authored-synthetic fixture shows one admitted
   Isolated model proposal through the same renderer with `1 provider call`
   and an opaque audit reference.
3. Switching planner after either admitted result removes the proposal,
   provenance and audit reference before another request.
4. Planner, proofreader, provider-call or audit-reference inconsistencies fail
   closed with no proposal or partial draft.
5. Appointment selection remains explicit user input and is deliberately
   re-required after a planner change, while confirmation, command and write
   authority remain absent.
6. The existing live-local Standard result, accepted occupied result,
   projection-overflow behaviour, API Spine contracts and availability
   reconciliation remain green.
7. Browser traffic is loopback-only, provider calls and credential reads are
   zero, and no database or runtime residue is introduced.

## Evidence labels

The new browser fixture is `route_intercepted_browser` because its typed
responses are local fixtures. It can prove client state and rendering, not a
new live backend or provider result. The earlier non-intercepted Standard and
occupied Sydney evidence remain separately labelled and immutable.

## Closed gates

No Vertex call, ADC read, API key, provider fallback, raw prompt/response,
chain-of-thought, product-derived or patient data, historical Diary material,
appointment confirmation, write, participant session, voice, Word,
production, deployment or release is authorised.
