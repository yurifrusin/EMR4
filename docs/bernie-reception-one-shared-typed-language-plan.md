# Reception One Shared Typed Language Plan

## Decision and objective

Yuri authorised a fresh descendant of the closed Reception One Extended
Proposal Runtime so that the model agent and deterministic proofreader use one
shared typed language. Yuri also authorised the agent to emit a strictly
bounded natural-language `operator_note` beside the form-fed typed program for
audit and troubleshooting.

The objective is to remove the lossy free-form wire that caused the two
accepted HTTP 200 responses to fail before proofreading. The provider must emit
the exact `PlanProgram` envelope the proofreader validates. A trusted,
deterministic compiler may attach local metadata and expand integer codes into
the already accepted PlanDraft representation; it may not interpret prose or
invent a step.

This plan creates a new continuity descendant. It does not revise the consumed
ledgers or results of any historical node.

## Shared language

`reception.one.bureau.plan-program.v2` contains:

- `operator_note`: bounded, audit-only natural language;
- `goal_code`: one integer from the frozen goal table; and
- `steps`: an ordered array of coded operators and coded input sources.

Operator argument names are implicit in the frozen operator signature. External
input codes index an exact request-local binding table. Prior-step output codes
use `1000 + (step_index * 16) + output_index`. `-1` represents only an omitted
optional input. Step identifiers are generated deterministically after program
admission.

The deterministic proofreader validates the PlanProgram schema, code ranges,
operator arity, optional omissions, backward-only references, output indices,
semantic types, goal/terminal-operator agreement, source grounding, freshness,
supersession, proposal-only effects and the existing PlanDraft contract. The
compiled PlanDraft then reuses the accepted executor. No natural-language
parsing exists after provider egress.

## Bounded operator note

The note is analogous to a worker speaking beside a form-fed typewriter. It is
useful operational speech, but it is not the production form.

The note:

- is a required UTF-8 string of at most 320 bytes and one line;
- gives a concise generic account of the proposal or clarification;
- must explicitly preserve review/proposal status and say that no booking was
  changed;
- is independently proofread before retention;
- is never parsed into a goal, operator, argument, proposal or command;
- is never delivered as product output;
- cannot supply evidence missing from the typed program;
- cannot repair or override a rejected typed program; and
- may be retained verbatim only when it passes its own deterministic gate.

The note gate rejects credentials, authentication material, URLs, email
addresses, project/service-account/endpoint details, UUIDs, synthetic or
product identifiers, patient or practitioner names/aliases, prompt copying,
hidden-reasoning language, markup, control characters, command-shaped claims,
unsupported facts and overlength text. A rejected note is discarded; only its
hash and reason codes may be audited. A rejected note also prevents release of
the associated program. An admitted note may remain in the external audit when
the typed program later fails, because that is the bounded troubleshooting
purpose Yuri authorised.

This is explicit application-level retention of one schema-admitted field. It
does not enable Vertex request-response logging and does not retain a raw
provider response.

## Fixed authority

The local tranche is default-off, authored-synthetic and proposal-only. It may
cover the existing create, move, resize, cancellation-review, status-change,
squeeze-in-assessment and clarification goals using only the existing fourteen
operator definitions. Backend-owned identity, practice scope, appointment
truth, availability, conflicts, confirmation, writes, idempotency and audit
remain authoritative.

No real, product-derived, patient, health, clinical or historical data is
admitted. No appointment write, confirmation, product delivery, Word wiring,
voice, representative-staff session, production, deployment, release, commit,
push or protected-ref movement is authorised.

## Conditional occupied gate

After all repository-only, provider-blocked, real-isolation, Continuity,
Compass and rendered-Compass gates pass, the tranche may make one primary
authored-synthetic call and at most one deterministic request-contract repair
through exactly:

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- location: `australia-southeast1`; and
- hostname: `australia-southeast1-aiplatform.googleapis.com`.

The incremental application ceiling is USD 1 and the absolute call ceiling is
two. Stop after the first admitted result. No provider, model, project,
identity, credential, region, endpoint, data-class, isolation, proofreader,
audit, cost or residency substitution or fallback is allowed.

The broker alone may refresh existing impersonated ADC and call the exact
regional endpoint. The cell receives no credentials or cloud configuration.
Provider tools, function calling, grounding, retrieval, explicit cache
creation, global endpoints and automatic regional fallback remain disabled.

The former control posture must be freshly reverified before the call:
impersonated credential type, exact project/target/scope, non-interactive
refresh, Vertex API, billing entitlement, model entitlement, exact
prediction-only custom role and permission, Vertex Data Access audit logging,
disabled/absent request-response logging, disabled project cache, no
service-account key and no API-key path.

## Deterministic gates

1. Validate all new schemas and exact frozen tables.
2. Prove lossless PlanProgram-to-PlanDraft compilation for every supported
   goal.
3. Reject malformed codes, type mismatches, forward references, fabricated
   sources, note leakage and command-shaped notes.
4. Run focused tests, the accepted typed-plan suite, relevant API Spine tests,
   JSON/schema validation, Python compilation/static checks and
   `git diff --check`.
5. Run a credential-free real-isolation lifecycle proving that the occupied
   cell can communicate only with the one-use broker.
6. Increment Continuity and Compass together and validate their revision
   binding and rendered Compass report before any occupied call.
7. Run the read-only ADC/control preflight.
8. If every gate passes, consume one distinct ledger for the primary call.
9. A second ledger is eligible only for a deterministic request-contract
   repair after closing and auditing the first attempt, adding a focused
   regression and rerunning every provider-free gate.

## Acceptance

The tranche passes locally when the provider envelope is mechanically lossless,
the note is independently bounded, the existing proofreader/executor accepts
all positive fixtures and rejects every negative fixture, isolation and residue
checks pass, and no external state changed.

An occupied pass additionally requires HTTP 200, exact PlanProgram admission,
operator-note admission, existing semantic proofreader admission, atomic
release of typed proposal fields only, a consumed ledger, a valid external
hash chain and complete cleanup.

An occupied failure remains a complete, fail-closed result with no release,
fallback or unauthorised retry.
