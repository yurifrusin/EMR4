# Bernie Current Strategic Transition Review

Date: 2026-07-18

Status: strategic recommendation accepted by Yuri on 2026-07-18; Stage 1
authorized for acceptance planning only; no implementation authority has moved

## Executive conclusion

Bernie is further along as a product than the recent evaluation sequence makes
obvious, but materially less proven than the perfect certification and
synthetic scores can suggest.

The repository contains a real development-only supervised-booking vertical:
deterministic instruction interpretation, clarification and safety policy,
backend patient/practitioner context and slot search, proposal staging, signed
confirmation evidence, backend revalidation, idempotent appointment creation,
audit records, an authoritative confirmation receipt, and a substantial Diary
review/confirmation experience. Bernie does not receive write authority; the
authenticated receptionist and backend remain the authorizing parties.

What has not been established is an operational Bernie product. The strongest
language results are deterministic and synthetic. Most Diary acceptance is
route-intercepted or development-harness evidence. Bernie session state is
process-local rather than durable. The live interpreter is default-disabled.
There is no production provider decision, no real receptionist field evidence,
no production privacy/residency approval, and no production security or release
case.

The provider sequence has now become disproportionately detailed relative to
the remaining product evidence gap. T3R2-T3R7 produced useful methodology,
feasibility, governance, transport, and fail-closed evidence. T3R7 did not
establish provider reliability, variance, production suitability, or product
integration. Another provider call or retry would refine a secondary unknown
while the primary product loop remains unproven outside controlled harnesses.

**Recommendation:** pause provider experimentation and close the current
provider lane without retry. Do not start another holdout, synthetic corpus, or
provider comparison. Subject to a fresh Yuri authorization, the immediate next
stage should be a narrow, provider-free, synthetic-data-only, non-intercepted
local demonstration of the existing supervised booking loop through the real
Diary, FastAPI backend, and development PostgreSQL database. That stage should
prove the product boundary, not reopen language research.

This is a recommendation only. This review does not update the Current Baton,
authorize the stage, change product code, enable a provider, perform a cloud
mutation, create an appointment, deploy anything, or move write authority.

## Rehydration and evidence boundary

The review was rehydrated from `AGENTS.md` at Git commit
`8c5f1cd24826e620670e3250074d19db637f353e`. At review start, `HEAD`, local
`master`, local `handoff/current`, `origin/master`, and
`origin/handoff/current` all resolved to that commit and the integration
worktree was clean. The fresh Ariadne receipt is
[`bernie-current-strategic-transition-review-receipt.json`](../orchestration/agent_inbox/codex/bernie-current-strategic-transition-review-receipt.json).
Its runtime state explicitly names the five mandatory sources:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

The review used the active plans, accepted aggregate evidence, source code,
current API Spine artifacts, focused closeouts, and the two indexed topic
ledgers. It did not inspect or enumerate protected holdouts, access the blocked
appointment-call corpus, transmit any data, make a provider call, or mutate a
cloud or product surface. Previous certification and provider results are
treated as immutable evidence.

The main evidence anchors are:

- [`implementation_plan.md`](../implementation_plan.md) and the current
  [`AGENTS.md`](../AGENTS.md);
- the [post-certification transition review](bernie-post-certification-transition-review.md),
  [LC4V10 closeout](bernie-lc4v10-fresh-certification-closeout.md), and
  [LC4V10 Sol acceptance](../orchestration/agent_inbox/codex/lc4v10-sol-acceptance.md);
- the [Silver v2 anchor contract](bernie-synthetic-silver-v2-anchor-contract.md),
  [closeout](bernie-synthetic-silver-v2-closeout.md), and
  [Sol acceptance](../orchestration/agent_inbox/codex/synthetic-silver-v2-sol-acceptance.md);
- the T3R1, T3R4, T3R5, T3R6, and T3R7 closeouts and Sol acceptances named in
  `AGENTS.md`;
- the [Access AI design](../orchestration/access_ai_api_design.md),
  [API Spine ADR](../orchestration/api_spine_adr.md),
  [API Spine programme](../orchestration/api_spine_programme.md), and
  [Bernie release gates](../orchestration/bernie_release_gates.md);
- the [language-evaluation ledger](handover-ledgers/bernie-language-evaluation.md)
  and [product/API/security ledger](handover-ledgers/product-platform-api-and-security.md);
- current backend, Diary, Access AI, API Spine, and focused test evidence.

Four safe, offline readiness checks were rerun during this review. They confirm
that the live provider is disabled, no provider call occurred, provider/runtime
gates remain blocked, and the T3 external-call gate remains blocked. A focused
serial test run covering API Spine artifacts, Access AI, supervised booking,
create confirmation, and accessible confirmation passed 74/74 tests. These
checks do not elevate development evidence into production evidence.

## North-star product purpose

Bernie is primarily an internal assistant for medical reception staff. The
expected input is comparatively predictable operational language with
occasional noise, shorthand, corrections, omissions, and ambiguity. Bernie's
job is to:

1. interpret the staff instruction;
2. identify what is known, assumed, missing, or contradictory;
3. ask for clarification when identity, time, action, or policy is unsafe;
4. request only the bounded backend context required for the task;
5. prepare one or more safe appointment proposals; and
6. explain the proposal and its unresolved constraints to the receptionist.

The backend—not Bernie and not a provider model—owns patient and practitioner
identity, availability, collision detection, practice policy, freshness,
confirmation, appointment writes, idempotency, and audit. A receptionist's
explicit authenticated confirmation authorizes a command; the backend then
revalidates and either commits or refuses it.

Bernie is not principally a simulated patient-facing medical receptionist.
Patient dialogue, clinical advice, autonomous booking, and voice-agent behavior
are not prerequisites for the current MVP and should not distort the critical
path.

## Current-state map

The labels below are deliberately strict:

- **Implemented** means present in current product code, not released or
  production-ready.
- **Evaluated only** means demonstrated in a harness or bounded experiment but
  not established as an operational product capability.
- **Designed only** means a durable contract or architecture exists without a
  complete Bernie runtime path.
- **Blocked** means an explicit authority or readiness gate is closed.
- **Not started** means no meaningful product evidence was found.

| Product layer | State | What exists | Material limitation |
|---|---|---|---|
| Deterministic language interpretation | **Implemented; evaluated only for quality** | A default-disabled/fake/live interpreter boundary, deterministic parsing and normalization, typed outcomes, and a booking-instruction route | LC4V10 certifies a frozen deterministic contract, not naturally occurring staff language or an operational route |
| Clarification, safety, policy, and replay | **Implemented; strongly evaluated** | Typed clarification/refusal/proposal behavior, correction and reversal handling, replay checks, no-write defaults, and backend-owned confirmation | Perfect synthetic scores do not establish real-world ambiguity frequency, usability, or clinical workflow safety |
| Bernie session/state coordination | **Implemented, development-only** | Server-owned state/revision semantics, PHI-minimised events, stale-state and idempotency checks, and UI state transitions | The session store is explicitly in-memory and is lost on process restart; multi-worker and durable recovery are unproven |
| Synthetic evidence | **Evaluated only; complete and sealed** | Silver v2 has 96 coherent anchors and 192/192 complete candidates over two observations, with 384/384 safety and zero variance | It is authored development evidence, not prevalence, field quality, or production evidence; no v3 is authorized |
| Live-provider feasibility | **Evaluated only; current lane blocked** | T3R4 multi-system observations, T3R5 regional feasibility, T3R6 residency policy, and T3R7 Sydney transport/control evidence | No provider is selected; reliability, repeat variance, exact-version stability, production privacy, and runtime behavior are unproven |
| Access AI/provider abstraction | **Partly implemented; production blocked** | Typed capability registry, entitlements, provider injection, bounded audit events, persisted audit metadata, and cost estimates; Bernie's optional live interpreter goes through this choke point | Static registry/configuration, production adapter operations, residency enforcement, service objectives, and provider governance are incomplete; the default remains disabled |
| Backend booking proposal | **Implemented, development-only** | Patient/practitioner context, slot search, duplicate detection, candidate freshness, proposal staging, and a supervised-booking route | The primary Bernie vertical is appointment creation; broader action coverage in the language harness is not equivalent to broader product execution |
| Backend confirmation and write | **Implemented, development-only** | Signed evidence, authenticated staff confirmation, backend revalidation, idempotency, appointment creation, audit, and `appointment.confirmation_receipt.v1` | It has not been accepted as a non-intercepted end-to-end Bernie MVP or hardened for production concurrency and recovery |
| Diary receptionist experience | **Implemented; mainly harness-accepted** | Instruction entry, transcript/session state, clarification, candidates, proposed preview, choose-another-time, duplicate recovery, explicit confirm, blocked/error recovery, and accessible confirmation receipt | Earlier sprints record Yuri live checks, but most reproducible evidence is route-intercepted Playwright/static review; the current head has no single cohesive acceptance-grade browser/backend/database proof |
| API Spine contracts | **Designed and partly implemented** | GraphQL read schemas, REST/OpenAPI command contracts, YAML capability/permission manifests, async event contracts, and artifact tests; adjacent practitioner-directory read work exists | Bernie still uses a mixed existing REST/service path; the full read/context graph, async/audit spine, and production conformance are not complete |
| Audit, security, and privacy | **Partly implemented; production blocked** | Booking audit evidence, Access AI audit rows, metadata minimization, idempotency, signed confirmation, PyJWT hardening, SCA/CodeQL/Bandit/leakage controls, and protected integration | PostgreSQL RLS, comprehensive append-only audit coverage, JWT storage hardening, field-level encryption, retention operations, and production assurance remain open |
| Residency, deployment, and production operations | **Blocked / not started for Bernie** | Synthetic-only regional policies and limited provider transport evidence | No Australian production/PII provider approval, operational deployment, monitoring/SLO, rollback, support, or limited production pilot exists |
| Real receptionist field evidence | **Not started** | Prior Yuri reviews and synthetic scenario UX evidence | No representative receptionist cohort, naturally occurring instruction sample, measured task completion, error rate, or trust/usability study exists |

## What has actually been achieved

### 1. A bounded deterministic interpretation capability

LC4V10 is a valid `certification_pass`: all 576 observations passed every
frozen language, policy, replay, safety, runtime, and variance dimension. That
is meaningful. It establishes that the current deterministic interpreter can
reliably implement its specified contract across the certified population and
that the evaluation process can remain sealed and fail-closed.

The result should be retained as a component-quality claim. It should not be
described as certification of Bernie, the Diary, the backend, a provider, or an
EMR deployment.

### 2. A coherent synthetic receptionist-instruction corpus

Silver v2 supplies useful ordinary-development evidence: 96 coherent anchors,
two noisy receptionist-to-Bernie candidates per anchor, complete policy/replay
coherence, 192/192 product-complete results over two observations, 384/384
safety, and zero variance. Independent review reproduced the result without
protected access.

This is a high-quality regression asset. It is not evidence about real
receptionist language distributions, workload, accents, practice conventions,
or error costs. It should remain frozen and useful, not expanded merely because
the provider lane has paused.

### 3. A real development booking-control chain

The current backend and Diary are not only design documents. The product code
contains:

- a booking-instruction boundary with disabled, deterministic fake, and
  optional live modes;
- bounded patient/practitioner context and availability search;
- typed candidate and proposal freshness evidence;
- exact-duplicate and overlap handling before slot confirmation;
- explicit receptionist confirmation;
- signed evidence bound to user, practice, surface, session revision, patient,
  practitioner, slot, and proposal;
- backend revalidation before write;
- idempotent replay behavior;
- appointment and audit persistence; and
- an accessible, typed confirmation receipt consumed by the Diary.

That architecture matches the north star: the model or parser proposes, the
staff member authorizes, and the backend decides whether the action is still
valid.

### 4. Useful provider-control and governance evidence

The T3 sequence established several nontrivial controls: tool-free evaluation,
synthetic-only payload boundaries, hard call and cost ceilings, no automatic
retry, safe normalization, data-minimized artifacts, regional endpoint
selection, keyless IAM, audit configuration, and terminal fail-closed behavior.
Those controls are reusable if a provider-dependent product stage is later
authorized.

### 5. A partially real Access AI choke point

Access AI exists as product code, not only an ADR. It provides typed capability
and method checks, entitlement decisions, provider injection, allowed/blocked/
failed audit events, metadata minimization, persisted audit rows, and cost
estimates. Bernie's optional live interpreter invokes the `admin.booking.interpret`
capability through this service.

The abstraction is nevertheless incomplete as a production platform. It does
not remove the need for exact provider/location controls, runtime health and
rollback, retention operations, production identity and policy, service-level
evidence, or an approved PII path.

## What has been demonstrated only in evaluation harnesses

The following evidence is useful but must remain scoped:

- LC4V10 demonstrates the deterministic language/policy/replay contract.
- Silver v2 demonstrates coherence and robustness on authored synthetic
  receptionist instructions.
- T3R1's perfect echo run demonstrates projection, runner, scorer, and
  no-action plumbing, not model quality.
- T3R4 demonstrates bounded successful outputs from three systems under a
  pragmatic methodology. It cannot rank or select a production provider.
- T3R7 demonstrates a small number of usable Sydney Vertex outputs and the
  evaluator's terminal stop. It does not establish provider reliability.
- Route-intercepted Playwright and fake-provider tests demonstrate UI and API
  contract behavior under controlled responses. They do not prove the current
  browser, backend, database, authentication, and Diary work together without
  interception.
- API Spine artifact tests demonstrate contract consistency and parser-level
  validity. They do not demonstrate a complete runtime spine.

## What remains unimplemented or unproven

The largest missing capability is not another parser rule or provider sample.
It is a durable, observed product loop.

Entirely unproven or materially incomplete areas include:

- a current, reproducible, acceptance-grade end-to-end Bernie booking proof
  through the Diary, FastAPI application, PostgreSQL database, and authenticated
  staff confirmation path. Earlier sprint live checks remain useful but do not
  bind the whole current head into one durable product gate;
- durable Bernie session/event persistence across restart, multiple workers,
  and failure recovery;
- real receptionist usability, correction behavior, trust calibration, and
  naturally occurring instruction coverage;
- operational monitoring, latency budgets, support/rollback procedures, and
  service objectives;
- production tenancy isolation and RLS, comprehensive append-only audit,
  token-storage hardening, field-level encryption, and verified retention;
- an approved Australian production/PII provider, exact model/version policy,
  or provider lifecycle plan;
- privacy, security, residency, clinical-safety, deployment, and release
  approval for a limited practice pilot; and
- patient-facing, voice/headset, autonomous delegation, memory/RAG/GraphRAG,
  and broad multi-action execution. These last items are not needed for the
  immediate MVP and should remain deferred.

## Layer-by-layer strategic assessment

### Language interpretation

The deterministic layer is the strongest completed component. It now needs to
be consumed as a stable dependency, not repeatedly re-certified. The remaining
question is whether its current supported grammar is sufficient for a useful
receptionist workflow. That question requires product observation, not another
synthetic score.

### Clarification and safety

The architecture correctly separates extraction uncertainty, policy
clarification, proposal state, and backend authority. Clarification,
correction, whole-action withdrawal, stale evidence, conflict, duplicate, and
idempotency paths have strong test and synthetic evidence. The missing evidence
is human: whether receptionists understand why Bernie paused, can recover
quickly, and do not mistake a proposal for a booking.

### Synthetic evidence

The synthetic programme has accomplished its current purpose. Silver v2 is a
valuable regression corpus and LC4V10 is a valuable sealed component
certification. More synthetic volume would now have sharply diminishing value
and risks optimizing the programme around its own authored distributions.

### Provider feasibility and reliability

Feasibility has been demonstrated in a narrow sense: several external systems
can produce safe, often correct structured responses, and Vertex can be invoked
through a tightly controlled regional synthetic pilot. Reliability has not
been demonstrated. The evidence is too small, incomplete, version-ambiguous,
and detached from the product runtime to support a provider decision.

That gap does not currently block a deterministic MVP demonstration. It should
therefore be paused rather than filled speculatively.

### Access AI/provider abstraction

The conceptual boundary is sound and parts are implemented. Access AI should
remain the only future provider choke point. However, it must not become an
architecture programme in search of a current provider use case. Its next
material expansion should follow evidence that the deterministic product loop
needs a provider, not precede the product loop.

### Backend proposal and confirmation workflow

This is the most under-recognized product asset. There is already an explicit
proposal-to-confirm command path with backend checks, signed evidence,
idempotency, audit, and an authoritative receipt. It is aligned with the API
Spine principle that reads and proposals do not confer command authority.

The immediate weakness is operational continuity. Bernie session state is an
in-memory stand-in, while confirmation and appointment data are persisted. A
restart or multi-worker deployment can therefore break the conversational
evidence chain even though the appointment write path itself is durable. That
is acceptable as an explicitly bounded local demonstration limitation, but not
for a practice pilot.

### Diary and receptionist experience

The Diary implements the important product states: instruction, understood or
clarify, candidate search, provisional preview, choose another time, duplicate
recovery, confirming, blocked recovery, and confirmed receipt. Accessibility
work also ensures that booking legitimacy does not depend on visually
inspecting the diary.

The outstanding question is no longer whether these controls can be rendered.
It is whether the whole workflow is fast, understandable, and useful to a real
receptionist when the backend, authentication, state, and database are all
real. Earlier Yuri live checks are positive continuity evidence, but current
route-intercepted regression evidence cannot answer that question by itself.

### Audit, security, privacy, residency, and production readiness

The programme has strong delivery-security controls and meaningful local audit
and evidence primitives. It is not production-ready. Tenant isolation, audit
completeness and immutability, secret/token handling, field encryption,
retention, operational access, incident response, Australian PII residency,
provider contracting, deployment, monitoring, and support all require explicit
work and review.

These are not reasons to avoid a synthetic local MVP proof. They are reasons to
keep that proof clearly separated from a production or clinical-pilot claim.

## Critical-path assessment of T3R2-T3R7

T3R2-T3R4 were reasonably on the critical path when the unresolved question
was whether an external model evaluation could be conducted safely and whether
candidate systems showed any useful structured behavior. T3R3's tool-free
preflight and T3R4's bounded pragmatic comparison answered those questions.

T3R5 provided a genuine strategic finding: there was no suitable long-lived
current Gemini successor available in Sydney under the examined conditions.
T3R6 then made a defensible policy distinction between future US-located,
deliberately synthetic development and Australian-gated production/PII.

T3R7 provided a tightly controlled Sydney transport pilot and proved that the
runner stops on the first consumed normalized-response failure. That is useful
control-plane evidence. But by T3R5-T3R7 the work had become provider-centric
and piecemeal relative to product progress. Multiple rounds refined model
availability, regional policy, IAM, cost, and transport while the existing
Diary-to-backend product loop still lacked one current non-intercepted
acceptance demonstration and durable session state.

The correct conclusion is not that T3R2-T3R7 were wasted. Their evidence should
be preserved. The conclusion is that the provider lane has reached its current
decision value and is no longer Bernie's next critical path.

## What T3R7 genuinely proved

T3R7 proved that, for its exact frozen setup:

- the project could invoke the `gemini-2.5-flash` alias through the Sydney
  Vertex endpoint with keyless IAM and a narrow custom permission;
- deliberately synthetic Silver v2 instructions could be transmitted without
  product, patient, practice, historical-diary, external-corpus, or protected
  data;
- provider tools were disabled, request/response logging was not enabled, Data
  Access audit logging was enabled, and calls were paced and cost-capped;
- ten responses normalized successfully, all ten were safe, and nine were
  perfect against the frozen scorer; and
- the eleventh call's parse/schema failure consumed the observation and caused
  an immediate no-retry, no-further-call stop.

T3R7 cannot support claims about:

- a provider completion or failure rate;
- repeat variance, because no repeat pair completed;
- broad language quality or real receptionist robustness;
- exact backend model revision stability;
- production provider ranking or selection;
- PII privacy, Australian production residency, or contractual suitability;
- product runtime, latency, user experience, backend context, appointment
  safety, or write behavior;
- the exact cause of the eleventh failure, because raw text was intentionally
  not retained; or
- authoritative total billing, because the failed call lacked usage metadata.

The failure is not a reason to retry. It is evidence that schema failure occurs
and that the control worked. A retry would require a new experimental question,
new frozen rules, and new authority; none is currently justified.

## Provider recommendation

**Pause all provider experimentation now.** Treat T3R7 as the terminal evidence
for the current provider lane and retain the 37 unused calls as unused, not as
latent authority.

The existing evidence is sufficient for the present strategic decision:
external models can sometimes produce useful normalized Bernie frames, and the
evaluation boundary can fail closed. It is not sufficient for production
selection—but production provider selection is not the next blocking decision.

Provider work should resume only when all of the following are true:

1. a provider-free product vertical has been demonstrated and its remaining
   language limitation is observed rather than assumed;
2. the exact provider-dependent capability and success measure are frozen;
3. the product context contract and normalized response schema are stable;
4. Yuri separately approves the model, location, data class, prompt, call
   count, cost, retry semantics, diagnostics, and retention;
5. non-content schema diagnostics are sufficient to distinguish transport,
   parse, schema, policy, and product failures without retaining raw data; and
6. the experiment still excludes production/PII unless a later Australian
   production review expressly authorizes it.

## Largest remaining risks and unknowns

1. **Harness-to-product gap.** Perfect deterministic and synthetic results may
   not survive naturally occurring receptionist language and workflow pressure.
2. **No cohesive current end-to-end proof.** The components and earlier live
   checks exist, but there is no single reproducible acceptance record binding
   the current head's non-intercepted browser/backend/database booking loop.
3. **Session durability.** Process-local Bernie state can disappear on restart
   and is unsuitable for multi-worker or recoverable practice operation.
4. **Identity and context safety.** Patient/practitioner matching, freshness,
   duplicate detection, and availability are safety-critical when exercised on
   realistic data and concurrency, even though the contracts are tested.
5. **Receptionist mental model.** Staff may misread “understood,” a proposed
   diary card, or provider-generated text as a completed action.
6. **Production security.** RLS, comprehensive audit immutability, token
   storage, field encryption, retention, privileged operations, and incident
   response remain open.
7. **Evidence representativeness.** Silver v2 is coherent by construction and
   cannot reveal real frequency, workflow, or organizational-language gaps.
8. **Provider instability.** Model aliases, schemas, availability, latency,
   quotas, pricing, and regional offerings can change independently of EMR4.
9. **Contract and gate drift.** Historical readiness artifacts sometimes refer
   to “route/database wiring” as blocked for a particular interpretation
   harness while development product routes and writes already exist. Future
   decisions must name the exact surface instead of treating all “runtime” as
   one gate.
10. **Scope dilution.** Patient-facing simulation, corpus hunting, provider
    scoreboards, voice, memory, and broad API programmes can consume effort
    without proving the receptionist booking loop.

## Work that should stop, remain sealed, or be deferred

### Stop

- T3R7 retry or continuation;
- provider comparison rounds without a product-derived question;
- further holdout versions, deterministic certification, or synthetic corpus
  refinement for their own sake;
- attempts to turn aggregate evaluation scores into whole-product claims;
- piecemeal provider/gate documents that do not advance an approved product
  stage; and
- treating provider availability as the prerequisite for a Bernie MVP demo.

### Remain sealed

- protected holdouts v1-v10 and all consumed certification versions;
- LC4V10 as immutable aggregate certification evidence;
- Silver v2 as frozen ordinary-development evidence;
- T3R1-T3R7 reports and consumed observations;
- the provenance-blocked appointment-call corpus; and
- historical diary/PHI material outside its exact approved payloads.

### Defer

- any new provider call, provider runtime, raw-response retention, or provider
  tool path;
- production/PII use and Australian provider/residency selection until the
  fresh review boundary no earlier than 2027;
- memory/RAG/GraphRAG and broad historical-diary context;
- external dialogue corpus acquisition or admission;
- patient-facing, clinical-advice, voice/headset, or autonomous receptionist
  behavior;
- broad GraphQL, async, or API Spine expansion not required by the selected
  vertical; and
- broader Bernie mutation types until booking creation is demonstrated and its
  authority model is accepted end to end.

## Shortest credible path to a demonstrable, safe Bernie MVP

The shortest credible demonstration is deliberately narrower than a production
pilot:

> In a local synthetic development practice, an authenticated receptionist
> types a booking instruction into the real Diary. The existing deterministic
> interpreter either clarifies or requests bounded backend context. The backend
> resolves identity, searches availability, and returns safe candidates. The
> receptionist selects a proposal and explicitly confirms it. The backend
> revalidates, performs exactly one appointment write, records audit evidence,
> returns an authoritative receipt, and the Diary visibly reloads the committed
> appointment. Ambiguity, duplicate, stale, conflict, and replay cases fail
> safely.

This proves Bernie's product purpose without depending on a live provider,
real patient data, a new corpus, a new holdout, or a production deployment.

## Recommended product-level sequence

No more than five stages are needed. Each stage is a fresh decision boundary;
none is authorized by this document.

### Stage 1 — Provider-free vertical MVP proof **(recommended immediate stage)**

**Purpose:** establish that the existing Diary, deterministic interpreter,
backend context/proposal services, explicit confirmation command, PostgreSQL
write, audit, receipt, and reload work together without route interception.

**Evidence required:**

- a real local FastAPI/PostgreSQL/Diary run using a deliberately synthetic dev
  practice and authenticated staff account;
- the ordinary create-booking path plus ambiguous identity, no slot, exact
  duplicate, stale proposal/conflict, and idempotent replay cases;
- proof that no appointment exists before staff confirmation and exactly one
  exists after a successful confirmation;
- correlated session, proposal, confirmation, appointment, receipt, and audit
  evidence without raw sensitive prompt logging;
- a current accessibility and receptionist-comprehension review; and
- a closeout that distinguishes non-intercepted evidence from route-intercepted
  regression tests.

**Acceptance boundary:** one booking-create vertical is demonstrably safe in a
local synthetic development environment. The receptionist remains the
authorizing principal; backend identity, availability, freshness, conflict,
policy, idempotency, write, and audit checks are authoritative. Any unsafe or
unclear path blocks without a write.

**Exclusions:** live providers, cloud mutations, production, PII, deployment,
new corpus/holdout work, broad API redesign, database migration, durable session
implementation, additional mutation types, and autonomous confirmation.

**User decisions:** Yuri must explicitly authorize the local synthetic
end-to-end stage, including synthetic development appointment writes and only
the narrowly necessary product/test corrections if the existing vertical does
not pass. If Yuri wants a zero-write demonstration instead, the acceptance
claim must be reduced to proposal-only.

### Stage 2 — Durable authority, recovery, and security foundation

**Purpose:** make the accepted vertical safe under restart, concurrency,
multi-worker operation, practice isolation, and audit/recovery requirements.

**Evidence required:** transactional durable Bernie session/event storage;
restart and concurrent-revision tests; cross-practice RLS/authorization tests;
complete append-only command/audit correlation; idempotency across failure and
retry; secrets/JWT and field-protection review; and a focused threat-model
delta.

**Acceptance boundary:** a booking session and confirmation can be recovered
and audited without cross-practice access or duplicate writes under realistic
failure and concurrency conditions.

**Exclusions:** provider enablement, production deployment, PII pilot,
additional Bernie actions, and broad platform migrations unrelated to the
vertical.

**User decisions:** authorize the necessary database migration and structural
security tranche; decide the required audit retention and recovery period.

### Stage 3 — Receptionist workflow validation

**Purpose:** determine whether the narrow product actually saves time and is
understood by intended staff.

**Evidence required:** approved synthetic task sessions with representative
reception staff; time-to-correct-booking, clarification/recovery rate,
proposal-versus-confirmation comprehension, accessibility, trust, and observed
language-gap findings; no real patient data unless separately authorized.

**Acceptance boundary:** staff can complete the supported booking tasks safely,
understand every blocked/clarification state, and do not mistake a proposal for
a confirmed booking. Product changes must respond to observed workflow issues,
not synthetic-score gaps.

**Exclusions:** live provider comparison, patient-facing use, production
release, clinical advice, voice, and autonomous delegation.

**User decisions:** authorize participants and observation protocol; decide
acceptable task-time and recovery thresholds and whether any naturally
occurring but de-identified language may be collected under a reviewed policy.

### Stage 4 — Controlled Access AI integration, only if needed

**Purpose:** address language limitations that Stage 3 demonstrates cannot be
handled acceptably by the deterministic layer.

**Evidence required:** a product-derived frozen capability, fake-adapter tests,
stable normalized schema, complete fail-closed/audit/cost/kill-switch evidence,
and—only under a separate approval—a small synthetic live-provider experiment
with exact model, location, budget, retention, retry, and diagnostic rules.

**Acceptance boundary:** provider output may improve interpretation or
explanation but cannot assert identity, availability, confirmation, or write
authority. Provider failure must return to safe clarification or deterministic
operation without an appointment mutation.

**Exclusions:** production/PII, raw-response retention, provider tools,
automatic retry, model-to-database writes, and provider-selection claims beyond
the approved evidence.

**User decisions:** decide whether observed Stage 3 gaps justify a provider at
all; if so, separately approve the provider experiment and its cost/privacy
boundary.

### Stage 5 — Australian production readiness and limited supervised pilot

**Purpose:** decide whether the demonstrated product can safely enter a tightly
bounded real practice environment.

**Evidence required:** fresh Australian privacy/residency and provider review;
security and clinical-safety assessment; RLS/audit/encryption/retention proof;
deployment, monitoring, rollback, incident response, support, training, and
data-processing controls; and a limited-pilot protocol with stop criteria.

**Acceptance boundary:** a named practice, user cohort, task scope, data class,
provider/runtime configuration, supervision model, monitoring plan, and expiry
are explicitly approved. Backend authority and receptionist confirmation remain
non-negotiable.

**Exclusions:** broad production release, autonomous operation, patient-facing
use, clinical advice, and expansion beyond the approved practice/task cohort.

**User decisions:** accept material privacy, residency, security, cost,
deployment, support, and clinical-governance obligations. Production/PII
provider review remains no earlier than the standing 2027 boundary unless Yuri
explicitly changes that policy under a fresh review.

## Immediate recommendation and alternatives

### Recommended: Stage 1, provider-free vertical proof

This gives the highest information value per unit of work. It tests whether the
substantial existing implementation coheres into a useful product, preserves
all provider and protected-evidence boundaries, and creates a concrete basis
for deciding whether durability, UX, language, or provider work is actually
next.

### Alternative A: proposal-only non-writing demonstration

This is safer and faster because it stops before appointment creation. It can
validate instruction, clarification, context, candidate, and UX behavior, but
it cannot prove Bernie's defining authority boundary: explicit staff
confirmation followed by exactly one backend-authoritative write and receipt.

### Alternative B: durable security/session foundation first

This reduces technical risk before any end-to-end demonstration and may be the
right choice if Yuri's next goal is a practice pilot rather than an MVP demo.
The trade-off is that substantial database/security work may be undertaken
before confirming that receptionists find the current workflow valuable.

### Alternative C: receptionist discovery before integration

Synthetic, zero-write workflow observation can test language and mental models
quickly. It reduces the risk of polishing the wrong UX, but still leaves the
backend confirmation chain unproven and may be distorted by a prototype that
does not behave like the real system.

### Not recommended: resume provider experimentation

Another provider sample could refine a failure-rate or schema-diagnostic
question, but neither question currently blocks a deterministic product proof.
It would continue the recent imbalance between provider detail and product
progress.

## Earlier assumptions or recommendations that should be corrected

1. **“Bernie is mainly a simulated receptionist.”** Incorrect. Bernie is an
   assistant to reception staff. Patient-facing simulation is evidence tooling,
   not the product north star.
2. **“LC4V10 certifies Bernie.”** Too broad. It certifies a bounded
   deterministic language/policy/replay component and its frozen evaluation
   contract.
3. **“Silver v2 proves real-world robustness.”** Incorrect. It proves coherent
   authored synthetic robustness and is a regression asset.
4. **“T3R1's perfect result is model-quality evidence.”** Incorrect. It is
   projection/runner/scorer plumbing evidence only.
5. **“T3R4 selected or nearly selected Gemini.”** Unsupported. The comparison
   was incomplete and pragmatic, repeat coverage was very small, and no
   independent veto was obtained.
6. **“T3R7 should be retried because most calls were unused.”** Incorrect. The
   eleventh observation was consumed, the terminal stop was the accepted
   control behavior, and unused calls carry no authority.
7. **“A live provider is required before Bernie can be demonstrated.”**
   Incorrect. The deterministic path can prove the product authority and UX
   loop first.
8. **“The backend proposal/confirmation workflow is only designed.”**
   Incorrect. A substantial development implementation exists, including real
   appointment write, revalidation, idempotency, audit, and receipt behavior.
9. **“The API Spine is either complete or entirely paper.”** Both are
   inaccurate. Durable contracts and selected runtime pieces exist, but the
   complete Bernie read/context/event spine and production conformance do not.
10. **“Access AI migration means provider abstraction is production-ready.”**
    Incorrect. Bernie's optional interpreter uses the implemented choke point,
    but provider operations, exact model/location policy, runtime reliability,
    and production governance remain blocked.
11. **“More synthetic or external dialogue data is the natural next step.”**
    No. The existing evidence is sufficient to expose the current gap: product
    integration and staff workflow evidence.
12. **“All runtime/API/database work is unopened.”** Too coarse. Existing
    development routes, database writes, session endpoints, and audit paths are
    real. What remains closed is new authority, production use, provider
    runtime, durable expansion, deployment, and release. Future gate documents
    should name the exact surface to avoid this ambiguity.
13. **The post-certification sequence's emphasis on security, corpus, and
    provider work should continue automatically.** It should not. The completed
    security and evidence work remains valid, but the next strategic question is
    whether the existing components form a useful supervised receptionist
    product.

## Decision requested from Yuri

The single most important decision is whether to **pause/close the current
provider experimentation lane and authorize Stage 1: a local,
provider-disabled, synthetic-data-only, non-intercepted supervised booking
vertical through the existing Diary and backend, with no production, PII,
deployment, new corpus, or new holdout authority**.

Until Yuri makes that decision, the correct state is pause. No sprint should be
manufactured merely to preserve momentum.
