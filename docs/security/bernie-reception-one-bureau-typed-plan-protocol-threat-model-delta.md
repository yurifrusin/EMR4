# Reception One Bureau Typed Plan Protocol - Threat Model Delta

Date: 2026-07-29

Scope: provider-free authored-synthetic typed planning, deterministic
proofreading and in-memory proposal dry run.

## Assets and authority

Protected assets remain outside the tranche: product and patient data,
credentials, provider access, database connections, command confirmation,
historical Diary material and protected holdouts.

The in-scope assets are the integrity of:

- the closed operator catalogue;
- typed plan and review contracts;
- supplied synthetic context;
- context revision and freshness;
- proofreader disposition;
- reviewed plan hash;
- executor effect ceiling; and
- evidence claims.

The planner is untrusted. The proofreader is the only egress gate. The executor
has no command, provider, network or database authority.

## Threats and controls

### Operator or tool invention

Threat: a planner invents an operator, REST path, SQL fragment, provider call,
shell command or confirmation step.

Controls:

- exact catalogue membership;
- exact lowercase operator schema;
- unknown and forbidden operator rejection;
- three closed effect classes; and
- no dynamic dispatch outside the fixed implementation table.

### Schema-shaped authority laundering

Threat: a typed-looking plan claims `confirmed_write`, adds a confirmation
field or names a stronger effect.

Controls:

- `effect_ceiling=proposal_only` is schema-constant;
- forbidden-surface inspection precedes admission;
- context authority fields are all exact false constants; and
- confirmation operation IDs are absent.

### Fabricated entity or Diary fact

Threat: the planner supplies a plausible patient, practitioner, appointment,
slot, status or policy not present in the supplied frame.

Controls:

- entity mentions bind to exact utterance spans and exactly one supplied
  candidate;
- semantic values are re-derived by `extract_semantics()`;
- context references are allowlisted;
- step outputs are typed and backward-only; and
- executor values are resolved again from the source frame.

### Type confusion and dataflow smuggling

Threat: a planner passes a patient reference where a practitioner, appointment
or policy is required, or uses a later step as hidden recursion.

Controls:

- exact per-operator signatures;
- declared input and output types;
- backward-only reference validation;
- unique step identifiers; and
- fixed maximum of twelve steps.

### Stale-plan release

Threat: a relevant Diary change occurs while a plan is being prepared and the
old plan reaches presentation or confirmation.

Controls:

- exact context-revision binding at review;
- timestamp freshness check;
- repeat context-revision and plan-hash checks at execution; and
- future watcher integration is limited to invalidation and fresh-read
  reconciliation, never authority.

### Semantic repair

Threat: the proofreader silently invents a missing duration, entity, slot,
policy or action.

Controls:

- repairs are limited to whitespace and canonical identifier casing;
- missing semantics route to clarification;
- signature defects require an immutable later attempt; and
- reviewed-plan hashes distinguish attempts.

### Infinite or manipulative revision dialogue

Threat: repeated planner/proofreader exchange consumes resources, widens scope
or launders a rejected request.

Controls:

- revision limit of two total attempts;
- diagnostics are allowlisted path/code pairs only;
- unknown authority, grounding and freshness failures reject rather than
  revise; and
- exhausted revision budget rejects.

### Squeeze-in policy escalation

Threat: a novel composition interprets “squeeze in” as authority to move
existing patients, overbook or create an appointment.

Controls:

- supplied policy requires `allow_move_existing=false`,
  `allow_overbook=false` and human review;
- the operator returns only supplied `squeeze_in_review` candidates;
- it has no API operation ID; and
- the result states no reservation and no write.

### Review or result substitution

Threat: an attacker pairs an admitted review with a changed plan or changed
context.

Controls:

- SHA-256 of canonical normalized plan in the review;
- exact hash verification before execution;
- exact context revision recheck; and
- execution rejects every non-admitted disposition.

### Evidence overclaim

Threat: repository-only synthetic results are described as live model,
product, database, residency or release evidence.

Controls:

- evidence mode is
  `authored_synthetic_provider_free_repository_contract`;
- provider/product boundary fields are explicit and machine-tested;
- current runtime/provider/trove readiness remains blocked; and
- closeout must enumerate unproved surfaces.

## Residual risks and future gates

The protocol has not yet been tested against adversarial live-model output,
real product context, concurrent event delivery or a real API adapter. Before
those surfaces open, a fresh threat-model delta must cover container and broker
isolation, prompt/context minimisation, Access AI entitlement, provider audit,
resource exhaustion, event concurrency, API authorization, idempotency,
confirmation binding and product-data privacy.
