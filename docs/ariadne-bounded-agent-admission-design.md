# Ariadne Bounded Agent-Admission Design

Date: 2026-07-23

Status: provider-neutral, repository-local and non-executing

## Design statement

The work cell now has a design for an empty chair. The chair is the cognition
adapter slot; the locked form is the typed admission envelope; and the accepted
deterministic proofreader remains the only door out. Describing the chair does
not seat an agent in it.

The central rule is: **coarse cognition may receive a coherent bounded task,
but admission never grants authority and generation never bypasses proof.**

## Relationship to the accepted predecessors

The Bounded Cognitive Work Cell established coarse cognition with fine-grained
typed output authority. The Scripted Rehearsal established deterministic
control-plane transitions. The Real-Isolation Rehearsal established one exact
container posture around the unchanged tape. This design adds only the missing
contract between bounded context and a future cognition adapter.

It does not renew the consumed container run or reinterpret any predecessor as
model evidence.

## The admission envelope

A future attempt would be eligible to reach an adapter only after a pure
deterministic check of:

- exact work-cell, practice, principal, purpose and correlation;
- immutable policy revision and implementation/container generation;
- complete context digest, frame allowlist, source labels and freshness;
- model-independent input, output and attempt budgets;
- empty capability and secret sets;
- unexpired, non-cancelled and non-superseded attempt state;
- the exact five draft output ports; and
- mandatory proofreader-only egress.

In this tranche the envelope always retains `execution_enabled: false`. A
`design_valid` decision means only that the declaration is internally
consistent. It is not an admission ticket and cannot be consumed by a runtime.

## Control plane versus evidence plane

The control plane contains versioned codes: allowed context types, output
ports, budgets, closed capabilities, cancellation rules and proofreader route.
Its canonical digest is computed independently of user or evidence content.

The evidence plane contains the user's bounded request and supplied synthetic
facts. Request text can legitimately describe work, but it cannot rewrite the
control plane. Text that says `ignore policy`, invents approval, requests a
tool or names a different destination remains untrusted content.

The canonical adversarial case replaces the request text with an instruction
to bypass policy. Because the mutation touches only the evidence frame, the
control-plane digest and evaluated authority remain unchanged. This is a
structural proof; a later model-specific tranche must separately test whether a
chosen model follows the separation.

## Minimal context package

The canonical package uses only authored-synthetic opaque references. Each
frame has:

- one allowlisted semantic type;
- `authored_synthetic` sensitivity;
- an API Spine source label;
- exact purpose, practice, principal and correlation bindings;
- one context revision and freshness interval;
- a canonical byte count; and
- a payload whose allowed keys are fixed by frame type.

The adapter cannot fetch more. Unknown frames, mixed scopes, stale evidence,
secret-class data or an oversized package are admission-design rejections.
Context minimisation is therefore a deterministic construction obligation, not
a request to the future model.

## Budgets without a selected model

Frame count and canonical input bytes are meaningful before model selection.
So are maximum draft count, canonical output bytes and immutable attempt count.
Those are fixed now.

Tokens are model- and tokenizer-dependent. Recording a plausible-looking token
number now would create false precision and could become an accidental grant.
The token field is null with status
`unresolved_until_model_and_tokenizer_selected`. A later concrete topology must
set and test it while preserving the model-independent caps.

## Capability vacuum

The future adapter begins with no tools and no ambient access. Network,
filesystem, process spawn, database, product reads, product writes, event
feeds, mailboxes, secrets and commands are all false or empty. The request and
provider cannot manufacture a capability. A new capability is a policy and
authority change, not a generated-output feature.

## Topology catalogue, not topology selection

The admission core does not depend on where inference occurs. The design
catalogues three future choices:

| Candidate | Potential advantage | New authority or risk that must be decided |
|---|---|---|
| In-cell local | Can avoid network and provider secrets | Model/image provenance, weights inclusion or mount, licence, device access, memory and container generation |
| Host-brokered local | Keeps weights outside the cell | IPC/local network, broker identity, multiplexing, cancellation and host trust |
| Remote-provider broker | Operationally flexible | External network, identity/secrets, jurisdiction, processing/retention, cost and provider failure |

None is selected or configured. The least authority-widening architecture at
this stage is a transport-neutral contract with an explicit later decision,
not an unexamined commitment to whichever transport is easiest to call.

## Cancellation and supersession

An attempt binds exact policy, generation and context digests. Cancellation,
deadline expiry and supersession are terminal. A late result is rejected before
it can enter the proofreader. New facts require a new immutable attempt through
the already-accepted fresh-context lineage; old context is never patched into a
running attempt.

This rule matters even without a runtime because it prevents a future adapter
from defining its own cancellation semantics.

## Draft-only egress

The adapter may one day return only the five accepted draft frame types. It
cannot return a verified edge, command, human approval, authoritative identity,
authoritative availability, evaluated policy or control-plane instruction.

All drafts go to the accepted deterministic proofreader. A draft which is
grounded and safe may later reach downstream or an inert human gate through the
existing verdict mapping. A draft that asks to skip the proofreader is simply
an untrusted draft plus an egress-bypass rejection.

## Evidence and observability

The deterministic evidence contains only source hashes, case identifiers,
fixed decision/reason codes, aggregate counts and manifest hashes. The public
trace does not echo frame payloads, prompts, identifiers, exception text or
chain-of-thought.

No future runtime should log raw context or generation by default. If raw
material is ever needed, that is a separate privacy, retention and audit
decision.

## API Spine result

Boundary classification:
`provider_neutral_non_executing_generated_cognition_admission_design`.

Typed context remains non-authoritative; generated content remains
`model_interpretation`-class draft evidence. GraphQL is read-only and unused;
REST/OpenAPI is the command plane and unused. The design creates no Access AI
invocation or provider adapter and changes no API Spine artifact.

## What remains unproved

This design does not prove model instruction-following, interpretation quality,
tokenisation, inference isolation, model provenance, licence fitness, device
isolation, provider privacy, PHI minimisation, runtime cancellation, live
authorization, product reads, persistence, human-gate usability, backend
commands or production safety. Those require separate authority and evidence.
