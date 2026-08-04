# EMR4 model-required Bureau Gate-zero shared contract

Date: 2026-08-04

Status: Gate-zero architecture candidate; provider-free and non-executing

Source boundary: `50dab5d66fc1401344fc47d7aa5ebd336b75e960`

## Decision

All named EMR4 intelligences use one versioned four-plane contract. A provider
model is mandatory for an eventual agentic product claim, but it remains an
untrusted candidate generator in a fresh one-attempt cognitive cell. Typed code
outside that cell owns proofreading, the backend owns authority, and a distinct
single-purpose handler owns any separately authorised effect and readback.

Gate zero freezes architecture and closed schema prototypes only. It performs
no provider call, product read or write, runtime wiring, deployment, release or
protected action.

The governing formula remains `model-required cognition; deterministic
authority`.

## Four planes and principals

1. **Cognitive plane — `cognitive_cell_generation`.** One approved model may
   receive exactly one minimized, authorized, labelled context envelope through
   the broker and may return exactly one bounded candidate byte stream. The
   model and cell have no command, credential, database, filesystem, shell,
   tool, URL, callback, metadata, ambient-network or actuator authority.
2. **Proof plane — `deterministic_proofreader`.** A strict hostile-byte parser
   and closed-schema validator ground every candidate field against current
   context, apply label/sink rules, freshness and supersession, and emit either
   one admitted candidate or one typed denial receipt. Neither output is an
   effect.
3. **Authority plane — `backend_authority_service`.** Current backend policy
   classifies the admitted candidate, actor, practice and target; binds any
   required confirmation or dual review; and either rejects it or constructs a
   backend-owned command envelope under a separately opened command contract.
   Candidate text is never authority evidence.
4. **Execution and verification plane — `single_purpose_command_handler`.** A
   separately authorised handler validates the backend-owned command, performs
   its bounded transaction, appends audit/outbox evidence and reads current
   truth back. Without that readback no success claim is released.

The broker is a transport principal, not a fifth authority plane. It owns the
provider request, immutable request policy, byte budgets and the only cell
channel. Cognitive, proof, authority and actuator principals remain distinct.

## Domain ownership

- **Bernie** owns prospective scheduling dialogue and appointment projection or
  proposal candidates. Appointment truth and commands remain backend-owned.
- **Rayleen** owns present-tense waiting-room dialogue and projection or
  arrival/status/movement proposal candidates. Patient-facing identity,
  product reads and every write remain closed.
- **Davida** owns institutional and practice-administration dialogue, advisory
  or administrative proposal candidates. She never confirms or administers her
  own proposal.
- **Controlled recovery/update intelligence** owns technical diagnosis,
  recovery-plan and update-proposal candidates. It receives no shell, SQL,
  cloud, IAM, migration, deployment or data-activation bridge.

Domain policies, context, memory, identities and authority never cross merely
because the Bureaus reuse schema and proofreader primitives.

## Label and capability algebra

Every context field, candidate field, transformation and sink decision carries
five dimensions:

- provenance source identifiers and transformation trace;
- integrity principals that actually endorse the value;
- confidentiality/readers permitted to observe it;
- observation, expiry and freshness state; and
- a maximum authority ceiling.

Join is monotone and conservative: provenance is unioned, integrity and reader
sets are intersected, the earliest expiry wins, any stale input makes the join
stale, and the lowest authority ceiling wins. Ordinary transformation cannot
add integrity, readers, freshness or authority.

Endorsement is named-principal, field-specific, evidence-bound and audited. It
does not erase provenance or raise confidentiality access. Declassification is
named-policy, field- and sink-specific, purpose-bound, expiring and audited. It
may narrow an explicitly authorised confidentiality restriction but cannot
endorse integrity, refresh stale data or raise an authority ceiling.

Every release and every security-relevant command argument is a sink. A sink
mediator evaluates the complete field label, current context hash, schema,
domain, practice, actor, freshness, endorsement/declassification evidence and
authority ceiling. Failure emits a closed typed denial receipt naming the field,
source labels and failed sink rule. Human confirmation does not relabel hidden
model influence and cannot cure a failed sink decision.

## Envelope conventions

The prototypes in
`orchestration/continuity/model-required-bureau-gate-zero/` are closed Draft
2020-12 schemas with no unknown properties:

- `labeled-context-frame` carries minimized backend facts and per-field labels;
- `typed-candidate` carries one unadmitted model candidate, the source context
  hash and per-field labels;
- `typed-denial-receipt` carries stable reason codes and sanitized evidence;
- `one-attempt-cell-manifest` freezes broker/cell identity, bridges and quotas;
  and
- `teardown-residue-receipt` proves kill, revocation and zero residual surface.

An admitted candidate is the same closed candidate payload plus deterministic
proof evidence. A future command envelope is a different backend-owned schema
and cannot be emitted by the cognitive or proof plane.

## Trusted sources and sinks

Only registered wrappers may originate source labels. Each wrapper binds source
type, practice/domain scope, authorization decision, observation time, schema
and content hash. Event payloads are hints only and require a fresh authorized
read before becoming context. Model output always begins with integrity
`untrusted_model` and candidate-only authority.

The closed sink registry distinguishes provider input, projection, proposal,
diagnosis, recovery plan, audit, human display, command argument and effect.
Provider input additionally requires an admitted provider/data/region/cost call
policy. Gate zero has no such admission, so its provider sink is structurally
specified but closed.

## One-attempt cell and broker contract

Every attempt receives a fresh cell generation, cell identity and one-use
broker token. The broker constructs one labelled input, owns one provider
request and accepts one candidate response. The cell sees only a once-readable
typed input and once-writable typed output. No generic bridge registry entry is
permitted.

The parser admits canonical UTF-8 JSON only, rejects duplicate keys, unknown
properties, invalid scalars, trailing bytes and over-budget payloads, and never
evaluates, interpolates or treats returned strings as paths, URLs, markup,
templates, commands or code.

The manifest fixes byte, time, CPU, memory, process and descriptor quotas.
Expiry, quota breach, parse failure, broker failure or supersession kills the
generation and releases nothing. Teardown revokes the token, closes channels,
kills processes and removes owned ephemeral storage. The residue receipt must
prove no live process, listener, mount, token, credential or temporary artifact
before the attempt can close.

## Provider admission and outage

There is no silent model, provider or heuristic fallback. Without an admitted
provider result, an agentic capability reports
`PROVIDER_REQUIRED_UNAVAILABLE`, releases no equivalent candidate and makes no
agentic completion claim. Deterministic safety automation, ordinary backend
validation and manual PMS workflows may continue under their own existing
authority; they must not impersonate the unavailable named intelligence.

Gate zero itself remains provider-free. A fresh independent source review may
occur only under its own applicable verifier authority and is evidence about
this contract, never an occupied product-model path.

## API Spine and future command envelope

GraphQL remains a named, practice-scoped read/context graph and cannot invoke a
provider, mutate state or carry a command. REST/OpenAPI owns every provider,
external or state-changing command. Events are committed hints that require a
fresh authorized read; manifests declare capability and policy inputs that
typed runtime code must enforce.

Any later backend-owned command envelope must name an exact command type,
practice scope, actor, correlation and idempotency keys, target and expected
revision, context/freshness binding, expiry, warnings, blocks, required risk
tier, confirmation or dual-review evidence, audit contract and deterministic
readback contract. The backend must reauthorize and revalidate immediately
before a write. The model, cell, broker and proofreader cannot construct that
envelope.

Any later provider invocation must use the Access AI command boundary and bind
capability, method, actor, practice, entitlement, context hash, data class,
provider, model, region, cost budget, correlation and audit policy. Raw prompts
or responses are not GraphQL fields and are not persisted or released by this
contract. Gate zero admits no such invocation.

## Human and dual-review expression

Risk is expressed as one of `observe_only`, `ordinary_confirmation`,
`manager_confirmation`, `dual_review`, `maintenance_release_authority` or
`forbidden`. The authority plane chooses from current policy; model output may
only propose a risk class. Required reviewers must be authorized, distinct
where separation of duties applies, current, scope-bound and expiry-bound.
Neither the model, cell, broker nor proofreader can satisfy a human review.

## Evidence labels and claim boundary

- `provider_free_component` proves only schemas, proofreaders, policies and
  failure semantics.
- `occupied_model_authored_synthetic` additionally proves one exact admitted
  provider/model/data/region/cost path.
- `live_product_read`, `live_product_write`, `live_actuator`, `deployment`,
  `production` and `release` each require their own exact evidence and authority.

This Gate-zero candidate may claim only
`provider_free_gate_zero_architecture_contract`. It grants no provider runtime,
product or patient data, command/write, actuator, migration, cloud/IAM,
deployment, production, release, protected-ref movement or Pages rebuild.
`docs/branding/` and protected evidence remain excluded.
