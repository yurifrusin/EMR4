# plan-claude-claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments` |
| Status | pending_plan_review |
| Created | 2026-07-03 19:05 +1000 |
| Source HEAD | `1ef7c50` |

## Plan Summary

Revised Fable architecture plan: accept amendment 1 (rehome reception frames+policy into diary domain in N1), accept principle / modify mechanics of amendment 2 (suggestion envelope + adapter normalization, not three catalog actions), meet amendment 3 in the middle (typed practice knowledge graph substrate as new K1 sprint, GraphRAG machinery still deferred behind the same interface). Advisory-only adversarial test lands in N1. Plan-only.

## My Understanding

Ariadne/Yuri reviewed the Fable native-diary consult and raised three amendments recorded in orchestration/bernie_native_diary_agent_notes.md and the task packet: move reception evidence frames and deterministic reception policy into the diary domain immediately; treat suggested next actions as multi-author (human + agents) inputs that must normalize to typed DiaryActionIntent before deterministic validation; reconsider deferring GraphRAG because Bernie may be the safest proving ground for the shared retrieval substrate.

## Intended Surface / Boundary

Coordination artifacts only: this plan packet and the source task packet status/notes. Future implementation surface named for each amended sprint (app/services/diary/, app/services/bernie/, appointments.py, tests; K1 adds knowledge substrate tables + retrieval interface). Must-not-change surfaces: diary grid geometry, booking modal, Waiting Room cards, taskpane, Word surfaces, reception_policy wire contract and bernie.reception_context.v1 schema literal.

## Out Of Scope

No production code, migrations, UI, route/schema changes, GraphRAG store, vector pipeline, or LLM extraction. No master/handoff movement. Stop after submit.

## Files I Expect To Edit

orchestration/agent_inbox/codex/plan-claude-claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments.md and the source task packet only

## Implementation Steps

Full revised plan body appended to this packet: amendment verdicts (accept / accept-principle-modify-mechanics / modify), revised N1 scope with frames+policy rehome and multi-author envelopes including DiaryActionSuggestion, unchanged N2/N3, new K1 knowledge-substrate sprint after N2, N4 unchanged plus suggestion persistence, first sprint recommendation amended N1 with N1a/N1b split fallback

## Visual / Behavioural Acceptance Checks

Packet states an explicit accept/modify/reject verdict per amendment with reasons grounded in current code; implementation-ready amended N1; GraphRAG/testbed implications explained; deterministic diary authority over availability and mutations preserved; advisory-only adversarial test placement stated (N1, extended K1)

## Risks / Ambiguities

N1 scope growth vs pure-move discipline; wire/naming regression on reception_policy and schema_version literal; suggestion channel becoming a shadow write path if its invariant test lags the envelope; K1 scope creep toward premature graph machinery; author-enum churn

---

# Revised Consulting Plan — Bernie Native Diary Architecture, Amended (Claude Fable 5)

> **Pause before execution.** This is a plan-revision packet. Nothing below is
> authorization to implement. Each sprint still needs its own packet, plan gate,
> and explicit `complete sprint task` release.

## R1. What Was Reviewed for This Revision

The original Fable consult packet
(`plan-claude-claude-bernie-native-diary-agent-architecture-consult.md`),
`orchestration/bernie_native_diary_agent_notes.md` (both amendment entries),
the revision task packet, protocol alerts, and — to ground the verdicts in
code rather than memory — the current `app/services/bernie/` package
(`frames.py` 185 lines, `policy.py` 126 lines, `capabilities.py`,
`session.py`, `temporal.py`, facades), the `reception_policy` consumers in
`app/routers/appointments.py` (~1578/1608), `app/schemas/appointments.py`
(755/803), `docs/diary/diary.js` (382–402, 2132, 4944, 5045), and the tests
that pin the wire contract (`test_bernie_context_frames.py`,
`test_bernie_interpret_booking_instruction.py`, `review/test_diary_smoke.py`
reception-policy cases). No production files were edited.

## R2. Verdicts at a Glance

| # | Amendment | Verdict |
|---|---|---|
| 1 | Move reception frames + deterministic reception policy into the diary/reception domain in N1 | **Accept** (with wire-compatibility mechanics) |
| 2 | Multi-author suggested next actions; assess propose/normalize/validate split | **Accept the principle; modify the mechanics** — one new suggestion envelope + adapter contract, not three catalog actions |
| 3 | Bernie as early constrained GraphRAG proving ground instead of a plain facts table | **Modify — meet in the middle**: build the graph-*shaped* substrate and shared retrieval interface now (new sprint K1), keep GraphRAG *machinery* (vector/extraction/graph DB) deferred behind that same interface |

The load-bearing invariants of the original plan are unchanged by all three
verdicts: deterministic diary authority over availability, roster truth, slot
validity, and mutations; evidence-gated confirmation; no autonomous tool loop;
retrieval advisory-only.

## R3. Amendment 1 — Frames and Reception Policy Move to the Diary Domain: ACCEPT

The original plan kept `frames.py`/`policy.py` under Bernie "unless the
ordinary diary UI starts building frame sets itself." On re-examination that
trigger has effectively half-fired already, and the original position was
applying my own §2.2 logic inconsistently.

**Why accept:**

1. **The revisit condition is already partially met.** Sprint 107 made the
   diary UI a first-class *consumer* of `reception_policy` — the policy
   decision object is already the shared truth for what the human surface may
   render. The distance from "consumes policy output" to "participates in the
   evidence language" is one sprint, and Rayleen/Davida make additional
   consumers a certainty, not a possibility.
2. **Symmetry with the catalog argument.** §2.2 of the original plan argued
   the capability registry must move *now, while there is one importing
   consumer, because moving after Rayleen/Davida import it is expensive*. That
   argument applies identically to the frame vocabulary and the policy
   evaluator. Keeping them Bernie-side was the same "bolted-on shape expressed
   as module paths" mistake, one layer down.
3. **The code confirms the move is cheap.** Both modules are pure contract
   code: no LLM, no DB, no wall-clock, no session import; `policy.py` imports
   only `frames.py`; the router consumes both via the `app.services.bernie`
   facade. This is mechanically the same pure-move-plus-facade slice as the
   temporal-policy rehome the original N1 already contained.
4. **The vocabulary is author-neutral evidence.** Seven of the eight frame
   types (`requested_appointment`, `patient_booking_context`,
   `roster_schedule`, `slot_search`, `advisory_warning`, `stale_evidence`,
   `guardrail_outcome`) describe facts about proposed diary work with no
   Bernie-specific semantics. `model_uncertainty` is agent-flavoured but
   generalizes to *any interpreting author* (Davida's compile stage will emit
   it too); human-UI authors simply never produce one. **Do not split the
   discriminated union across packages** — the union type and the policy
   evaluator iterate over all frame types and must stay whole.

**Mechanics (the modifications):**

- Rehome `frames.py` and `policy.py` into `app/services/diary/` as a unit, in
  the same N1 slice as the catalog and temporal rehomes. Bernie keeps
  import-compat facades exactly as Sprint 106A did.
- **Wire compatibility is non-negotiable in N1.** The
  `schema_version: "bernie.reception_context.v1"` literal and the
  `reception_policy` response field name are asserted by tests and consumed
  by `diary.js`; both stay byte-identical. Rename Python symbols to neutral
  `Reception*` names with `Bernie*` aliases exported from the bernie facade
  (or defer the rename entirely — sprint-plan decision). A
  `reception_context.v2` schema id may exist only when a real contract change
  ships (e.g. the `knowledge` frame type in K1), never as part of a move.
- **Division that survives the move:** frame *definitions* and the policy
  *evaluator* become diary-domain; frame *assembly for a conversational turn*
  (which frames Bernie builds, in what order, from which resolver outputs)
  stays Bernie-side. Bernie retains interpretation, the session statechart,
  narration/voice, the pilot gate, and facades. The diary domain never
  imports Bernie.

This also strengthens N2: `explain_schedule` reason codes now flow through a
frame/policy vocabulary that already lives in the domain that owns schedule
truth, and the original plan's "N2-first pays a second small move" caveat
disappears.

## R4. Amendment 2 — Multi-Author Suggestions: ACCEPT THE PRINCIPLE, MODIFY THE MECHANICS

The refined principle is adopted verbatim as a named architecture invariant
(the **suggestion invariant**):

> Any participant may suggest. Only the diary domain may validate. Only
> confirmed typed actions may mutate state.

The original §4.1 listing of `suggest_next_actions` as Bernie-authored was
indeed too narrow. Accepted changes: the action's authorship widens to
`human | bernie | rayleen | davida | system`; every envelope carries author
provenance from day one; and the invariant gets its own adversarial test.

**On the proposed three-way split** (`propose_next_action` /
`normalize_next_action` / `validate_next_action`): the *stages* are exactly
right; making them three **catalog actions** would be a mistake. Verdict:
model the stages as **one new envelope + one adapter contract + the existing
tiers**, not as new catalog rows.

1. **`validate_next_action` already exists — it is the propose tier.** An
   intent submitted to the diary domain and answered with a deterministic
   `DiaryActionProposal` (warnings, blocks, freshness id, confirmation
   requirement) *is* validation. A separate validate action would create a
   second validation grammar beside the proposal flow — re-introducing the
   three-grammar disease this whole plan exists to cure.
2. **`normalize_next_action` is per-author adapter machinery, not a diary
   action.** Bernie's interpreter normalizes natural language; a UI gesture is
   *born normalized* (a drag already arrives as typed coordinates — the
   client/route constructs the intent deterministically); typed agents author
   intents natively; a future SMS/kiosk channel normalizes in its own
   adapter. Putting normalization in the diary catalog would drag NL
   interpretation into the domain package that must never import an LLM.
   Instead: a **normalization contract** — every author-side adapter must
   emit a well-formed `DiaryActionIntent`; nothing else crosses the boundary.
3. **What deserves first-class typing is the artifact, not the stage.** Add a
   fourth envelope to the original §4.2 set:

   - `DiaryActionSuggestion` — author kind + authenticated actor, channel
     (`nl_text | ui_gesture | agent_policy | system_rule`), raw content ref,
     optional pre-normalized `DiaryActionIntent`, turn/frame refs, and
     **zero write authority by construction**: a suggestion can never carry
     freshness evidence the confirm gate accepts.

   Suggestions become storable, auditable, narratable conversation-layer
   artifacts shared by all participants — which is what makes the two-way,
   multi-agent conversation Yuri describes buildable without ever opening a
   second write path.

**Pipeline as adopted:** suggest (any author, `DiaryActionSuggestion`) →
normalize (author-side adapter, output `DiaryActionIntent`) → validate (diary
domain, propose tier, output `DiaryActionProposal`) → confirm (evidence-gated,
staff-confirmed, `DiaryActionConfirmation`). Only the last stage mutates.

**Catalog consequence for N1:** catalog rows gain an `allowed_authors` field,
so the completeness test asserts authorship policy per action, and
`suggest_next_actions` keeps its read-only tier with widened authorship.

## R5. Amendment 3 — GraphRAG Timing: MODIFY (MEET IN THE MIDDLE)

Yuri's counterargument lands two real hits on the original dissent:

- **The proving-ground logic is sound.** If EMR4 is committed to a
  multi-agent future where Scribe/Consultant/Davida need retrieval, the
  substrate's *contract and integration shape* should be debugged where wrong
  answers are cheap, verifiable, and advisory-only — reception facts — not
  first encountered where they are clinical. The original "wait for a corpus"
  position underweighted this derisking value.
- **Bernie's knowledge base is genuinely graph-shaped.** Practitioner ↔
  appointment-type ↔ policy ↔ patient-relationship links with validity
  windows are edges, not rows in a flat facts table; pretending otherwise
  would build a second data model to throw away.

But "GraphRAG" bundles four separable commitments: (a) a graph-shaped data
model, (b) deterministic graph traversal retrieval, (c) LLM-based graph
extraction from an unstructured corpus, (d) vector/hybrid semantic search.
Bernie's small, verifiable knowledge base justifies (a) and (b) **now**;
(c) and (d) still have no corpus and no second consumer, and deploying their
machinery early is cost and attack surface with nothing to retrieve.

**Revised recommendation — replace the "typed practice-facts table" (original
§12.3) with a typed practice knowledge graph substrate, built as new sprint
K1:**

- **Storage:** practice-scoped entity + typed-edge tables (nodes:
  practitioner, appointment type, practice policy/rule, patient-relationship;
  edges typed, with provenance, validity window, and practice-admin CRUD).
  Plain relational storage — consistent with the existing pgvector/rag model
  space but requiring no graph DB, no embeddings, no new runtime dependency.
- **Interface:** one retrieval entry point,
  `retrieve_advisory_context(...) -> list[AdvisoryFact]`, that emits **only**
  advisory facts with source attribution, surfaced into turns as a new
  `knowledge` frame type (source literal `knowledge_store`).
- **The GraphRAG testbed claim is honest here:** this substrate *is* a small
  knowledge graph and *is* v1 of the shared retrieval layer. When Davida's
  unstructured corpus (practice manual, policies, correspondence) exists,
  extraction and vector lanes plug in **behind the same interface** — the
  consumers (Bernie narration, Davida onboarding, Rayleen advisories) never
  change shape. That is the substrate-derisking Yuri wants, bought without
  premature machinery.
- **The hard boundary is unchanged and gains a mechanism:**
  `evaluate_reception_context` counts `knowledge` frames as advisory only;
  availability classification remains derivable exclusively from
  `roster_schedule`/`slot_search` frames; the type layer rejects
  knowledge-sourced roster/slot frames. A graph fact can colour narration
  ("Mrs Thompson usually sees Dr Shera") but can never flip
  `can_offer_candidates`, fabricate a no-slot state, or touch roster truth,
  slot validity, or any mutation.

**Escalation criteria to full GraphRAG machinery** (all three required): a
real unstructured multi-hop corpus exists; a second consuming agent needs it;
and the K1 interface has been in production use by Bernie long enough that
its contract is stable. Adopting (c)/(d) earlier requires a new consult.

## R6. Where the Advisory-Only Adversarial Test Lands: N1

The boundary test must exist **before any retrieval integration exists** —
that was already the original plan's position, and amendment 3 makes it more
important, not less. Placement:

- **N1:** property-style adversarial test over `evaluate_reception_context`
  (rehomed): no combination of advisory- or model-sourced frames may yield
  `roster_unavailable` or `search_ran_no_candidates`, flip
  `can_offer_candidates`, or unblock a confirmation; model-sourced
  `roster_schedule`/`slot_search` frames are rejected at the type layer. This
  lands in the same sprint that moves the policy evaluator, so the boundary
  is pinned in its new home from day one.
- **K1:** the same test extends to the `knowledge` frame type and the
  retrieval interface the moment they exist (knowledge-sourced availability
  frames rejected; knowledge frames classified advisory-only).
- **N3:** the suggestion-injection variant (below) joins the confirm-gate
  test family.

## R7. Revised Sprint Sequence

| Sprint | Content | Risk | Behaviour change |
|---|---|---|---|
| **N1 (amended) — Diary/reception domain package, envelopes, boundary tests** | Create `app/services/diary/`; rehome **four** units as pure moves with bernie facades: action catalog (+ human-UI actions `propose_edit/cancel/status/waiting_area`, + `allowed_authors`, + audit codes), canonical temporal policy, reception frames, reception policy. Add **four** envelope contracts (internal only): `DiaryActionIntent` / `DiaryActionProposal` / `DiaryActionConfirmation` / `DiaryActionSuggestion`, all with author provenance (`staff_ui | bernie | rayleen | davida | system` + authenticated actor). Tests: catalog completeness over router mutations incl. authorship; availability-provenance adversarial test (§R6); temporal single-source; suggestion-cannot-mutate contract test. Wire strings (`reception_policy`, `bernie.reception_context.v1`) byte-identical. | Low | None — suite green unchanged, JSON byte-identical |
| **N2 — `explain_schedule` + copy catalog** (absorbs Sprint 108) | Unchanged from the original plan, now born directly in the diary domain; reason codes flow through the rehomed frames → policy → copy catalog keyed `(state, reason_code)`. Amendment 1 removes the second-move cost the original plan tolerated. | Medium-low | Copy/diagnostics improve; no write-path change |
| **N3 — Unified evidence-gated confirm** | As originally planned (generalize `confirm-bernie`; human dialogs echo proposal evidence; HMAC-sign evidence; close None-is-fresh for grammar-routed confirms; deprecation window; backend-first deploy). Additions from amendment 2: every confirmation logs author provenance; confirm-gate tests include suggestion-injection (a `DiaryActionSuggestion` or its embedded intent posted to any confirm/mutation endpoint → typed 409). | High | Human confirm flow semantics |
| **K1 (new) — Typed practice knowledge substrate** | Entity/edge tables + migration; `retrieve_advisory_context` interface; `knowledge` frame type + advisory-only policy extension; practice-admin CRUD; first consumer: Bernie narration advisories. Extends the N1 adversarial test. Explicitly excluded: vector store, embeddings, LLM extraction, graph DB, multi-hop LLM reasoning. Runnable after N2; parallelizable with N3 (disjoint file surface: new tables/service/frame type vs confirm-path endpoints). | Medium | Additive — narration gains advisory colour; no availability or write-path change |
| **N4 — Persisted session + domain event log** | As originally planned, still gated on the §10 Yuri decisions (PHI/retention, TTL, concurrency). Addition: persisted `DiaryActionSuggestion` artifacts land here with the session/event-log migration decision — same audit substrate. | High | Session semantics move server-side |

**First implementation sprint recommendation: amended N1.** It is larger than
the original N1 (two more rehomed modules, one more envelope, one more test
family) but identical in kind — the proven Sprint 106A pure-move pattern plus
additive contracts, still strictly no-behaviour-change. If Ariadne prefers
smaller review units, split as **N1a** (four rehomes + facades, suite green
unchanged) and **N1b** (envelopes + `allowed_authors` + the three contract
test families); N1a before N1b, both trivially plan-gated.

## R8. Risks (Revised)

New or changed relative to the original §15:

- **N1 scope growth.** Four rehomes + four envelopes + three test families in
  one sprint invites mixed commits. Mitigate: pure moves and additive
  contracts in separate commits; unchanged-suite rule per commit; the N1a/N1b
  split as the fallback.
- **Wire/naming regression.** `reception_policy` and
  `bernie.reception_context.v1` are pinned by backend tests, the smoke
  harness, and `diary.js`. The move must keep them byte-identical; symbol
  renames happen only behind facade aliases. A grep-based invariant check
  (both literals present, single definition site) is cheap insurance.
- **Suggestion channel as a shadow write path.** The risk amendment 2 creates
  is an eager consumer treating a suggestion's embedded intent as executable.
  Mitigate: the suggestion-cannot-mutate test lands in N1 *with* the envelope
  — never after a consumer exists; suggestions structurally cannot carry
  confirm-grade evidence.
- **K1 scope creep toward premature machinery.** The substrate's boundary is
  data + deterministic traversal + one interface. Embeddings, extraction,
  graph DBs each require the R5 escalation criteria and a new consult.
- **Author-enum churn.** Author kinds will grow (kiosk, SMS, portal). Keep
  the author kind a closed enum per contract version with explicit version
  bumps — not a free string — so the audit trail stays queryable.
- **Carried over unchanged:** N3 breaking-flow rollout, evidence key
  management/expiry, N4 PHI/TTL/concurrency decisions, `diary.js` monolith,
  grammar over-engineering boundary (catalog stays data + Pydantic, no
  plugin/dispatch framework).

## R9. Acceptance Tests (Delta Over Original §16)

Original §16 checks all stand. Added or modified:

- **Rehome integrity (N1):** full backend suite green unchanged; the
  `reception_policy` JSON payload byte-identical on interpret/supervised
  routes; `schema_version` literal unchanged; bernie facade imports and new
  diary-domain imports resolve to the same objects.
- **Authorship policy (N1):** every catalog row declares `allowed_authors`;
  the completeness test asserts action + tier + confirmation requirement +
  allowed authors for every mutating router path.
- **Suggestion invariant (N1, extended N3):** no mutating endpoint accepts a
  `DiaryActionSuggestion`; a suggestion's embedded intent carries no
  freshness evidence acceptable at the confirm gate; N3 adds live
  suggestion-injection at confirm endpoints → typed 409.
- **Advisory-only provenance (N1, extended K1):** as §R6 — adversarial frame
  sets with advisory/model (later knowledge) frames can never produce
  availability classifications or unblock confirmation; type-layer rejection
  of model-/knowledge-sourced roster and slot-search frames.
- **K1 substrate checks:** retrieval returns only attributed advisory facts;
  validity-window filtering enforced; deterministic ordering; when the
  optional paraphrase lane ever ships, narration containing knowledge facts
  still passes the original token-provenance constraint (every date/time/
  name/count token present in the typed payload).

## R10. Dissent Recorded

- I reversed my own original position on frames/policy placement; the
  original packet's "revisit only if the diary UI builds frame sets" trigger
  was already half-met by Sprint 107 when I wrote it, and Ariadne/Yuri were
  right to call it.
- I resisted the literal three-action split in amendment 2 even though it
  came from Ariadne/Yuri: three catalog actions would rebuild the
  multi-grammar problem inside the new grammar. The adopted
  envelope-plus-adapter form preserves every property the amendment asks for
  (any author, free-form input, deterministic validation, confirm-gated
  mutation) with one new contract instead of three new actions.
- On GraphRAG I concede the proving-ground strategy but continue to refuse
  the machinery: K1 is deliberately a knowledge graph without GraphRAG
  tooling. If Yuri wants the vector/extraction lanes sooner than the R5
  criteria allow, that should be a conscious, separately-consulted decision —
  not scope drift inside K1.

## R11. Pause Before Execution

This packet is a plan revision only. No production code, migrations, UI, or
schema changes were made. Next action belongs to Ariadne and Yuri: review the
verdicts, then — only if approved — dispatch the amended N1 (or N1a) as its
own plan-gated sprint packet with an explicit `complete sprint task` release.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
