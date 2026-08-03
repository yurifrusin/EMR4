# Bernie and Davida shared-agent boundary

Date: 2026-08-03

Status: architecture-only frozen seam

## Boundary classification

`separate_probabilistic_domain_work_cells_over_shared_deterministic_api_spine`

Bernie is native to the operational Diary/reception vocabulary. Davida is
native to the Practice Administration vocabulary. Native means schema-literate
and domain-aligned, not database-connected or code-authoritative.

## Topology

```text
authenticated EMR4 surface
  -> deterministic consumer composition ----------------------+
  -> deterministic auth/context compiler                      |
       -> bounded Bernie or Davida probabilistic work cell     |
       -> agent-specific deterministic proofreader policy      |
  -> shared backend API Spine <--------------------------------+
       -> GraphQL named read/context frames
       -> REST/OpenAPI proposal and confirmation commands
       -> committed events followed by fresh reads
  -> PostgreSQL truth + append-only audit/outbox
```

The native Diary active-practitioner consumer follows the deterministic branch.
It is not an agent, receives no model interpretation and must not acquire an
agent-proofreader dependency. Its new composition reuses only the lower
application-session and authorized product-read bridge. It does not reuse the
Office consumer's one-use terminal reload/logout lifecycle, because the native
Diary is a long-lived browser surface. The existing bearer-authenticated
GraphQL path and REST fallback remain unchanged whenever the new application-
session feature is off.

Bernie and Davida must not inhabit one combined probabilistic container. A
combined service would couple capability manifests, runtime identity, release,
failure, scaling, cost and compromise blast radius. Future deployment may reuse
one base image or SDK, but each service needs its own immutable policy,
service identity, call budget, network allowlist and default-off feature gate.

The proofreader runs in the trusted deterministic boundary, not in the model's
authority domain. One proofreader engine may be reused, but Bernie and Davida
policies are separately constructed and must never be merged into a union of
allowed fields or actions.

## Authority classes

### Authoritative structured state

Practice, location, practitioner, room, waiting-area, opening-hours, role and
capability truth belongs to backend domain services and PostgreSQL. Reads are
practice/role/resource scoped and fresh. Changes require typed commands.

### Advisory institutional knowledge

Practice knowledge carries source, author, capture time, effective dates and
review status. It can explain practice customs or guide a human decision. It
cannot establish availability, roster truth, a hard policy block, confirmation
affordance or command authority. If a practice rule must become authoritative,
it needs a structured policy schema and an explicit administration command; it
must not be promoted merely because a model retrieved it.

### Session state

Agent clarification, selected candidate, dry-run proposal, context revision and
conversation state are bounded workflow state. They expire, can be superseded
and never become institutional truth by persistence or repetition.

## Active-practitioner ownership

Practitioner lifecycle truth has one backend owner. `Query.practice.practitioners`
is the named read projection for authorized internal consumers. Diary and
Office/Davida compositions may consume it with their own surface/session
partitions, but cannot broaden fields, infer write authority or retain a
competing authoritative directory.

A future Davida request such as “deactivate Dr Example from next month” follows
the administration command pattern. It must not edit the projection or table
directly. The command requires an expected aggregate version, effective date,
reason, actor/practice/resource authorization, a before/after dry-run,
confirmation evidence, idempotency, audit and backend revalidation. Bernie sees
the resulting lifecycle change only through a committed event followed by a
fresh read.

## Read pattern

1. The backend supplies minimal authenticated surface and capability frames.
2. The work cell emits a typed read-intent draft grounded only in supplied
   opaque references and allowed vocabulary.
3. The deterministic proofreader checks schema, scope, provenance, freshness,
   authority ceiling and grounding.
4. The backend authorizes and executes one named GraphQL/context read.
5. Any model-authored explanation is separately proofread and labelled model
   interpretation; returned database fields remain labelled live API facts.

The work cell cannot construct arbitrary GraphQL, choose fields, change practice
scope or receive a database session.

## Write pattern

1. Davida emits a non-mutating typed administration-intent draft.
2. The proofreader admits, rejects or requests bounded clarification.
3. The backend computes a fresh dry-run with explicit warnings, blocks and a
   before/after diff.
4. An authorized human reviews and confirms where the command's risk tier
   requires it.
5. A single-purpose REST/OpenAPI command receives `practice_id`, actor and role
   context, resource id, command type/version, correlation id, idempotency key,
   expected aggregate version or ETag, intent/proposal hash, effective time,
   reason, confirmation evidence and source surface.
6. The backend reauthorizes and revalidates current state, commits atomically,
   writes typed audit/idempotency/outbox evidence and returns a sanitized
   outcome.
7. Consumers reconcile through a fresh read.

The proofreader never substitutes for command authorization, domain invariants,
freshness checks or transactional audit.

Davida itself never emits a confirmation or write-authorized envelope. The
trusted backend constructs command authority from authenticated human
confirmation after the dry-run. Davida operation names use a closed enum rather
than an open action string.

## Shared kernel and separate domains

Shared deterministic components may include context-frame envelopes, typed
draft/proposal/result envelopes, proofreader mechanics, auth-context binding,
correlation/idempotency metadata, retry/supersession grammar, sanitized audit
envelopes, provider broker interfaces and evidence labelling.

Bernie-specific components remain Diary intent grammar, availability/proposal
semantics, reception session state and Diary narration. Davida-specific
components remain Practice Administration resource/lifecycle grammar,
onboarding/dry-run semantics, administrative risk policy and practice-operations
explanation.

Deterministic product consumers share only the authentication, authorization,
read-contract, audit and evidence-labelling substrate they actually need. They
must not be routed through an agent work cell merely to maximize code sharing.

Davida read frames must be backed by pure practice-scoped read services. The
existing active-practitioner directory service is the relevant precedent. A
future active-location projection needs the same no-side-effect posture;
current room and waiting-area GET routes that can normalize state and commit are
not eligible context sources until read/write behavior is separated.

Before any Practice Administration apply command exists, the backend resource
models need a uniform aggregate revision or ETag and the command plane needs a
closed operation vocabulary, idempotency retention, append-only audit/outbox
evidence and explicit human confirmation semantics.

Cross-domain collaboration uses typed committed events and fresh reads. There
is no direct agent-to-agent control channel and no shared mutable model memory.

## Gates preserved

This boundary opens no runtime container, provider call, memory/RAG/GraphRAG,
database credential, model-to-database write, GraphQL mutation, external
identity write, patient/clinical/document data, cloud/IAM change, deployment,
production, release or protected-ref authority.
