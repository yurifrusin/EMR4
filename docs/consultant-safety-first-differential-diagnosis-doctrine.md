# Consultant safety-first differential-diagnosis doctrine

Date: 2026-08-04

Status: Yuri-approved clinical direction and future architecture input;
documentation only. Consultant architecture, runtime, provider, patient data,
clinical use, commands, deployment and release remain closed.

Decision owner: Yuri

## Purpose

Consultant should make careful diagnostic reasoning easier and less
time-consuming for a practitioner. Its primary objective is not to predict the
single statistically most likely diagnosis. It is to help the practitioner
recognise, investigate and safely disposition plausible diagnoses whose delay
or omission could cause serious preventable harm, while also avoiding harmful
or indiscriminate investigation.

The governing clinical doctrine is:

> Probability proposes; preventable harm prioritises; evidence discriminates;
> the practitioner decides.

This doctrine complements the EMR4 architectural doctrine:

> model-required cognition; deterministic authority.

Consultant is therefore a clinician-controlled diagnostic-safety assistant. It
does not become the diagnosing practitioner, an autonomous test-ordering agent,
or a source of clinical truth.

## Clinical origin and external alignment

Yuri attributes the originating practice principle to Dr Michael Shera: begin
by identifying the most critical patient-safety diagnosis that remains
reasonably possible, even when it is uncommon in the general population;
actively seek history, examination, test or specialist evidence that can
confirm it or make it sufficiently unlikely; then continue through the
remaining differential until the evidence supports a safe working conclusion.
This is a user-supplied account of Dr Shera's clinical approach, not an
independently verified biographical claim.

Yuri also recalls that Dr Shera ensured every GP practising at his medical
centre had licensed Cochrane Library access through a button in the original
EMR toolbar. The architectural lineage for Consultant is therefore not merely
"add retrieval": preserve universal clinician access to a trusted evidence
standard and evolve the old human-initiated library link into licensed,
source-grounded assistance inside the new EMR/Raisa workspace. This is likewise
user-supplied practice history, not an independently verified biographical or
commercial claim.

That principle is consistent with two established diagnostic-safety ideas:

- the Australian `restricted rule-out` approach considers both the common
  explanation and serious diagnoses that must be ruled out; and
- differential-support tools can improve consideration of important
  `must-not-miss` diagnoses.

It also requires an important safeguard. General practice commonly begins with
low pre-test probabilities. Testing every rare serious condition can produce
false positives, incidental findings, overdiagnosis, anxiety and harmful
investigation cascades. Consultant must support diagnostic stewardship: the
right evidence or test for this patient at the right time, with its limitations
and downstream obligations visible.

## Evidence hierarchy and licensed Cochrane centrality

The Cochrane Library is the selected **central general evidence-based pillar**
for Consultant. The intended first integration candidate is the licensed
**Wiley Agent Knowledge Base: Cochrane Library** offered through AWS
Marketplace. It exposes structured Cochrane evidence through an API for AI and
retrieval workflows, so it is a natural licensed successor to the original EMR
toolbar access. Consultant must not scrape Cochrane Library pages or treat an
ordinary human-reader subscription as permission for agentic use.

Central does not mean exclusive or sufficient for every question. Cochrane's
systematic reviews, protocols and clinical answers should anchor general
evidence synthesis where they apply. Australian guidelines and regulatory
sources, diagnostic-test evidence, drug and interaction references, local
pathways, specialty guidance, rare-disease references, primary studies and
current safety notices remain complementary layers. Absence of a relevant or
current Cochrane review is an evidence gap, not evidence that a condition,
association or intervention is absent.

The backend must preserve a provider-neutral, source-type-aware evidence
contract even though Cochrane is the preferred central corpus. Every retrieved
item needs source identity, title, version/date, evidence type, citation or DOI,
permitted excerpt, retrieval time, currency, licence and provenance metadata,
and any source-supplied certainty or risk-of-bias information. Consultant's
reasoning layer receives bounded evidence packets and cites them; the UI and
model prompt never call a corpus directly, and provider/model memory never
becomes the evidence store.

This direction authorises architecture and contract planning only. Subscribing
to a private offer or EULA, accepting cost, calling the AWS/Wiley API, sending
patient or product-derived context, caching or embedding licensed content,
choosing a region or retention policy, or making a regulatory or production
claim each remains subject to its exact licence, privacy, security, clinical-
safety and human-authority gate.

## Safety-weighted differential, not one ranking score

Consultant must not collapse a hypothesis into one opaque probability or
priority number. Each candidate needs independently visible dimensions:

- patient-specific plausibility, distinct from population prevalence;
- severity of the harm if the diagnosis is missed;
- time to material or irreversible harm;
- treatability or reversibility if recognised promptly;
- evidence for, evidence against and important evidence not yet obtained;
- whether the condition is actually excluded, merely less likely, or still
  unresolved;
- the safest useful next discriminator;
- the risks, limitations and expected information value of that discriminator;
- relevant specialist knowledge or escalation pathway; and
- the uncertainty and provenance attached to every contributing item.

A low-probability but plausible time-critical diagnosis must remain prominent
even when a common benign diagnosis is currently more likely. Conversely,
severity alone does not justify testing a diagnosis for which the
patient-specific evidence does not cross an appropriate clinical threshold.

No clinician-approved policy should hide these trade-offs inside a model-owned
composite score. If deterministic prioritisation is later used, its rules,
versions and clinical ownership must remain inspectable.

## Proposed diagnostic journey

### 1. Immediate safety screen

Surface current red flags, time-critical syndromes and escalation criteria
before routine synthesis. An emergency or urgent referral pathway interrupts
ordinary differential work; the model cannot lower the urgency established by
an approved deterministic rule or clinician decision.

### 2. Structured differential construction

Create a closed, reviewable candidate set that deliberately considers:

- plausible must-not-miss conditions;
- the diagnoses most strongly supported by current evidence;
- treatable or reversible alternatives;
- important mimics, medication effects and multiple simultaneous conditions;
  and
- an explicit insufficient-evidence or unresolved presentation state.

Consultant should be able to ask, in effect, `What else could this be?` and
`Which dangerous explanation have we not yet adequately considered?` without
presenting an exhaustive encyclopaedic list.

### 3. Evidence and discriminator planning

For each material candidate, distinguish:

- `FOR`: reliable evidence supporting it;
- `AGAINST`: reliable evidence opposing it;
- `UNKNOWN`: clinically important information not yet available;
- `DISCRIMINATOR`: the next history question, examination, observation, test,
  record retrieval or specialist input most likely to change management; and
- `ACTION_THRESHOLD`: what finding, absence, deterioration or elapsed time
  should trigger escalation, reassessment or safe de-prioritisation.

The preferred action is not automatically a test. It may be a focused history,
physical examination, review of an existing result, observation over time,
consultation with a specialist, or immediate transfer of care. Test sensitivity,
specificity, pre-test probability, contraindications, delay, invasiveness,
radiation, false-positive consequences and follow-up capacity all matter.

### 4. Iterative evidence update

New history, examination, results and specialist advice update a versioned
differential snapshot. They do not silently overwrite prior reasoning. The
system should preserve what changed, why a candidate moved, and which source
supplied the change.

Provisional disposition terms should remain conservative. Candidate examples
for later schema design are:

- `active_must_not_miss`;
- `active_probable`;
- `less_likely_not_excluded`;
- `excluded_by_clinician_accepted_criteria`;
- `clinician_confirmed_working_diagnosis`;
- `deferred_with_safety_net`; and
- `insufficient_evidence`.

The provider model may never emit an authoritative `ruled_out` or `confirmed`
state. A negative result does not exclude a diagnosis unless the applicable
clinician-approved pathway, the test's limitations and the patient context
support that conclusion.

### 5. Closure, follow-up and safety net

Diagnosis continues after the consultation. Consultant must keep visible:

- ordered but incomplete tests;
- results not yet reviewed or communicated;
- referrals not yet accepted, attended or reported;
- an expected clinical course and reassessment time;
- symptoms or changes that require earlier review; and
- the person or role responsible for every follow-up obligation.

No news is not evidence of a normal result. No diagnostic episode should appear
closed merely because the cognitive exchange ended.

## Longitudinal diagnostic memory: the Diagnostic Thread

Consultant should help preserve the memory track of a diagnostic problem across
time. The working architectural name is `DiagnosticThread`: a durable,
patient-scoped, backend-owned record connecting the past, present and expected
future of one clinical concern.

This is not provider-model memory, a conversation transcript, an embedding
store, RAG or GraphRAG. It is typed, versioned clinical workflow state. The
provider model may interpret and explain an authorised view of it; the model
cannot create its authority, rewrite its history, declare its obligations
fulfilled or close it.

The three temporal views are:

- **Past:** the original presentation, material history and examination,
  previous differential snapshots, tests and specialist opinions, clinician
  decisions, safety-net advice, amendments and an attributable account of why
  each hypothesis changed.
- **Present:** active must-not-miss and probable candidates, current working
  diagnosis, unresolved uncertainty, evidence already available, outstanding
  evidence, present risk state and responsible practitioner or team.
- **Future:** expected results, planned observations, referrals, review dates,
  reminder or recall obligations, deterioration triggers, escalation deadlines
  and the evidence required before the thread may be safely resolved.

The thread should survive encounters, documents and individual Consultant
sessions. A new result, correspondence item, referral report, appointment or
patient-reported change is a typed signal to perform a fresh authorised read
and consider a new immutable snapshot. An event is not authority to change the
differential or mark an obligation complete.

### Intersection with reminders and recalls

The diagnostic thread and the PMS reminder/recall system should meet at a
typed `FollowUpObligation`, not through private Consultant scheduling logic.
The obligation describes what clinical uncertainty must be revisited, by whom,
by when, why it matters, and what outcome would satisfy or escalate it. The
ordinary backend reminder/recall domain owns delivery, retries, appointment
linkage, acknowledgement and audit.

Important distinctions must remain visible:

- creating a reminder does not complete the clinical obligation;
- sending a recall does not prove that the patient received or acted on it;
- attendance does not prove that the intended result or diagnostic question
  was reviewed;
- a normal result does not automatically close a hypothesis when the test is
  insufficient to exclude it;
- an overdue or failed follow-up increases attention but does not let the model
  invent a diagnosis; and
- closing a thread requires an authorised practitioner decision with material
  obligations resolved, transferred or explicitly retained in a safety-net
  plan.

Potential lifecycle states for later clinical and schema design include
`open_assessment`, `awaiting_evidence`, `active_monitoring`,
`specialist_review_pending`, `working_diagnosis_established`,
`resolved_with_safety_net`, `closed_by_practitioner` and `reopened`. Exact
states, transition rules and reminder/recall ownership remain future clinical
architecture decisions.

This longitudinal design should reduce a common diagnostic failure mode: an
important concern is considered in one consultation but becomes detached from
its pending test, referral, review interval or later contradictory evidence.
Consultant's value is partly to keep that thread coherent and inexpensive for
the practitioner to resume.

## Clinician-facing projection

The principal view should not be a single ranked diagnosis list. A useful
projection is:

1. **Act now** — current red flags and urgent escalation.
2. **Must not miss** — serious plausible conditions not yet adequately
   excluded.
3. **Most likely** — hypotheses best supported by the present evidence.
4. **What would discriminate** — focused questions, examinations, tests,
   observation or specialist input.
5. **What would change our mind** — contradictory findings and explicit action
   thresholds.
6. **Outstanding evidence** — unclosed tests, reports, referrals and review
   responsibilities.
7. **Safety net** — deterioration, new symptoms and time limits for
   reassessment.

The interface should minimise work while making uncertainty and provenance
easy to inspect. It should pre-compose a focused evidence map and next-step
options, but the practitioner controls inclusion, correction, ordering,
referral, diagnosis and documentation.

## Four-plane Bureau and API Spine implications

These are design inputs, not frozen schemas.

### Mandatory cognitive plane

The accepted provider model:

- interprets the practitioner's natural-language question;
- proposes a closed differential and missing discriminators;
- conducts clarification dialogue;
- explains evidence, alternatives and residual uncertainty; and
- cannot read arbitrary records, order anything, write the clinical record or
  certify a diagnosis.

### Deterministic proof plane

Trusted code outside the cognitive cell:

- admits only a typed, bounded candidate;
- checks that every patient-specific assertion is grounded in an authorised,
  source-labelled context item;
- separates patient report, clinician observation, imported result, specialist
  opinion, licensed guidance, retrieved quotation and model inference;
- enforces freshness, patient/practice scope, candidate closure and citation
  integrity;
- applies clinician-owned rules for red flags, escalation and follow-up state;
- prevents absence of evidence from becoming fabricated reassurance; and
- releases an advisory snapshot, not a diagnosis or command.

Deterministic validation can prove shape, provenance, policy and calculations;
it cannot transform model output into clinical truth.

### Authority plane

The authenticated practitioner owns the clinical decision. Applicable policy
may additionally require urgent escalation, specialist involvement, shared
decision-making, or another authorised reviewer. Human confirmation authorises
the displayed clinical action; it does not upgrade the integrity of a poisoned,
stale or unsupported source.

### Execution and verification plane

Any future test request, referral, clinical-note insertion, prescribing action
or other mutation must use a single-purpose REST/OpenAPI command with current
patient and practice scope, practitioner identity, correlation, freshness,
idempotency where applicable, audit and deterministic readback. GraphQL and
context services remain scoped reads only. The cognitive cell never receives a
database, provider, command or actuator credential.

The Gate -1 labelled-capability envelope and one-shot brokered cell apply in
full. Patient text, documents, results, correspondence, guidelines and retrieved
literature can all contain direct or indirect prompt injection. Source labels
and permitted flows must survive every transformation; source quotations do
not become trusted instructions merely because they are exact.

## Candidate typed artifacts for a future architecture tranche

Names remain provisional until a separately authorised Consultant architecture
tranche freezes them:

- `ConsultantContextFrame` — clinician-selected, patient-scoped facts and
  declared omissions with source labels and freshness;
- `DifferentialCandidate` — one hypothesis with the separate safety and
  evidence dimensions above;
- `EvidenceItem` — source-linked `FOR`, `AGAINST` or `UNKNOWN` item;
- `DiscriminatorActionCandidate` — a non-authoritative question, examination,
  observation, test, retrieval or specialist-advice candidate with benefits,
  limitations and risks;
- `DifferentialSnapshot` — immutable versioned candidate set and explanation
  of changes;
- `DiagnosticThread` — durable patient-scoped link between presentations,
  differential snapshots, evidence, decisions and future obligations;
- `DiagnosticThreadEvent` — source-labelled observation that may cause a fresh
  authorised read and new snapshot but cannot itself change clinical state;
- `FollowUpObligation` — owner, due state, result/referral linkage and
  escalation rule, bridged to the existing reminder/recall domain without
  treating delivery as clinical completion; and
- `SafetyNetPlanCandidate` — practitioner-reviewed deterioration and
  reassessment advice.

No one artifact grants a clinical write. Model inference must remain visibly
different from patient, clinician, test, specialist and source evidence.

## Evaluation doctrine

Top-one diagnostic accuracy is insufficient. Future Consultant evaluation
should include:

- recall of clinically plausible must-not-miss diagnoses, stratified by
  severity and time to harm;
- dangerous false-reassurance and premature-closure rates;
- materially omitted hypotheses and discriminators;
- evidence-source and citation correctness;
- unsupported patient-specific assertions;
- appropriate insufficient-evidence and escalation behaviour;
- unnecessary-test and investigation-cascade burden;
- closed-loop result, referral and safety-net performance;
- continuity of diagnostic threads across encounters, handoffs and delayed
  evidence;
- overdue-obligation detection without excessive or duplicate alerting;
- clinician correction, override and residual-disagreement patterns;
- time saved and cognitive burden without alert fatigue;
- subgroup, accessibility and atypical-presentation performance; and
- security outcomes for prompt injection, retrieval poisoning, data leakage and
  attempted authority expansion.

Clinical adjudication is required. Agreement with another model is useful
development evidence but is not clinical acceptance.

## Research input: DeepLens Diagnosis Agent

Bayeshi and colleagues' 2026 DeepLens preprint is a useful demonstration that a
small model can improve markedly when placed inside a structured workflow. Its
five useful separations are fact extraction, patient-level retrieval,
constrained candidate generation, candidate-specific evidence triangulation
and final candidate selection.

Consultant should consider borrowing:

- separation of extraction from synthesis;
- different retrieval passes for general case context and
  candidate-discriminating evidence;
- a closed candidate set;
- explicit evidence for and against each candidate;
- exact source-span grounding;
- an insufficient-evidence outcome;
- stage-level observability and failure localisation; and
- ablation, latency and cost measurement.

Consultant should not copy:

- a top-one, single-gold-label objective as its safety objective;
- model-extracted facts becoming canonical patient truth;
- exact quotation being treated as sufficient evidence integrity;
- retrieval or pattern-library content entering without Gate -1 provenance and
  influence controls;
- comparison claims in which frontier baselines did not receive the same
  workflow; or
- model-judge accuracy as a substitute for clinician adjudication and
  prospective safety evidence.

DeepLens is therefore evidence for the value of a reasoning harness, not a
complete clinical-safety, authority or containment architecture.

## Decisions deliberately deferred

This note does not decide or authorise:

- Consultant's final intended-use statement or regulatory/TGA classification;
- the clinical safety owner, governance body or approved pathway authors;
- exact plausibility, escalation, exclusion or testing thresholds;
- a provider, model, region, identity, patient-data class, retention policy or
  cost;
- exact AWS/Wiley offer acceptance, licence rights, cost, API runtime, region,
  PHI/data handling, caching, embedding, retention, RAG or GraphRAG design;
- real patient/context access, a clinician study or a patient-facing surface;
- test, referral, prescribing, record-write or autonomous action authority;
- a runtime isolation profile beyond the accepted Gate -1 requirements; or
- deployment, production, release, protected integration or Pages.

Those decisions require their own evidence and authority gates. Selecting
Cochrane as Consultant's central general evidence pillar grants no provider,
licence, patient-data, clinical, implementation, deployment or production
authority; current Bureau development remains governed by its separate baton.

## References

- Yuri's account of Dr Michael Shera's differential-diagnosis practice
  principle, EMR4 architecture discussion, 2026-08-04. User-supplied oral
  history; no external biographical claim is made.
- Yuri's account of Dr Michael Shera providing every GP at his medical centre
  with licensed Cochrane Library access through the original EMR toolbar, and
  Yuri's selection of Cochrane as Consultant's central general evidence pillar,
  EMR4 architecture discussion, 2026-08-05. User-supplied oral history and
  product direction; no external biographical claim is made.
- AWS Marketplace. [Wiley Agent Knowledge Base: Cochrane
  Library](https://aws.amazon.com/marketplace/pp/prodview-rxkns32my7r7m),
  including the API-based delivery, private-offer licensing and entitlement-
  dependent full-text access described by the vendor listing.
- Wiley. [Building better healthcare AI with Cochrane
  Library](https://www.wiley.com/en-mx/insights/trending-stories/healthcare-ai-aws-cochrane/),
  2026, describing the licensed machine-readable evidence feed for AI
  workflows.
- Bayeshi M, Kocaman V, Naqvi MA, Gul Y, Talby D. [DeepLens Diagnosis Agent:
  Agentic Workflow Design Lets a Small Reasoning Model Compete with Frontier
  LLMs](https://arxiv.org/abs/2607.22555), arXiv:2607.22555v1, 2026.
- Royal Australian College of General Practitioners. [Starting off in general
  practice — consultation skill tips for new GP
  registrars](https://www.racgp.org.au/afp/2014/september/starting-off-in-general-practice-consultation-skil),
  including restricted rule-out, diagnostic pause and safety-netting.
- Agency for Healthcare Research and Quality. [Diagnostic Safety Research
  Priorities and
  Opportunities](https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-pediatric-safety-4.html),
  including evidence on differential-support tools and must-not-miss diagnoses.
- World Health Organization. [World Patient Safety Day 2024: Improving
  diagnosis for patient
  safety](https://www.who.int/news-room/events/detail/2024/09/17/default-calendar/world-patient-safety-day-2024-improving-diagnosis-for-patient-safety),
  framing diagnosis as correct, timely and communicated care.
- World Health Organization. [Technical Series on Safer Primary Care:
  Diagnostic
  errors](https://www.who.int/publications-detail-redirect/9789241511636), 2016.
- Royal Australian College of General Practitioners. [We live in testing times
  — teaching rational test ordering in general
  practice](https://www.racgp.org.au/afp/2014/may/we-live-in-testing-times/),
  covering pre-test probability, false positives, investigation cascades,
  overdiagnosis and test harms.
- Agency for Healthcare Research and Quality. [Diagnostic Stewardship as a
  Model To Improve the Quality and Safety of
  Diagnosis](https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-dx-stewardship2.html),
  including test selection, interpretation, reporting and follow-up.
- Agency for Healthcare Research and Quality. [Current State of Diagnostic
  Safety: Results](https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-current-state3.html),
  including ordering, interpretation, result management, communication and
  closed-loop follow-up as distinct testing-process safety concerns.
- National Academies of Sciences, Engineering, and Medicine. [Improving
  Diagnosis in Health
  Care](https://nap.nationalacademies.org/catalog/21794/improving-diagnosis-in-health-care),
  2015, including diagnostic teamwork, patient participation, health-IT support
  and learning from diagnostic errors.

External sources inform this future design direction. They do not validate an
EMR4 implementation or replace formal clinical, regulatory, privacy, security
or legal review.
