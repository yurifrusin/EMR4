# Reception One selected-action-console consolidation orientation threat-model delta

Date: 2026-08-14

Timestamp: 2026-08-14T14:18:57+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: accepted selected-appointment status, time, duration and
practitioner compositions at task baseline
`2b65cc8b639b6922c8f176a1d65ddc206fa6ba52`

## Changed surface

This tranche changes no product surface. It selects a future presentation-only
console that exposes four deterministic action choices and at most one
existing field editor. It adds no command, data or provider authority.

## Threats and required controls

| Threat | Required control |
|---|---|
| Visual consolidation becomes a generic command dispatcher | The palette sets only `activeSelectedAction`; every field keeps its existing renderer, executor, bridge and command family. |
| Status and update authority appear to be one transaction | Preserve explicit field-to-bridge mappings and never construct a combined payload or multi-field confirmation. |
| Choosing an action performs work | Open, collapse and switch produce zero proposal, confirmation or mutation routes. |
| A hidden provisional draft later executes | Only one editor exists; idle switching discards and resets the outgoing unsubmitted draft from current truth. |
| Staff switch actions during confirmation | Disable every palette transition while any action is busy or the existing dialog owns focus. Keep the active editor mounted for focus return. |
| Stale or interrupted state reopens as actionable | Preserve the existing refresh-only reconciliation gate and clear drafts before another action can open. |
| Requested values are displayed as current truth | The compact summary comes only from the selected fresh projection; terminal truth comes only from exact fresh reconciliation. |
| A screen reader receives four simultaneous outcome streams | Render one active field and one polite atomic feedback region only. |
| Custom palette keyboard behavior becomes inaccessible | Use native buttons with ordinary tab order, `aria-expanded` and `aria-controls`; add no custom tablist or roving focus. |
| A new modal conflicts with confirmation focus | Keep disclosure inline; the existing confirmation dialog remains the sole focus-contained review layer. |
| Small screens still accumulate middleware | Require one wrapping palette and one full-width editor with no horizontal overflow and 44-pixel targets. |
| Natural language silently gains command authority | Future intent may select an editor only after deterministic admission; it cannot propose, confirm or combine a command. |
| Future actions resume unchecked accretion | Adding another material action group requires a fresh density and authority review rather than automatic palette growth. |

## API Spine preservation

GraphQL remains read-only. Status stays on its existing status
proposal/confirm route family. Time, duration and practitioner stay on the
existing update proposal/confirm route family through their current bridges.
No OpenAPI, Pydantic, database, generated-client or audit change is admitted.

## Residual boundary

The selected design has not yet been implemented or tested with users. Natural
language action activation, multi-field editing, full edit, new appointment
fields, product data, live runtime, deployment and production remain unproved
and closed.
