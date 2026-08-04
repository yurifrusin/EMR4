# Threat-model delta: model-required Bureau Gate-zero shared contract

Date: 2026-08-04

Status: architecture/schema prototype; provider-free and non-executing

Parent:
`docs/security/emr4-model-required-bureaus-gate-minus-one-threat-model-delta.md`

## Scope change

Gate −1 selected deterministic information-flow confinement and a fresh
one-shot brokered cell per Bureau attempt. Gate zero converts those selections
into one closed, versioned cross-Bureau contract. It does not implement a cell,
broker, provider adapter, product read, command or actuator.

## Assets

- domain and practice-scoped context truth;
- per-field provenance, integrity, readers, freshness and authority ceilings;
- provider admission, request and response identity;
- proofreader admission and denial evidence;
- human or dual-review evidence;
- backend-owned command and readback evidence;
- cell generation, one-use token, quota, teardown and residue evidence; and
- the distinction between provider-free, occupied-model and live-product
  evidence labels.

## Trust boundaries

1. backend source wrapper to labelled context;
2. orchestrator to broker-owned immutable attempt policy;
3. broker to fresh untrusted cognitive cell;
4. hostile response bytes to deterministic parser and proofreader;
5. admitted candidate to backend authority service;
6. authority decision to a separately authorised command handler;
7. handler transaction to deterministic readback; and
8. every field to every release, display, audit or command-argument sink.

The model, cognitive cell and returned bytes are hostile. The broker is trusted
for bounded transport but has no product or command authority. Human review is
authority evidence only when independently authenticated and bound by backend
policy; it is not evidence that model-controlled bytes are safe.

## Threats and frozen controls

### Label omission or laundering

A transform may drop a low-integrity source, widen readers, refresh stale data
or raise an authority ceiling.

Controls: schemas require labels on every field; joins are monotone; transforms
cannot raise a dimension; endorsement and declassification are distinct,
field-specific, named-policy operations; every sink re-evaluates the complete
label and context hash; failure yields a typed denial receipt.

### Cross-Bureau or cross-practice confusion

Shared primitives may be mistaken for shared context, policy or authority.

Controls: domain, practice scope, authorization decision and context hash are
mandatory on envelopes; closed domain-specific candidate kinds reject unknown
or crossing values; principals, identities, memory, policy and commands remain
domain-scoped; no model field can rewrite these bindings.

### Stale or superseded context

A validly shaped candidate may refer to expired truth or an earlier attempt.

Controls: observation and expiry are mandatory per frame and field; earliest
expiry wins; stale input contaminates a join; attempt, context hash and current
authorization must match at every admission; supersession releases nothing.

### Confidential information exits through a legitimate sink

A response may encode restricted data in explanation, denial, audit or command
arguments.

Controls: readers are intersected on join; every output field has its own label;
declassification is purpose/sink/expiry-bound and audited; denial receipts use
closed reason codes and sanitized identifiers; free-form raw provider bytes are
never persisted or released.

### Candidate bytes become host instructions

Strings may be interpreted as paths, URLs, callbacks, markup, templates,
commands, code, SQL or tool invocations.

Controls: canonical UTF-8 JSON, duplicate-key rejection, exact schemas,
byte/scalar limits and no trailing bytes; strings remain data; the cell has no
generic bridges; candidate and proof outputs cannot carry a command envelope.

### Broker or cell compromise reaches ambient authority

A cell may probe credentials, metadata, runtime sockets, filesystem, network or
other processes, or survive for a later attempt.

Controls: fresh identity and token per attempt; only one broker-owned request;
no shell/tool/path/URL/callback/filesystem/database/credential/metadata/ambient-
network/actuator bridge; exact quotas; kill on any failure; token revocation,
channel closure, process kill, ephemeral removal and typed zero-residue proof.

The schema is a design contract, not proof that an eventual isolation runtime
meets it. Runtime implementation will require separate evidence.

### Model output claims authority or human approval

A candidate may assert confirmation, dual review, risk acceptance or successful
execution.

Controls: separate principals and schemas; model output is candidate-only;
backend policy authenticates reviewers and constructs command evidence; only a
single-purpose handler plus deterministic readback can support success.

### Provider outage is hidden by a heuristic fallback

A named intelligence may appear available without a provider-model result.

Controls: explicit `PROVIDER_REQUIRED_UNAVAILABLE`, no equivalent candidate or
agentic completion claim, and no silent provider/model/heuristic substitution.
Independent deterministic safety and manual workflows retain only their own
existing identity and authority.

### Evidence-class inflation

Provider-free fixtures may be reported as an occupied model or live product
result.

Controls: closed evidence labels; Gate-zero acceptance permits only
`provider_free_gate_zero_architecture_contract`; occupied provider, live read,
write, actuator, deployment, production and release claims each require their
own exact evidence and authority.

## Deterministic Gate-zero evidence

- all closed Draft 2020-12 schemas validate their canonical examples;
- unknown properties, domains, candidate kinds, bridges and evidence labels
  fail closed;
- hostile duplicate-key and over-budget responses fail before proofreading;
- low-integrity, stale, unauthorized-reader and over-ceiling fields are denied
  at consequential sinks with typed receipts;
- provider outage releases no candidate or equivalent agentic success;
- quota expansion and incomplete teardown/residue evidence fail schema checks;
- cognitive, proof, authority and actuator principals remain distinct; and
- acceptance records zero provider, product-data, runtime, command/write,
  deployment, Pages and protected-ref side effects.

## Residual risks and closed successors

JSON schemas and deterministic simulations cannot prove operating-system,
container, broker, provider or cloud isolation. Provider/model/region/identity,
prompt data class, cost/licence, product reads, patient-facing Rayleen, Davida or
recovery writes, actuators, external updates, migrations, deployment,
production, release, protected refs/Pages and protected evidence remain closed.
Any new bridge or weaker isolation profile is a material security fork.
