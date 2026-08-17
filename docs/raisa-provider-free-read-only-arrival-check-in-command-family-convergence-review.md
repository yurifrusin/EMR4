# Provider-free read-only arrival/check-in command-family convergence review

Date: 2026-08-18

Timestamp: 2026-08-18T06:20:30.8340302+10:00 (Australia/Brisbane)

Status: `candidate_ready_for_deterministic_verification`

Task baseline: `fb39d235c5dc4de2440a5b0e4685ee5da5b4f4d0`

Result:
`raisa_provider_free_read_only_arrival_check_in_command_family_convergence_review_pass`

Evidence label: `repository_static_authored_synthetic`

## Decision

The dedicated check-in family is selected as the future canonical
product-facing command for ordinary appointment arrival. `Arrived` remains the
authoritative appointment state produced by that command; it is not by itself
the complete meaning of check-in.

The general status family remains canonical for other appointment lifecycle
changes. During a later atomic first-party cutover, its product-facing
`Arrived` target must cease to represent ordinary check-in at the same time as
both first-party consumers move to the dedicated command. It must not remain a
second interchangeable canonical path. The raw compatibility status route is
not promoted by this decision and remains separately deprecated evidence.

This selection does not enable A5.1. The existing Rayleen-named feature flag
and authored-synthetic practice allowlist remain default-off admission
scaffolding around a deterministic domain contract that must first be
separated into a reusable product adapter.

## Contract matrix

| Dimension | General status proposal/confirm | Waiting-area-only proposal | Dedicated A5.1 check-in |
|---|---|---|---|
| Intent | Any admitted appointment status change, including current `Arrived` target | Change, remove or preserve an area without changing status | Exact `Booked|Confirmed -> Arrived` check-in |
| Product route | Canonical `/proposals/status/{appointment_id:uuid}` plus `/proposals/status/confirm`; hidden historical confirm alias | `/proposals/waiting-area/{appointment_id}` proposes, but current status product adapter rejects this proposal variant | `/proposals/check-in/{appointment_id:uuid}` plus `/proposals/check-in/confirm` |
| Admission | `Receptionist|GP|Nurse`; generally mounted | `Receptionist|GP|Nurse` proposal only; no admitted dedicated confirm family | Exact `Receptionist`, feature flag on and exact authored-synthetic practice allowlist, checked before resource lookup |
| Confirmation | `confirmed=true`, signed status evidence, opaque database generation binding and idempotency key | Proposal requires confirmation but has no dedicated signed confirm action | `confirmed=true`, opaque HMAC evidence with nonce/expiry/purpose and durable one-use evidence-hash claim plus dedicated idempotency namespace |
| Current truth | Product adapter opens a distinct command session, checks current actor twice, locks the appointment and validates database-owned generation | Proposal reads current appointment/area only; no admitted atomic write | Exact appointment row lock, current source-state/freshness and practice/actor/evidence revalidation |
| Status policy | Blocks no-op and terminal re-transition; other transitions are broadly represented | Does not change status | Only `Booked|Confirmed -> Arrived`; all other sources fail closed |
| Waiting area | Status command may assign/clear a supplied area and terminal status auto-clears; the current status seam does not establish A5.1 same-location check-in semantics | Can propose assignment, move or removal | Optional assignment only when none exists; omission/null preserves; no move/removal; assigned or preserved area must be active, same-practice and same non-null appointment location |
| Atomic effect | Status, optional reason/area, one attributable audit and private v1 receipt | No admitted confirm effect | Status, optional compatible area, command-bound audit, one patient-free `diary.appointment_checked_in.v1` event and receipt in one transaction |
| Replay | Same key/fingerprint returns byte-identical private receipt; changed key does not carry A5.1 evidence-consumption semantics | No admitted confirm replay contract | Same key exact replay; different-key reuse of the same signed evidence is rejected, including after state restoration |
| Readback | Canonical stored response plus client reload of Diary truth | Proposal only | Fresh bounded receipt/readback; no check-in consumer or external publisher |
| First-party use | Ordinary Diary and Reception One both currently use this family for `Arrived` | Ordinary waiting-room UI can include an area with its status request; Reception One has no area control | Neither first-party client calls A5.1 |
| Static action posture | `status_change` is implemented and bound to `DiaryConfirmAction.status` | `waiting_area_move` remains planned-not-implemented | `check_in` remains planned-not-implemented and the route contract incorrectly says no signed endpoint exists |

## Why dedicated check-in is canonical

The two write paths can reach the same state but do not prove the same facts.
A5.1 records a narrower source transition, a Receptionist check-in authority,
one-use evidence, stricter waiting-area compatibility and a dedicated committed
event. Generic status records a general state change and intentionally admits a
broader role and transition set. Treating them as synonyms would make the
meaning of `Arrived` depend on which client happened to submit it and would
make check-in event/audit completeness route-dependent.

The promotion checklist already anticipates this conclusion: check-in requires
either a dedicated signed action or a reviewed status binding that records
check-in semantics. The generic family does not currently preserve the full
A5.1 contract, while the dedicated route already represents it. Rebuilding
A5.1 semantics inside generic status would add complexity without producing a
clearer domain boundary.

Waiting-area-only movement remains a separate command family. Check-in may
assign or preserve a compatible area as one atomic arrival effect, but moving
or removing an already assigned area is not check-in and stays outside the
canonical command.

## Reusable kernel and A5.1-only layer

Reusable deterministic check-in contract:

- exact check-in operation and `Booked|Confirmed -> Arrived` policy;
- authenticated practice and current human role from the server session;
- row lock, current authority and source-generation revalidation;
- opaque expiring one-use evidence and dedicated idempotency/replay rules;
- active same-practice/same-location waiting-area assignment or preservation;
- atomic status/area, attributable audit, patient-free committed event and
  private receipt; and
- bounded fresh readback, with the event remaining an acceleration hint.

A5.1-only admission/provenance:

- `rayleen_a5_check_in_enabled` and
  `rayleen_a5_check_in_synthetic_practice_ids`;
- Rayleen/A5.1 naming and authored-synthetic provenance;
- the current development-only claim boundary; and
- the absence of general-practice, external-adapter or production admission.

Receptionist-only authority is retained in the initial reusable contract. It
is a present domain safety policy, not model authority; any expansion is a
separate later policy decision.

## Static contract classification

- `action_grammar.py` saying `check_in` is `implemented=False` is
  **scope-qualified current**: no generally admitted grammar/UI action exists.
- Its prose saying no signed endpoint exists is **factually superseded** by the
  mounted default-off A5.1 confirm route.
- `action_route_contract.py` classifying check-in as
  `planned_not_implemented` is **scope-qualified current** for general product
  authority, but its generic status proposal binding and “no confirm action”
  note are **superseded/incomplete** as route inventory.
- `planned_action_promotion.py` is **current**. Its dedicated-action alternative
  is selected; its gates remain useful for later product promotion.
- `confirm_actions.py` is **current but incomplete for product check-in**: it
  contains no `DiaryConfirmAction.check_in` because that action is not yet
  generally admitted.

These files remain unchanged until the adapter and eventual atomic route/client
cutover supply the authority their declarations would imply.

## Typed route spelling finding

FastAPI mounts the status and A5.1 proposal paths with
`{appointment_id:uuid}`, while `action_route_contract.py` records the generic
status proposal as `{appointment_id}`. Its endpoint-coverage test compares raw
path strings, so the status proposal appears missing and its simplistic
parameter detector does not recognise the typed segment. It then falsely
reports the literal `/proposals/status/confirm` route as shadowed.

This is static normalization/test drift, not an actual route-order or command
authority defect. A later route-contract repair should compare normalized
parameter names/types or use the mounted FastAPI route representation. It must
not change route authority merely to make the test pass.

## Narrowest successor

Open exactly one provider-free unmounted implementation tranche:

`raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal`

It may add an unmounted reusable check-in product adapter and exact authored-
synthetic tests by extracting the deterministic contract from the current A5.1
route-local implementation. It must preserve the existing route byte-for-byte
in behavior and keep it behind its current default-off gate. It may not yet:

- enable any practice or call the route;
- edit the general status admission of `Arrived`;
- register `DiaryConfirmAction.check_in` or mark the grammar implemented;
- wire ordinary Diary or Reception One;
- add a waiting-area move command; or
- open product data, a provider, deployment or production.

Later, one atomic convergence tranche can route A5.1 through the accepted
adapter, promote the static check-in action, switch both first-party clients
and close ordinary product-facing `Arrived` admission in generic status
without leaving either a gap or two canonical paths.

## API Spine finding

- Boundary classification: scheduling command semantics and first-party
  adapter convergence.
- REST/OpenAPI remains command authority; GraphQL remains read-only.
- Proposal, model provenance and client presentation confer no write authority.
- The backend must recheck current human authority and database truth inside
  the mutation transaction.
- The committed event records the result but is not current truth or a receipt.
- Open Yuri decision: none. The extraction rehearsal is bounded, provider-free
  and does not admit product use.

## Parallelism efficacy

Sol retained the coupled comparison and selection. DeepSeek remained declined
for this review because no separable implementation package existed. The
successor extraction creates such a package and must reassess DeepSeek at its
plan freeze. Gemini 3.7 Flash/high is required for one fresh exact-candidate
read-only veto because this result freezes material command-family meaning.
Native subagents remain declined under current developer policy.

## Claim boundary

This review proves repository facts and selects a semantic/product direction.
It does not prove live route or database behavior, general A5.1 admission,
product usability, external-adapter conformance or production readiness.

No product/backend/API/OpenAPI/GraphQL/schema/service/migration/database source,
action grammar, route contract, raw compatibility behavior, feature flag, live
route/source/watcher, provider, product/patient/clinical/historical data,
deployment, release, Pages or protected ref changed. `docs/branding/` and every
unrelated untracked file remain preserved.
