# EMR4 API Spine Programme

This programme records the root-to-branch API design direction for EMR4. It is
not an implementation sprint by itself. It is the architectural spine that future
sprints should test against.

## Core Decision

EMR4 should use a mixed API architecture:

- **GraphQL** for the connected read/context graph: patients, practitioners,
  diary state, proposals, evidence, audit, permissions, agent context, and
  knowledge-base citations.
- **Command-style REST/OpenAPI mutations** for irreversible or high-risk writes:
  confirm booking, cancel appointment, finalise consultation, send messages,
  submit billing, or call external regulated services.
- **Async/event contracts** for integrations such as Caller ID, SMS, pathology,
  Medicare Online, OPV/PVM/IHI, billing, and external knowledge-base refresh.
- **YAML manifests** as the declarative operating layer around the API, not the
  API itself.

The practical rule is simple: GraphQL can ask rich questions about EMR4's state;
commands perform explicit, auditable actions.

## YAML Manifest Layer

YAML remains important because it is readable by humans, deterministic scripts,
and future copilot agents. It should describe desired state, policy, setup, and
capability. It must not become a shadow programming language.

Primary YAML uses:

- dev/prod environment manifests with project IDs, regions, feature flags,
  provider choices, service-account targets, and allowed test identities;
- setup paths for GCP/IAM/Access AI/practice onboarding, including dry-run,
  execute, verify, rollback, and helper-link metadata;
- capability manifests for agents and roles;
- practice onboarding manifests for practitioners, rooms, locations, appointment
  types, waiting areas, billing preferences, and opening hours;
- security and permission profiles for receptionist, practice manager, GP,
  nurse, admin, agent, and external integration principals;
- agent context contracts defining which frames each agent may read or receive;
- integration placeholders where research is required before implementation.

Complex branching, safety enforcement, and clinical or billing logic belong in
typed code and database-backed policy, with YAML supplying validated inputs.

## Context Frame Rule

Agents should receive typed, minimal, relevant context frames. The goal is not
to fill a frontier model's context window just because it is available. The goal
is to give each agent the same precise operational context that a strong human
user would bring to the task.

For *bernie*, the preferred booking-context sequence is:

1. Interpret enough of the request to identify likely patient, practitioner,
   date/time, and task intent.
2. Recognise the patient where the evidence is strong enough for reception
   workflow.
3. Fetch deterministic patient-specific booking context, such as 60 days back
   and 2 years forward for that patient only.
4. Fetch deterministic availability context for the requested date/time window.
5. Let the LLM use those typed frames to explain, warn, or ask follow-up
   questions, while all availability and writes remain API-enforced.

The patient-specific booking context frame should include recent bookings,
future bookings, and derived signals such as usual practitioner or an existing
future follow-up. It should not include the entire practice diary.

This creates a reusable design practice for other agents:

- *consultant* should receive a curated patient-context and cited
  knowledge-source frame, not a raw database dump.
- *davida* should receive setup/profile/capability frames, not unrestricted
  admin state.
- Library agents should receive their real source-specific search results and
  citations, not unbounded clinical context.

YAML may define which context frames an agent is allowed to request or receive.
The runtime API still owns authorization, freshness, audit, and schema
validation.

## Agent Naming And Role Rule

Agentic names should be lower-case and italicised in project documentation:
*bernie*, *scribe*, *davida*, and *consultant*.

Source-specific clinical library agents should be named after their real
knowledge base rather than given human-like names, for example
*cochrane-library* or *racgp-guidelines*.

The exception is *consultant*: the doctor's synthesis copilot. *consultant*
should coordinate clinical-library agents and patient-context frames, but must
remain a doctor-reviewed advice surface rather than an autonomous diagnosing or
prescribing actor.

## Agent Capability Charters

YAML charters should define what each agent may read, ask, propose, and never do.
For example:

```yaml
agent: consultant
knowledge_sources:
  - cochrane-library
  - racgp-guidelines
  - patient-history
  - pathology-results
  - imaging-results
context_frames:
  allowed:
    - current_consult_note
    - active_problems
    - medications
    - allergies
    - recent_results
    - relevant_past_history
output_contract:
  must_include:
    - differential_diagnoses
    - red_flags
    - supporting_evidence
    - uncertainty
    - suggested_next_questions
    - suggested_tests
    - citations
  must_not_include:
    - final_diagnosis_without_doctor_review
    - autonomous_prescribing
safety:
  require_doctor_confirmation: true
```

The runtime API must still enforce authorization, audit, PHI rules, and
doctor/staff confirmation. YAML describes the charter; code enforces it.

## Security Principles

Security is part of the API spine, not an afterthought:

- every authenticated human, agent, and integration is a principal with scoped
  capabilities;
- every write has an explicit command, actor, confirmer where applicable,
  idempotency key, and audit event;
- agents do not bypass normal API permissions;
- dev/prod behaviour changes through environment and manifest values, not forked
  code paths;
- external integrations start as placeholders with research status until their
  real API, legal, billing, and privacy implications are understood.

## Sprint Map

### Sprint 98 - *bernie* Booking Loop Integrity

Stabilise the current receptionist flow before the architecture programme
absorbs it:

- resolved practitioner names must not surface as missing raw IDs;
- staff can choose a different proposed time after reaching confirm-ready state;
- confirm booking either succeeds through the supported proposal token path or
  fails with a precise, test-covered contract reason.

### Sprint 99 - API Root-To-Branch Plan Review

Plan-gated multi-agent architecture review:

- Claude: GraphQL/domain schema boundaries and object graph.
- Antigravity/Gemini: frontend, agent UX, and API consumption model.
- Codex worker: security, permissions, audit, dev/prod mode, and deployment
  posture.

### Sprint 100 - API Spine ADR

Ariadne synthesises the accepted plans into a canonical architecture decision
record covering GraphQL, OpenAPI command mutations, async integrations, YAML
manifest layer, agent charters, and security model.

### Sprint 101 - Schema Prototype

Add non-invasive schema artifacts and validation:

- GraphQL SDL draft;
- OpenAPI command surface draft;
- YAML manifest schema examples;
- placeholder integration branches for Medicare/OPV/PVM/IHI, Caller ID, SMS,
  pathology, billing, Cochrane/Wiley, RACGP, and other library agents.

### Sprint 102 - API Steward Skill

Create a permanent API steward skill/subagent profile that advises Ariadne on
API consistency, schema drift, authorization, and manifest design during future
implementation sprints.
