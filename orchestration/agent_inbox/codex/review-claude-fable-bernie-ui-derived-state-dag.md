# Review: Bernie UI Derived State DAG Plan

| Item | Value |
|---|---|
| Reviewer | Claude Fable (`claude-fable-5`) — no model substitution |
| Date | 2026-07-08 |
| Subject | `docs/bernie-ui-derived-state-dag-plan.md` |
| Type | Design review only — no code, gate, provider, route, GraphQL, or write changes |

Inputs read: the plan packet,
`orchestration/event_driven_statechart_architecture.md`,
`orchestration/bernie_interaction_model.md`,
`orchestration/bernie_release_gates.md`, `orchestration/api_spine_adr.md`,
`docs/bernie-prompt-thread-tranche-readiness.md`, plus grounding checks of
`app/services/bernie/session.py`, `app/schemas/appointments.py`, and
`docs/diary/diary.js`.

Proposal-surface guard citation (both commands run 2026-07-08, output matched):

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Verified current blocked values:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`
- `default_provider=disabled`
- `live_provider_enabled=false`
- `provider_calls_performed=false`
- `route_behavior_changed=false`
- `database_access_performed=false`
- `memory_or_rag_access_performed=false`
- `historical_diary_material_access_performed=false`

## Verdict

**Approve the direction; require the changes listed below before Sprint D2
implementation.** The plan is not new architecture — it names a layer that
already exists implicitly and badly. The server already has a genuine
statechart (`BernieSessionState` in `app/services/bernie/session.py`) and a
snapshot read model (`BernieSessionSnapshotOut`,
`app/schemas/appointments.py:1201`), while `docs/diary/diary.js` (~9,700
lines) reconstructs display state through scattered functions
(`bernieStatusCopy`, `bernieHeadlineCopy`, `bernieReviewTransition`,
`bernieStatusCopyForPayload`, and friends). The DAG proposal is the standard
selector/view-model pattern applied to that spread. It is the right amount of
architecture provided it stays a pure projection and never becomes a third
state store.

## Direct Answer to Yuri's Sequencing Question

Yuri has already approved the practitioner-directory REST first slice
(`docs/api-spine/practitioner-directory-approved-gate.json`), so the
either/or in the question mostly dissolves. My recommendation:

1. **The practitioner-directory REST sprint proceeds as the approved active
   track.** Nothing here should displace it.
2. **Sprints D1+D2 (design packet + pure selector with fixtures) are a good
   parallel plan-only/tests-only lane** — disjoint files, no runtime surface,
   suitable for a worker lane while the practitioner route sprint runs.
3. **Sprints D3/D4 (UI integration inventory and the first UI consumer slice)
   must wait behind the prompt-thread fake-provider backend pass.** That pass
   is the recommended next Bernie step per
   `docs/bernie-prompt-thread-tranche-readiness.md` and is the thing most
   likely to change snapshot/envelope shapes. Wiring UI to a selector built on
   a contract the backend pass then invalidates would churn both layers.

So: not "instead of," and not "fully behind" — D1/D2 now or next, D3/D4 after
the fake-provider backend pass.

## Strongest Reason To Do It Soon

Every Bernie UI sprint that ships before this layer exists adds more scattered
switches that will need retrofitting later, and the specific bug class this
design prevents has already occurred: the Sprint 98 screenshot blockers (raw
`missing_practitioner_id` copy shown to reception, no path back from a staged
proposal, generic `Not Found` on confirm) are all failures of exactly the
"many switches conditioned on nothing canonical" pattern. The
confirmation-state discipline in the plan — success copy only after backend
confirmation, `pressed`/`awaiting_backend` never claiming "booked" — encodes
the release-gate rules as a type rather than as reviewer vigilance.

## Strongest Reason To Delay

The selector's input contract is still moving. The fake-provider backend pass
has not run, and its stated purpose is to surface route/runtime mismatches in
the prompt-thread corpus. Building `BernieSessionSnapshot -> BernieUiViewModel`
against a snapshot schema that pass may amend creates churn in a layer whose
whole value is stability. Secondary cost: this project already carries a large
gate/guard/harness surface; an eighth named abstraction has real onboarding
cost and must earn it by deleting frontend complexity in D4, not just adding a
parallel layer.

## Answers to the Review Questions

**1. Is the event-log + statechart + derived-DAG split coherent?** Yes, and it
is already half-built. Events and the statechart exist server-side; the DAG
layer is the missing pure projection. The split matches the architecture doc's
own rule: statecharts model temporal legality, the DAG models current display
dependencies. The one incoherence risk is a *parallel* phase vocabulary — see
required change 1.

**2. Are the canonical nodes the right granularity?** Mostly. Eight nodes is
appropriate. Two adjustments: (a) `session_phase` must be bound to the
existing `BernieSessionState` enum, not a new near-duplicate; (b) `copy_mode`
is derived-of-derived — legal in a DAG but it must be declared a leaf computed
purely from the other seven nodes, with no independent inputs, or it becomes a
second place to encode policy. `confirmation_state`'s nine values mix
client-transient (`pressed`) with server-authoritative (`confirmed`) states;
keep them in one enum if you must, but tag each value's source of truth.

**3. Most likely hidden write-authority leak: `confirmation_state`,
specifically its `ready` value, with `freshness_state` as the accomplice.**
The confirm button is gated on `confirmation_state == "ready" and
freshness_state == "fresh"`. The leak scenario is gradual: first the UI trusts
the derived pair to enable confirm (fine — display), then someone "simplifies"
the confirm REST command to accept the derived view-model state instead of
re-echoing proposal/freshness/evidence IDs, and the backend's recomputation
step (API spine ADR proposal pattern, steps 5–6) quietly becomes a rubber
stamp. `identity_state` is the runner-up: a derived `recognized` value must
never be read as permission to silently link a patient — recognition
sufficiency is the backend's call under the interaction-model rules.

**4. Where should the first selector live?** Under `app/services/bernie/` as a
backend contract, computed server-side and delivered inside the existing
snapshot/read-model responses — with one honest caveat. The taskpane/diary
frontend is plain no-build JS, so a Python selector cannot be shared code;
whatever the frontend renders is either (a) a view model the backend already
computed, or (b) a JS reimplementation that will drift. Choose (a): the
backend selector is the contract and the tested artifact, the frontend becomes
a dumb renderer of view-model fields, and the future GraphQL `bernieSession`
read model (API spine ADR) is the natural long-term delivery surface —
"confirmation readiness as display state only" is already reserved there.
Exception: purely client-transient states (`pressed`, in-flight request) stay
in the frontend by necessity; the plan should name them explicitly as the only
client-owned inputs.

**5. Minimum fixture matrix before any UI wiring sprint** (each fixture = one
snapshot + one expected view model):

- The ordinary release-gate flow (Margaret Thompson / Dr Shera, synthetic
  evidence labelled as such) captured at every phase: instruction, candidates
  available, proposal staged, confirmation ready, pressed, awaiting_backend,
  confirmed.
- `empty_after_search` no-slot state showing no-slot copy plus suggestion
  actions, never "found these times."
- Clarification states: ambiguous patient identity; unclear/invalid reason
  code.
- Stale via diary navigation/refresh while a proposal is staged: confirm
  hidden, stale warning shown, refresh path visible.
- Backend rejection (`failed`): retry/edit visible, no success copy.
- Freshness mismatch after press (`awaiting_backend -> stale`).
- `identity_state=ambiguous` with a proposal present: proposal blocked, no
  confirm.
- Terminal `confirmed`: candidate list hidden, success copy, confirm gone,
  verification details collapsed.
- **Negative assertions on every pre-confirmed fixture:** copy never contains
  "booked"/"confirmed", raw UUIDs, snake_case codes, or `Not Found` (the
  Sprint 98 blocker classes).
- **Fail-closed fixture:** a snapshot with an unknown enum value must produce
  a blocked/technical-details view model or a raised error — never permissive
  defaults.

**6. Sequencing** — answered above: D1/D2 as a parallel plan-only lane now,
D3/D4 behind the fake-provider backend pass; nothing displaces the approved
practitioner-directory sprint.

**7. Does the plan preserve the read-hints-are-not-write-grants rule?** Yes as
written — REST confirm remains the only write path, and the view model is
display state. But preservation is currently by intent, not by mechanism; see
required changes 5 and 6 for making it structural.

## Required Changes Before Implementation (D2)

1. **Bind `session_phase` to `BernieSessionState`** (`app/services/bernie/
   session.py`) rather than defining a parallel phase enum. A second
   vocabulary is a new cross-file invariant of exactly the kind CLAUDE.md
   warns fails silently.
2. **Tag every node value with its source of truth**: server-snapshot-derived
   vs client-transient. The selector must be structurally unable to produce
   `confirmation_state=confirmed` or `copy_mode=success` unless the input
   snapshot carries a backend-confirmed field.
3. **Declare `copy_mode` a leaf node** computed only from the other nodes, or
   fold it directly into view-model output fields.
4. **Fail closed on unknown input**: unknown enum values or missing required
   snapshot fields map to a blocked/technical-details view model or raise —
   matching the fail-closed pattern already used in the interpretation
   harness (H49).
5. **Name the real input type.** The plan says `BernieSessionSnapshot`, which
   does not exist; the existing schema is `BernieSessionSnapshotOut`
   (`app/schemas/appointments.py:1201`). D2 must either consume it or define
   a versioned superset with an explicit mapping, so the selector is anchored
   to the contract routes actually return.
6. **Add an explicit no-write-echo rule**: derived view-model fields must
   never appear in confirm command payloads, and the selector must never emit
   `writes_authorized`-style fields. Confirm continues to echo
   proposal/freshness/evidence identifiers only, and the backend continues to
   recompute before writing. Add a test asserting the view-model schema
   contains no such field names.
7. **Decide and record the frontend consumption mechanism** (backend-computed
   view model in snapshot responses, per Q4) in the plan itself, since
   the no-build frontend makes "shared selector code" impossible.

## Recommended First Sprint Shape

One bounded plan-only/tests-only sprint combining D1 and D2:

- the amended plan packet (changes above applied);
- `app/services/bernie/ui_view_model.py` — pure selector, no imports of
  routers, providers, DB models, H15/H-series fixtures, or local ignored
  outputs;
- `tests/fixtures/bernie_ui_view_model/*.json` covering the fixture matrix in
  Q5;
- `tests/test_bernie_ui_view_model.py` including the negative copy assertions
  and the fail-closed case;
- a source-isolation guard in the style of H57 proving no production route
  imports the selector *yet* (it becomes route-consumed only in D4 after
  review).

No frontend edits, no route changes, no schema changes to existing responses.
D3 then runs as an inventory-only packet after the fake-provider backend pass.

## No-Go Boundaries That Must Remain Closed

This review approves none of the following, and D1–D3 must not touch them:

- live provider calls; provider prompt wiring; provider dry-run wiring;
- runtime route wiring from the interpretation harness;
- memory/RAG/GraphRAG runtime wiring;
- H15/H-series runtime imports; historical diary material access;
- GraphQL mutations; new GraphQL resolvers;
- external patient clients; model-to-database writes;
- appointment writes outside existing REST command handlers.

D4 (first UI consumer slice) additionally requires its own review after D2/D3
evidence exists, route-intercepted Playwright evidence labelled as such, and
no change to confirm command payload shape.

## Residual Risks

- **Dual-implementation drift**: the Python selector is the contract but the
  browser renders JS; until D4 replaces the scattered `bernie*Copy` functions,
  two truths coexist. Mitigate by making D4 delete frontend logic, not wrap it.
- **View model mistaken for authority later**: a backend-served
  `confirmation_state=ready` will look authoritative to future contributors.
  The no-write-echo test (change 6) is the mechanical defence; keep it.
- **`pressed` is unavoidably client-owned**, so the "one pure selector" story
  has a small honest hole. Contain it by enumerating client-transient inputs
  in the plan rather than letting them accrete.
- **Copy-safety lives in fixtures, not a lint**: new copy strings added
  outside the fixture matrix can bypass the negative assertions. A future
  copy-lint over view-model output strings would close this; not required for
  D2.
- **Schema churn from the fake-provider backend pass** may force selector
  rework; accepted, since D2 is cheap relative to retrofitting the UI.
