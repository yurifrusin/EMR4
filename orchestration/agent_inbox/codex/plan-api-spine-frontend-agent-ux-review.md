# API Spine Frontend And Agent UX Review

| Item | Value |
|---|---|
| Worker | Codex frontend/agent-UX planning lane |
| Sprint | API root-to-branch plan review |
| Date | 2026-07-06 |
| Scope | Planning artifact only; no production code, tests, provider wiring, H15/trove, memory, RAG, or GraphRAG |

## Read Summary

This review treats `orchestration/api_spine_programme.md` as the controlling
architecture: GraphQL should own connected read/context graphs, REST/OpenAPI
command endpoints should own explicit mutations, async event contracts should
own integrations and cross-surface state updates, and YAML manifests should
describe policy, setup, capability, and allowed context frames without becoming
a shadow runtime.

The current frontend reality is already close to this split but not yet named
that way. `docs/diary/diary.js` has a rich receptionist surface with appointment
state, template/resource reads, Bernie session events, staged booking previews,
confirm calls, admin resource commands, route-intercepted smoke modes, and
server-session idempotency keys. The Word taskpane is a patient/document-aware
SPA that reads patient summaries, history, medications, allergies, document
metadata, and diary schedule snippets, while using direct REST writes for
patient edits, file URL backfill, consult finalisation, and clinical actions.
The API Spine ADR should preserve that product learning while replacing
scattered endpoint-by-endpoint coupling with an explicit consumption model.

## Consumption Model

### Diary

The native Diary grid should become the first proof that GraphQL reads can feed
a dense operational UI without granting write authority. Its primary read query
should assemble a date/location/resource diary frame: rooms, practitioners,
rosters, breaks, appointment cards, waiting-area summaries, appointment-type
metadata, lifecycle/status policy, current user permissions, and pending
proposal/read-only Bernie context. That gives the grid one coherent render
input instead of many locally stitched REST reads.

Diary mutations should remain OpenAPI command calls with explicit intent names:
prepare booking proposal, confirm proposal, cancel appointment, change status,
resize/move appointment, update room, update waiting area, and similar actions.
Each command response should return a typed result envelope with `accepted`,
`blocked`, `warnings`, `audit_event_id`, `idempotency_key`, `correlation_id`,
and a refresh hint for the GraphQL read side. The UI should never infer that a
successful GraphQL refetch means a command was authorized.

Diary should consume async events for state that changes while the user watches:
appointment changed, proposal staged/expired/confirmed/cancelled, waiting-room
movement, SMS reply, caller-ID context, room/resource changes, and backend
policy drift. Early implementation can use polling or a narrow server-sent
event channel, but the UI contract should already label events as `observed`
state rather than command authority.

YAML manifests should reach Diary as validated capability/config frames:
available appointment statuses, reason-code policy, staff-visible labels,
feature flags, role affordances, and environment/provider posture. The Diary
should render manifest-derived controls only after the backend exposes them as
authorized UI affordances; raw YAML should not be fetched from the browser as a
source of truth.

### Word Taskpane And Command Centre

The taskpane should consume GraphQL as a patient/document context graph. A
single patient-file context read can include patient banner data, allergies,
current medications, recent encounters, active problems, available clinical
tabs, document metadata, and permissioned actions. That fits the existing
document-aware tab model from implementation plan sections 2 and 11 while
reducing the current pattern of separate lazy REST reads per tab.

Clinical and document writes should stay as OpenAPI commands: create patient
with file, update patient details, backfill document URL, start/finalise consult,
acknowledge results, draft/send correspondence, and any future prescribing or
billing operation. The taskpane UX should show command state as a command state:
drafted, pending review, submitted, succeeded, blocked, or stale. It should not
collapse those into generic toast text.

Async events matter less for the narrow taskpane but still matter for document
and clinical workflow: background scribe status, transcription complete, result
arrival, command-centre lock/ownership, file URL reconciliation, and remote
patient demographic updates. Events should be surfaced in restrained status
badges so the taskpane remains the quick navigation/control surface rather than
a noisy operations dashboard.

YAML should shape taskpane navigation and agent charters: which tabs exist for a
role, which Access AI capabilities are available, which context frames *scribe*
or *consultant* may receive, and which workflows require doctor confirmation.
The browser receives the backend's evaluated affordance frame, not raw
environment secrets or provider configuration.

### Bernie

Bernie should consume GraphQL through typed receptionist context frames, not
through broad practice diary dumps. The minimum useful frame sequence is:
selected diary context, caller/patient candidate context when available,
patient-specific booking history and future bookings, requested
date/time/resource availability, relevant policy/manifest labels, and current
proposal/session state. Each frame should carry provenance, freshness,
confidence, and whether it is deterministic API fact, staff-selected context,
caller-ID signal, model interpretation, or route-intercepted fixture evidence.

Bernie writes should remain OpenAPI commands with human confirmation in the
middle: interpret or prepare proposal may be read-only/proposal-producing, but
confirm booking, status changes, waiting-area moves, and patient linking must
go through signed command endpoints with audit and idempotency. The existing
Bernie session/event model in the Diary can become the UX precedent: each turn
has a server revision, idempotency key, and explicit event type; commands should
return typed failure envelopes rather than raw route or ID errors.

Async events are central to Bernie. A proposal staged by Bernie should appear
as an event in the diary grid and chat transcript, with expiry and conflict
updates. Staff selection, clarification replies, confirm submission, stale
session detection, provider/fake-provider interpretation status, and proposal
confirmation should all be event-shaped so the UI can recover from reloads and
multi-user reception work.

YAML should give Bernie read-only schema literacy: action grammar, status
labels, reason-code policy, capability tier, and which context frames it may ask
for. That literacy must stay visibly separate from authority. Manifest-derived
knowledge can help Bernie say "I can prepare this for confirmation"; it cannot
let Bernie claim availability, verify identity, or write the diary.

### Davida

Davida should be treated as a practice-operations copilot over manifest and
setup state, not as a direct administrator with ambient write power. GraphQL
reads should give her evaluated setup/profile frames: practice locations,
rooms, practitioners, onboarding progress, feature flags, provider readiness,
permission gaps, setup-path dry-run outcomes, and audit summaries.

Davida mutations should be command-style and reviewable: validate manifest,
run setup-path dry-run, apply approved setup step, rollback step, enable
feature, invite user, update practice profile, or generate an admin checklist.
Even setup/onboarding work should be command-backed because it can change cloud,
identity, billing, or practice configuration.

Async events should report long-running setup progress, external provider
verification, IAM propagation, billing readiness, failed rollback, and security
review blockers. Davida's UX should feel like an operations runbook with
explicit checkpoints, not a chat box that silently changes infrastructure.

YAML is Davida's native planning material. She may explain and validate setup
paths, environment manifests, capability manifests, and onboarding manifests,
but only the backend command layer should execute or persist changes.

### Consultant

*consultant* should consume GraphQL patient-context frames plus cited
knowledge-source frames. The patient side should be deliberately curated:
current consult note, active problems, allergies, medications, recent relevant
results, key past history, and doctor-selected questions. Knowledge-base reads
should include citation ids, source freshness, licence boundary, and whether
PHI was permitted in the query.

Clinical writes should remain doctor-confirmed commands: insert draft note,
finalise consult, create letter, acknowledge result, request test, or create
prescribing draft. *consultant* output should be advice/draft/proposal until the
doctor confirms a command. It must not call provider APIs directly from the
browser or taskpane.

Async events for *consultant* should cover background evidence retrieval,
transcription/note extraction completion, result arrival, citation refresh, and
draft generation state. The UX should distinguish "retrieved evidence",
"model synthesis", "doctor accepted", and "record written".

YAML should define *consultant* charters: allowed knowledge sources, required
citations, output contract, safety phrases, and confirmation requirements. The
runtime still owns authorization, PHI handling, provider policy, and audit.

## Context-Frame UX Implications

Context frames should become visible UX material, not invisible prompt stuffing.
Each agent panel should show compact evidence chips or an expandable "What I am
using" drawer with frame type, source, freshness, confidence, and authority
level. Suggested labels:

- `Live API fact`: non-intercepted backend read from the current environment.
- `Staff selected`: explicit human selection in the UI.
- `Caller signal`: identity/context hint that still needs staff verification.
- `Manifest policy`: backend-evaluated capability or policy frame.
- `Model interpretation`: agent output, never write authority.
- `Fixture/intercepted`: route-intercepted, fake-provider, smoke, or authored
  synthetic evidence.

Agent copy should reflect those labels. Bernie can say "I found available
candidate slots from the diary API" only for live/non-intercepted reads. In
route-intercepted checks the UI and closeout evidence should say "fixture
candidate slots rendered" or "route-intercepted candidate slots rendered".
Consultant should say "Cochrane citation retrieved" only when the knowledge
source frame is actually returned by the configured backend path; otherwise it
should say "fixture citation" or "draft citation shape".

The most important UX invariant is authority separation. Reads explain what the
system knows, commands ask the system to do something, events tell the user what
changed, and manifests explain what is allowed. The UI should preserve those as
separate visual states.

## Route-Intercepted Vs Live Evidence Labelling

The existing Bernie release-gate language should become an API Spine standard:

- If Playwright uses `page.route(...)`, Office is stubbed, `?smoke=true` is
  active, fixture payloads are served, a fake provider is used, or backend routes
  are intercepted, evidence is `route-intercepted` or `fixture/fake-provider`.
- If the UI renders in a real browser but API calls are intercepted, it is still
  not live evidence.
- A live UI check requires non-intercepted browser calls to the intended backend.
- A live-provider check additionally requires provider metadata showing
  `live_provider: true`.
- Closeout notes and screenshots should carry the label in their title or first
  sentence, not only in fine print.

For frontend prototypes, add a small evidence banner in review mode:
`Evidence mode: route-intercepted fixture`, `Evidence mode: local live backend`,
or `Evidence mode: live provider`. This should be driven by backend/debug
metadata, not by a worker's prose after the fact.

## First Five Frontend/API-Consumption Prototype Checks

1. Diary GraphQL read-shape mock: define one non-invasive fixture or schema
   draft for `DiaryDayContext` that can render the current diary grid without
   extra REST reads for appointments, resources, breaks, policy labels, and
   current permissions.
2. Diary command-envelope review: map the current Bernie confirm/create proposal
   and room/waiting-area writes to a proposed OpenAPI command envelope with
   idempotency, correlation id, typed blocked reasons, warnings, and refresh
   hints.
3. Bernie context-frame drawer prototype: using authored or route-intercepted
   data only, show staff which frames Bernie used and whether each frame is
   live API fact, staff selection, model interpretation, manifest policy, or
   fixture/intercepted evidence.
4. Taskpane patient context query sketch: replace the current mental model of
   separate summary/history/meds/allergies reads with a single patient-document
   context graph and list which panels can render from it without changing
   production code yet.
5. Evidence-mode closeout check: add a planning/review checklist that every
   future UI smoke, screenshot, or release gate must state route-intercepted vs
   live backend vs live provider before claiming pass/fail.

## Risks And Dissent

- GraphQL can become a tempting write tunnel. The ADR should explicitly forbid
  high-risk mutations in GraphQL until a later reviewed exception exists.
- A single "mega query" could make the Diary slower or harder to cache. Prefer
  named context-frame queries with stable fragments rather than one unbounded
  practice graph.
- YAML manifest enthusiasm could leak raw config to browsers. Frontends should
  receive evaluated affordances and labels, not secrets, provider config, or
  policy internals that imply authority.
- Bernie UX may over-trust manifest literacy. Labels must keep schema knowledge
  separate from live diary evidence and staff-confirmed writes.
- The taskpane remains constrained inside Word. GraphQL may improve data shape,
  but workflows needing microphone, broad review panes, or sustained focus
  should continue moving to Command Centre/Diary surfaces instead of forcing all
  agent UX into the sidebar.
- Davida could become an all-powerful admin chat if setup commands are too
  broad. Keep setup commands granular, dry-run first, and auditable.
- Consultant evidence frames will need licensing and PHI policy before live
  knowledge-base use. Do not let the frontend prototype imply clinical evidence
  runtime readiness.
- Current route-intercepted smoke coverage is useful but can create false
  confidence. The evidence label rule should be treated as a release blocker,
  especially for Bernie booking and provider claims.
