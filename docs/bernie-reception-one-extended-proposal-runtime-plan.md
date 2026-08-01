# Reception One Extended Proposal Runtime Plan

Date: 2026-07-30

Owner: Yuri / GPT Sol

Status: `authorised_frozen`

## Objective

Extend the accepted default-off, authored-synthetic Reception One runtime from
appointment creation into four receptionist proposal families:

1. move or reschedule a selected appointment;
2. review cancellation of a selected appointment;
3. extend or contract a selected appointment's duration; and
4. assess a squeeze-in without moving or overbooking another appointment.

The result must use the existing closed typed language, deterministic
proofreader and backend-owned API Spine proposal services. It must end in one
bounded authored-synthetic Sydney Vertex demonstration of an extended family.
It grants no appointment confirmation or write authority.

## Frozen authority and data boundary

- Environment: local development, default off.
- Data: disposable, deliberately authored-synthetic only.
- API classification:
  `authenticated_default_off_command_style_read_and_proposal_runtime`.
- Authentication to the product runtime: existing authenticated appointment
  roles and exact practice scope.
- Planner: untrusted typed-plan candidate only.
- Proofreader: exact schema, catalogue, grounding, revision, effect and
  authority checks before atomic typed release.
- Backend: owns identifiers, selected-appointment truth, availability,
  conflicts, freshness, proposal evidence and all confirmation/write paths.
- Bureau: may display a reviewable proposal; it may not confirm or write.
- Closed: protected holdouts, historical Diary files, real/product-derived
  data, patient or health data, clinical fields, voice, Word wiring,
  production, deployment and release.

The request may carry a trusted selected appointment UUID from the Diary
surface. Practice scope is verified before any frame is built. The planner sees
only a request-scoped opaque appointment handle and minimal scheduling fields;
it never sees the UUID, ORM object, database session, authentication material,
notes, reason, contact data or clinical content.

## Runtime contract

Each family must pass this sequence:

`authenticated request -> minimal context desk -> typed plan -> deterministic
proofreader -> named non-mutating API Spine proposal adapter -> admitted Bureau
envelope`

Move and duration-change reuse `proposeAppointmentUpdate`. Cancellation review
reuses `proposeAppointmentDelete`. Squeeze-in is explicitly assessment-only,
has no API Spine mutation operation, never moves an existing appointment,
never overbooks and always requires human review.

The adapter must independently bind the opaque appointment handle to the
practice-scoped selected record, verify reviewed-plan hash and context
revision, refresh target availability where required, and retain signed
confirmation evidence only inside the trusted backend. No confirmation payload
or write-capable control is released to the model or this Bureau tranche.

## Tranches and gates

### A — authority and revision binding

Create the five-source rehydration and pre-plan receipts, this plan, a policy
manifest and threat delta. Add a new graph descendant and increment Continuity
and Compass together without revising any historical node. Revision binding
and rendered Compass validation must pass before an occupied call.

### B — kernel and API Spine adapters

Add selected-appointment binding, exact extended output types and fresh
proposal-adapter findings. Reject missing, cross-practice, stale, terminal,
conflicting, already-cancelled, unsafe or ungrounded requests. Preserve
GraphQL read-only and every confirmation/write route.

### C — Bureau typesetter

Render the four proposal families in the same compact/expanded Reception One
sheet with clear current/proposed values, warnings and a persistent
“nothing changed” boundary. Keep Return, Close, Escape and ordinary Diary
fallback. No active confirm control is added.

### D — provider-free proof

Prove every family against a disposable PostgreSQL-backed authored-synthetic
practice through the real local route and rendered browser. Require unchanged
appointment, event, command and audit hashes; provider calls zero; no
cross-practice access; and deterministic cleanup. Run adversarial schema,
handle, revision, expiry and authority cases plus API Spine and legacy-gate
regressions.

### E — occupied Sydney Vertex denouement

Only after A-D and all revision/report gates pass, run one primary occupied
call over an authored-synthetic runtime-shaped extended-family frame:

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- region: `australia-southeast1`;
- hostname: `australia-southeast1-aiplatform.googleapis.com`;
- work cell: credential-free, isolated, one-use;
- broker: sole ADC and regional data-plane holder;
- tools, grounding, retrieval, cache creation and provider fallback: disabled;
- global endpoint and API-key authentication: prohibited;
- application cost ceiling: USD 1;
- occupied-call ceiling: two, comprising one primary and at most one repaired
  retry solely for a deterministic request-contract defect.

Stop immediately after the first proofreader-admitted result. A repaired retry
requires a closed first ledger, bounded sanitized diagnosis, focused regression
test, complete provider-blocked rerun and a distinct ledger. No other retry or
substitution is authorised.

### F — audit and closeout

Consume every ledger; retain only allowlisted provider-error fields; record
request/schema/plan/review/release hashes rather than raw prompts, responses or
reasoning; clean all owned containers, networks, images, processes and
temporary roots; update Continuity and Compass together; render and validate
Compass; update AGENTS.md and the orchestration ledger; and state precisely
what the evidence does and does not prove.

## Acceptance

The tranche passes only when all four families:

- are exact-schema and proposal-only;
- are grounded in a current authored-synthetic selected appointment or
  availability frame;
- invoke only their named non-mutating adapter;
- release no raw UUID, credential, prompt, provider response, reasoning or
  confirmation evidence;
- preserve appointment, event, command and audit truth unchanged;
- fail closed for unknown operators, forged handles, stale frames,
  cross-practice records and unsupported compound effects; and
- render a clear human-review state in the Bureau.

The live result additionally requires the exact Sydney model, project,
identity, endpoint and keyless-ADC controls above. It proves configured and
observed locational routing plus bounded typed release—not Australian physical
or sovereign processing, real-data safety, production fitness or appointment
write safety.

## Stop conditions

Stop for Yuri if the work requires real/product-derived/patient/health/clinical
or historical data; appointment confirmation or write; Word or production
wiring; IAM, billing, project, API or credential changes; a different model,
provider, project, identity or region; global or regional fallback; API/static
keys; cost above USD 1; more than two calls; weakened isolation/audit/residency
assurance; or any authority beyond this plan.
