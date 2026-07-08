# Bernie UI Derived-State DAG D3 Inventory

Date: 2026-07-08

Status: inventory/review only. No UI wiring, route wiring, provider wiring,
database access, memory/RAG/GraphRAG access, H15/H-series runtime import,
historical diary material access, GraphQL resolver, or appointment write is
approved here.

Proposal-surface guard citation:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Expected blocked values: `runtime_or_provider_wiring_ready=false`,
`raw_trove_access_ready=false`, `runtime_gate_decision=blocked`,
`default_provider=disabled`, `live_provider_enabled=false`,
`provider_calls_performed=false`, `route_behavior_changed=false`,
`database_access_performed=false`, `memory_or_rag_access_performed=false`, and
`historical_diary_material_access_performed=false`.

## Position

Sprint 236 added the provider-free `BernieUiViewModel` selector contract. This
D3 inventory maps the current Diary/Bernie taskpane switch points to that
contract so a later D4 consumer slice can replace scattered local switches
deliberately.

The frontend source of interest is `docs/diary/diary.js`. This file remains
unchanged in D3.

## Current Switch Points

| Current UI switch point | Current role | Future view-model field |
|---|---|---|
| `BERNIE_STATUS_COPY` | maps ad hoc review states to status badge copy | `copy_mode`, `primary_copy` |
| `BERNIE_HEADLINE_COPY` | maps ad hoc review states to headline copy | `copy_mode`, `primary_copy` |
| `scrubBernieStaffCopy` | removes raw IDs, snake_case codes, and generic not-found copy | negative-copy invariant remains; future renderer still applies safe copy |
| `bernieStatusCopy` | fallback status copy with provider-unavailable special case | `copy_mode`, `flags.show_technical_details` |
| `bernieHeadlineCopy` | fallback headline copy with provider-unavailable special case | `copy_mode`, `primary_copy` |
| `isBernieConfirmReady` | checks selected-slot evidence, confirm payload, policy, and affordance flags | `confirmation_state`, `freshness_state`, `flags.show_confirm_button`, `flags.enable_confirm_button` |
| `hasBernieSelectedSlotEvidence` | derives whether candidate/proposal evidence exists | `candidate_state`, `proposal_state` |
| `bernieReviewTransition` | central but still payload-shaped state classifier for candidates, no-slots, blocked, clarification, and confirmation-ready | `session_phase`, `clarification_state`, `candidate_state`, `proposal_state`, `confirmation_state`, `freshness_state`, `identity_state` |
| `bernieStatusCopyForPayload` | converts transition state plus schedule explanation into badge text | `copy_mode`, `primary_copy` |
| `bernieHeadlineCopyForPayload` | converts transition state plus schedule explanation into headline text | `copy_mode`, `primary_copy` |
| `bernieReviewActionCopy` | action/help copy, including repeated pre-confirm "nothing booked" safety copy | `copy_mode`, `primary_copy`, `secondary_copy` |
| `createBernieServerSessionBanner` | renders stale-session refresh banner from `bernieSession.serverConflict` | `freshness_state`, `flags.show_stale_warning` |
| `bernieComposerPlaceholder` | changes input placeholder from ask/reply/ask-another based on turns and legacy session state | `clarification_state`, `session_phase`, `copy_mode` |
| `renderBernieToolIntentReview` | separate tool-intent proposal surface with confirmable/non-confirmable branch | future separate tool-intent view model; do not fold into booking selector in D4 |
| `confirmBernieToolIntentChange` | writes through existing signed REST command path | out of scope for display selector; must remain command-owned |
| `renderBernieReview` | primary booking review renderer that consumes transition/copy/confirm helpers and candidate/proposal payloads | first D4 candidate for read-only consumption of backend-computed view-model fields |
| `handleBernieConfirmShortcut` | keyboard shortcut for the confirm button | `flags.show_confirm_button`, `flags.enable_confirm_button` |
| `bernie-review-confirm-button` branch inside `renderBernieReview` | existing signed REST confirmation command caller for the booking review panel | out of scope for view-model fields; command payload must not consume display state |

## Suggested D4 First Consumer Slice

The safest first D4 slice is the primary booking review panel only:

- candidate slot list visibility;
- pending proposal card visibility;
- confirm button visibility/enabled state;
- stale warning visibility;
- success copy visibility;
- retry/edit affordances for stale or failed states.

This should consume backend-computed view-model fields when they are delivered
by a later reviewed route/read-model change. Until that delivery surface exists,
D4 should use route-intercepted fixtures only and must not reimplement the
Python selector in frontend JavaScript.

## Required D4 Evidence

Before any UI wiring lands:

- route-intercepted Playwright or JS smoke evidence must prove the ordinary
  Margaret Thompson / Dr Shera flow still shows candidate times, staged
  proposal review, confirm readiness, and backend-confirmed success only after
  the existing signed REST command reports success;
- pre-confirm copy must not show raw UUIDs, snake_case codes,
  `missing_practitioner_id`, generic `Not Found`, or success language;
- `pressed` and `awaiting_backend` must hide/disable confirm and avoid success
  copy;
- stale/failed states must show refresh, retry, or edit affordances;
- command payloads must still use existing signed proposal/freshness/evidence
  fields and must not include `BernieUiViewModel` fields;
- evidence labels must say route-intercepted unless the browser reaches a real
  non-intercepted backend and provider metadata proves otherwise.

## Closed Gates

Still closed:

- UI wiring into `docs/diary/diary.js`;
- route or response wiring for `BernieUiViewModel`;
- provider prompt or provider dry-run wiring;
- live provider evidence;
- memory/RAG/GraphRAG runtime wiring;
- H15/H-series runtime imports;
- historical diary material access;
- GraphQL resolvers or mutations;
- appointment writes outside existing signed REST command handlers;
- model-to-database writes.

## Strategic Position

This is a guardrail/inventory sprint in the Bernie UI derived-state DAG lane.
It sits between D1/D2 selector definition and any D4 UI consumer work, reducing
the risk that the first UI wiring sprint picks an accidental broad refactor.
