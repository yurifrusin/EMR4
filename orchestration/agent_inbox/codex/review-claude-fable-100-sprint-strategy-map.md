# Fable Strategy Review — EMR4 100+ Sprint Strategy Map

| Item | Value |
|---|---|
| Author | Fable (Claude high-reasoning strategy collaborator) |
| For | Ariadne / Codex orchestrator + Yuri |
| Mode | Strategy collaboration only — no production code, no runtime/provider/trove wiring |
| Date | 2026-07-06 |
| Inputs read | AGENTS.md, implementation_plan.md, phase_programmes.md, sprint_closeout.md (H69), parallel_workstreams.md, api_spine_programme.md, access_ai_api_design.md, bernie_release_gates.md, protocol_alerts.md |
| Engine state at read | Paused after H69 by Yuri request |
| Status | integrated |

---

## 1. Executive Verdict

**The single most valuable next strategic move is to close the "consumer gap": stop
building blocked-by-default guardrail scaffolding and start building the one runtime
surface those guardrails were designed to protect — a live, staff-confirmed Bernie
booking loop sitting on the Access AI spine.**

The project has spent roughly H40–H69 (≈30 sprints) hardening a *provider-free
interpretation harness*: self-validating frames, snapshot assertions, readiness
checkers, guards on the guards, and reviews of the reviews. This work is high-quality
and the safety posture is genuinely excellent. But R28/Fable's own earlier verdict is
now the sharpest thing in the record and it still holds:

> **"The blocker is missing consumers, not missing guardrails."**

Every recent closeout ends with the same line — "No runtime routes, UI, providers,
database access, memory/RAG/GraphRAG, H15/H-series runtime imports were added." That is
correct discipline, but after 30 sprints it is also the tell of a programme that has
optimised its safety envelope far past its product envelope. We are building a
seatbelt-testing rig for a car that has no engine wired to the wheels.

The right response is **not** to open the blocked gates. It is to build the *missing
runtime consumer* — the Bernie booking loop and the Access AI invocation path — behind
the existing (excellent) contracts, so that the next unit of guardrail work has a real
thing to guard. Concretely: finish Programme 2G's Sprint 98 booking-loop integrity, land
the API-spine ADR (Sprint 100), and drive the Access AI invocation service (Programme
2F Sprints 82–86) to the point where one real capability — `admin.booking.interpret` —
flows through capability policy → entitlement → provider adapter → typed proposal →
staff confirmation, with the historical trove still fully boxed.

Direction in one sentence: **pivot the centre of gravity from harness-hardening to
spine-building, keep every currently-blocked gate blocked, and let the trove wait until
a runtime consumer exists to justify opening H15 further.**

---

## 2. Proposed 100+ Sprint Map (bands, not a fixed schedule)

This is a *map of terrain*, not a Gantt chart. Bands are ordered by dependency and
value, sized ~8–15 sprints each. Later bands are deliberately coarser — we should not
pretend to know sprint 80's exact shape from here. Sprint numbers below are *band-local
ordinals* (B1-1, B1-2…) so they don't collide with the existing global counter; Ariadne
maps them onto the real sequence at dispatch time.

### Band 1 — Bernie Booking Loop + API Spine Foundation (the consumer gap) — ~10 sprints
Goal: one real, staff-confirmed booking loop on a documented spine.
- Stabilise Sprint 98 booking-loop integrity (resolved practitioner never surfaces raw
  IDs; choose-another-slot path; typed confirm failures — the three screenshot blockers).
- API Spine ADR (Sprint 100) synthesising GraphQL read-graph + OpenAPI command mutations
  + async placeholders + YAML manifest layer + agent charters + security model.
- Schema prototype (Sprint 101): GraphQL SDL draft, OpenAPI command surface draft, YAML
  manifest schema, integration placeholder branches.
- API steward skill (Sprint 102) as a standing advisor on schema drift/authorization.
- Booking-loop happy-path release gate (Margaret Thompson / Dr Shera) proven as a
  blocking check, deterministic first, live-provider-deferred and labelled as such.

### Band 2 — Access AI Runtime Spine, Boxed Providers → First Live Capability — ~12 sprints
Goal: the Access AI service becomes the *only* path to any model, fake first, then one
carefully opened live capability.
- Access AI invocation service (Sprint 82) as single entry point; fake-provider only.
- Invocation audit + cost envelope (Sprint 83); typed audit event catalog hardening.
- Enterprise auth seam design (Sprint 84) — org/role/FGA mapping, no third-party dep yet.
- Bernie interpreter migration (Sprint 85) — route interpretation through Access AI,
  guards intact, still default-disabled.
- Copilot/scribe migration (Sprint 86) — scribe/extraction/letters behind Access AI with
  no user-visible change.
- **Gate event:** first *live* capability enablement (`admin.booking.interpret` or
  non-PHI live smoke) — requires explicit Yuri review, budget alerts, dev-only, non-PHI
  fixtures. This is the first place a currently-blocked boundary is deliberately opened,
  and it must be its own reviewed sprint, not a side effect.

### Band 3 — Safe Appointment Mutation Workbench Completion (Programme 2B) — ~10 sprints
Goal: every high-risk receptionist write is a proposal → confirmation → audit path.
- Drag/reschedule design + backend contract; cancel/no-show/DNA confirmation semantics.
- Recurrence + reason-note polish; duplicate-review and patient-search alert hardening.
- Caller context identity source (Sprint 87) + pending Bernie proposal object (Sprint 88).
- Diary pending-proposal highlight UI (Sprint 89) + confirm-to-appointment bridge
  (Sprint 90) — the pending-hold experience from the Access AI design record.

### Band 4 — Reception Copilot Readiness → Bernie GA-internal (Programme 2D) — ~10 sprints
Goal: Bernie is a trusted internal receptionist copilot: suggest, propose, confirm.
- Tool-schema audit-log foundation; staff message-taking model; slot-search proposal
  contract; non-autonomous Bernie command preview.
- **This is where the native Bernie/Diary action grammar earns its keep** — the H-series
  interpretation harness finally gets a runtime consumer, promoted one verb at a time
  through the H39 promotion gates (route contract, signed confirm, evidence, audit, staff
  affordance, RBAC, UI, regression tests).

### Band 5 — Practice Messaging + Daily Admin + Davida Setup (Programmes 2E, 2C) — ~12 sprints
Goal: operational surfaces that make EMR4 a real practice tool, and self-serve setup.
- Internal message model/API + diary message panel; billing review queue; operational
  notification semantics.
- Davida setup-path expansion: CSV ingestion validation, dry-run/execute/verify/rollback
  maturity, GCP pitfall helper metadata, keyless prod posture.

### Band 6 — Knowledge Base + *consultant* Evidence Support — ~10 sprints
Goal: cited clinical decision support without autonomy.
- Multi-provider knowledge-base adapter (Sprint 91) + Wiley/Cochrane spike (Sprint 92):
  licence scope, citation handling, PHI query rules, audit metadata.
- *consultant* charter runtime: curated patient-context + cited-source frames,
  doctor-confirmation-required, no autonomous diagnosis/prescribing.

### Band 7 — Deployment/Tooling Maturity + Security Foundations (Programme 2C + §15A) — ~10 sprints
Goal: preview/promote/rollback discipline and the deferred security P1s.
- Preview deployment harness (Sprint 84-deploy), browser-smoke automation, pytest
  timeout segmentation, GitHub security alert automation.
- §15A P1s: PostgreSQL RLS tenant isolation, `audit_log` table, JWT hardening, field-level
  encryption, secrets management, threat model.

### Band 8 — Historical Diary Trove Utilisation (only after a consumer exists) — ~10 sprints
Goal: turn 58k-file trove into value *through the spine*, never as raw retrieval.
- **Precondition gate:** native Bernie/Diary action grammar stable in runtime (Band 4);
  deterministic replay harness over authored slices proven; H22 gate-review packet
  reviewed and Yuri-approved for any scope beyond the one tiny H15 local prototype.
- Then, and only then: one-time full-trove *mining* run with checkpointing and explicit
  `-AllowLargeRun` justification → validator-safe aggregate refresh → neutral transition
  graph (GraphRAG-over-derived-state, not raw) → de-identified synthetic fixture families.
- Fine-tuning (if ever) only on approved synthetic/de-identified phrasing, never raw
  diary content or authoritative transitions.

### Band 9 — Online Booking / PWA / Kiosk (Phases 3, 3B, 4) — ~12 sprints
Goal: reuse the same appointments API + Access AI spine for external clients.
- Online booking portal, patient PWA, Rayleen kiosk — each a client of the spine, each
  with its own identity-proofing security gate.

### Band 10+ — Clinical Depth (Phases 5–12) — open-ended
DDx engine, Centaur Brain historical pipeline, live RAG + Hive Mind, results/referrals,
VOIP (3CX), ePrescribing, Medicare/billing, ADHA PRODA, ambient scribe, launch prep.
Deliberately left coarse: these depend on regulatory, provider, and clinical-safety
decisions that should not be pre-committed from here.

**Total:** Bands 1–9 ≈ 96 sprints; Band 10+ carries the remainder well past 100. Treat
the count as a horizon, not a promise.

---

## 3. First 5–10 Tactical Sprints (with sequencing rationale)

Assumes Yuri lifts the H69 pause. Ordered by dependency and value.

1. **Inbox/residue cleanup enabling sprint** (small, first). Clear stale queued/pending
   Codex inbox packets and Claude branch residue flagged by `poll --fetch`. *Why first:*
   it is cheap, it unblocks clean orchestration signal for everything after, and it must
   happen *before* a fresh multi-worker band so poll output is trustworthy. Time-box it;
   do not let it grow into a project (see §6).

2. **Sprint 98 — Bernie booking-loop integrity.** Fix the three screenshot blockers
   (raw practitioner ID leak, no path back to candidate list, generic `Not Found` on
   confirm). *Why:* it is the closest thing to a real product surface and it is already
   the recommended next move in phase_programmes.md. It is also the release-gate the whole
   Bernie safety edifice is meant to protect.

3. **Sprint 100 — API Spine ADR.** Multi-agent plan-gated (Claude: domain/GraphQL
   schema; Antigravity: frontend/agent UX; DeepSeek/Codex: security/audit/deploy). *Why
   now:* Band 1 and Band 2 both hang off this decision; making it explicit prevents the
   Access AI and Bernie surfaces from diverging into two API styles.

4. **Sprint 101 — Schema prototype (non-invasive).** GraphQL SDL + OpenAPI command
   surface + YAML manifest schema drafts + integration placeholder branches. *Why:* turns
   the ADR into validatable artifacts without runtime risk.

5. **Sprint 82 — Access AI invocation service (fake-provider only).** Single backend
   entry point `AccessAiService.invoke(context, request)`. *Why here:* the booking loop
   (98) needs a home for interpretation calls; building the service now means Bernie
   interpreter migration (85) has somewhere to land, still boxed.

6. **Sprint 83 — Invocation audit + cost envelope.** *Why:* audit must precede any live
   provider opening; you cannot safely open Band 2's live gate without it.

7. **Sprint 102 — API steward skill.** *Why:* a standing advisor that keeps Bands 2–4
   from drifting the schema; cheap insurance on a long programme.

8. **Sprint 85 — Bernie interpreter migration (still default-disabled).** Route
   interpretation through Access AI with all guards intact. *Why:* this is the bridge that
   finally connects the H-series interpretation harness to a runtime path *without*
   opening a provider — the harness becomes the fake-provider contract behind the service.

Sprints 1–4 are the critical spine; 5–8 begin wiring the consumer. Stop before any *live*
provider or trove step and return to Yuri for the Band 2 gate decision.

---

## 4. Adaptation Checkpoints

Re-plan is mandatory — not optional — at each of these. Do not carry a stale map past them.

**Cadence checkpoints (every ~10 sprints / band boundary):**
- After Band 1, before Band 2: is the booking loop actually usable, or did we ADR-in-a-
  vacuum? Re-confirm the spine before wiring providers.
- After each subsequent band: re-read closeout, re-score value vs. remaining guardrail
  drift, re-rank the next band.

**Event checkpoints (trigger immediate re-plan regardless of cadence):**
- **Major gate failure** — a release gate (e.g. Margaret Thompson happy path) fails or a
  screenshot regression reproduces. Stop the band, fix or narrow, re-plan.
- **User decision** — Yuri approves/denies a live-provider opening, an H15 scope change,
  a security posture change, or a phase re-prioritisation.
- **Provider/runtime boundary change** — the first time a real provider is enabled, or a
  route/DB write path is opened, re-plan the following band with the new blast radius.
- **Security finding** — any P0/P1 discovered (RLS gap, auth bug, PHI leak, prompt-
  injection surface). Security re-plan takes precedence over feature velocity.
- **Architecture discovery** — the schema prototype or a worker plan reveals the ADR is
  wrong. Amend the ADR before continuing; do not build on a known-wrong spine.
- **Trove precondition** — before Band 8, re-run the H22 gate review and readiness check;
  if either regresses from blocked-expected values, pause the engine.

---

## 5. Gates That Must Remain Blocked

These stay closed unless a *dedicated, explicitly-reviewed, Yuri-approved* sprint opens
them one at a time. None may be opened as a side effect of feature work.

1. **Broad historical diary trove mining** — no 58k-file pass. Only the single approved
   H15 tiny local prototype (one root, one dense day, ≤80 samples, `explain_schedule`
   read-only candidates) exists, and it is not authorization for more.
2. **H15/H-series runtime imports** — `app/` production code must not import harness
   fixtures, H-series profiles, candidate builders, `local_data`, or trove paths
   (enforced by H57 isolation test — keep it).
3. **Providers** — no live model calls outside a dedicated, budget-alerted, non-PHI,
   dev-only, Yuri-reviewed enablement sprint. Fake providers remain the test/review
   default.
4. **Memory / RAG / GraphRAG** — no retrieval or memory layer wired to runtime. GraphRAG
   over *derived* neutral state is a Band-8 candidate only, post-consumer, post-H22.
5. **Database writes from model output** — every write remains a typed command with a
   human confirmer; no model response grants `writes_authorized=true`.
6. **Runtime route wiring of the interpretation harness** — the harness stays a
   test/review artifact until Band 4 promotes verbs through the H39 gates.

Standing rule: **run and record**
`.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
before any sprint that proposes touching the above. Expected:
`runtime_or_provider_wiring_ready=false`, `raw_trove_access_ready=false`,
`runtime_gate_decision=blocked`. Any drift = pause.

Important nuance: **Band 2 deliberately opens exactly one of these (a live provider) —
but through the Access AI spine, dev-only, non-PHI, and only after audit (Sprint 83) is
in place.** Opening a provider is *not* the same as opening the trove or the H15 runtime
import; keep those distinct in every review.

---

## 6. Where Inbox / Claude-Residue Cleanup Belongs

Cleanup is an **enabling workstream**, not the objective. Placement:
- **Sprint 1 of the next band** (see §3.1): a single small, time-boxed hygiene sprint to
  clear the stale queued/pending Codex inbox packets and Claude branch residue that
  `poll --fetch` reports, so orchestration signal is clean before a multi-worker band.
- **Standing hygiene, not a programme:** fold ongoing residue cleanup into each band's
  integration/realign step (the existing `record-integration` → `realign` → `audit` →
  `retire-stale` flow). Do not spawn a "cleanup programme."
- **Guardrail:** if cleanup exceeds ~1 sprint of effort, that is a signal the orchestration
  tooling needs a fix (like H69's decode tolerance), which is itself a bounded tooling
  sprint — not license to keep polishing inboxes instead of building the spine.

The failure mode to avoid: cleanup and harness-hardening are both *comfortable* work that
feels productive and carries near-zero risk. That comfort is exactly why they can crowd
out the riskier, higher-value consumer-building. Cap the cleanup, then move.

---

## 7. Dissent

**What Ariadne may be over-indexing on:**
- **Guardrail recursion.** H40–H69 built validators, then validated the validators, then
  snapshotted the validation, then guarded the snapshot, then reviewed the guard. This is
  a local maximum. The marginal safety of the 30th harness sprint is far below the
  marginal value of the 1st runtime-consumer sprint. R28/Fable already said the blocker is
  consumers — the project half-heard it (kept building grammar/replay artifacts) but did
  not cross into runtime.
- **Meta-orchestration weight.** The orchestration protocol is enormous and mostly
  excellent, but the ratio of process-doc surface to shipped product surface is high.
  Protocol should be refactored/compressed opportunistically, not extended by default.
- **Historical trove gravitational pull.** The trove is fascinating and Yuri clearly
  values it, so it keeps attracting sprints (H1–H35+) despite having *no runtime consumer*
  and a correctly-locked semantic gate. It is the single biggest sink of effort with the
  most-deferred payoff.

**Pull earlier:**
- Sprint 98 booking-loop integrity and the API Spine ADR — these are the spine everything
  else needs and they keep getting queued behind harness increments.
- Access AI invocation service (82) + audit (83) — the platform that lets *any* AI value
  ship safely. Earlier than more Bernie-proposal contract polish.
- §15A security P1s (RLS, audit_log) — currently deferred; they should be Band 7 not
  "someday," because they get exponentially harder after multi-tenant data grows.

**Pull later / defer:**
- All broad-trove work (Band 8) — correctly gated; keep it there and stop feeding it micro-
  sprints. One tiny approved prototype is enough until a consumer exists.
- Wiley/Cochrane knowledge base (Band 6) — high integration/legal cost, no dependency
  from the core booking loop. Spike only.
- Online booking / PWA / kiosk (Band 9) — genuinely valuable but strictly downstream of a
  working internal spine; do not start external clients before the internal one is real.

**Candidates to kill or freeze:**
- **Freeze net-new interpretation-harness guardrail sprints.** The harness is done enough.
  Its next legitimate change is *becoming a runtime consumer* (Band 4), not gaining
  another self-validation layer. If a new guardrail is proposed, require it to name the
  runtime consumer it protects; if there is none, decline.
- **Kill "cleanup as programme."** Keep it as bounded hygiene (§6).
- **Consider retiring the retired Word-diary artifacts** (`create_diary_file.py`) if they
  are causing any confusion — low priority, but reduces surface.

---

## 8. Recommended Collaboration Pattern (Ariadne + Fable + workers)

**Overall:** Ariadne stays orchestrator/integrator. Fable is reserved for *band-boundary
architecture gates and unusually hard reviews only* — Claude Fable access is expected only
through **2026-07-07**, so spend it on the highest-leverage checkpoints (the API Spine ADR
synthesis, the Band 2 live-provider gate review, and the Band 8 pre-trove architecture
review) rather than routine sprints.

**Per band:**
- **Band 1 (spine/ADR):** full three-way plan-gated loop — Claude (domain/GraphQL schema),
  Antigravity/Gemini (frontend + agent-UX + API-consumption dissent), DeepSeek Flash or
  Codex worker (security/audit/deploy). Ariadne synthesises the ADR. Use Fable once here
  for the synthesis review if access remains.
- **Band 2 (Access AI runtime):** Claude/DeepSeek implement bounded backend lanes behind
  fake providers; Antigravity for independent domain-policy critique; keep every lane
  fake-provider until the dedicated live-gate sprint. Ariadne runs all verification.
- **Bands 3–5 (mutation workbench, copilot, messaging/setup):** default worker mix per
  the 2026-07-05 protocol — check Claude health first; if capped, replace with a second
  DeepSeek Flash lane rather than pausing; Antigravity for test/fixture/UX and dissent.
  Narrow file ownership, plan gate, submit, Ariadne-verify.
- **Bands 6+ (knowledge base, security, trove):** reserve an independent adversarial review
  lane by default (H63-style brief) for anything touching providers, PHI, or a boundary
  change. Trove work (Band 8) requires the H22 gate review as a distinct reviewed artifact
  before any implementation lane opens.

**Cost posture:** DeepSeek Flash for cheap bounded implementation/review; Claude for real
implementation while quota is healthy; Antigravity for independent critique + UX + test
design; Codex subagents when OpenAI credit is flowing; Fable only at the three named
architecture gates. Keep the "explore once, crystallise into a harness, run free" rule for
all UI review so the model stays out of deterministic loops.

**Anti-pattern to guard against in collaboration:** do not let the multi-agent plan-gate
ritual itself become another form of comfortable meta-work. For genuinely small,
tightly-coupled guardrail/hygiene increments, single-track Ariadne is correct (per the
2026-07-07 alert); reserve the three-way loop for separable, judgment-heavy, architecture-
or safety-facing sprints — which is exactly what Bands 1–2 are.

---

## 9. Files Changed & Verification

**Files changed:**
- `orchestration/agent_inbox/codex/review-claude-fable-100-sprint-strategy-map.md` (new,
  this artifact).

No production code, tests, scripts, app, frontend, database, or provider files were
touched. No raw/ignored `local_data` or historical diary material was read. No blocked
gate was opened.

**Verification:**
- `git diff --check` — result recorded below.

```
$ git diff --check   ->   exit 0 (no whitespace or conflict-marker errors)
```
