# EMR4 model-required, deterministic-authority Bureau architecture

Date: 2026-08-04

Status: approved architecture direction; implementation and provider authority
remain closed

Decision owner: Yuri

## Decision

Every EMR4 capability presented as an intelligent conversational agent must use
an approved provider model in its cognitive loop. The model is mandatory for
natural-language interpretation, dialogue, ambiguity management, explanation
and candidate formation. It is never the source of product truth and never
owns authorization, confirmation, mutation, deployment or proof of success.

The governing formula is:

> model-required cognition; deterministic authority.

Provider-free tests remain necessary evidence for schemas, proofreaders,
policies, state machines, command handlers and failure behavior. They are not,
by themselves, sufficient evidence that a named intelligent product capability
works end to end. A future product-readiness claim for Bernie, Rayleen, Davida
or the controlled recovery/update intelligence must include its accepted model
path as well as its deterministic spine.

This decision does not authorize a provider, model, call, prompt, cost, data
class, credential, region, runtime, deployment or production use. Those remain
separate reviewed gates.

## Non-negotiable invariants

1. No admitted provider-model result means no agentic or natural-language task
   completion.
2. No current, authorized and source-labelled typed context means no model
   invocation.
3. No deterministic proofreader admission means no released projection,
   proposal, diagnosis or recovery plan.
4. No deterministic backend validation means no authoritative product result.
5. No applicable human, dual-human or policy authority means no protected
   action.
6. No deterministic post-action readback means no claim that an action or
   recovery succeeded.
7. A model may explain evidence but may not manufacture, replace or certify it.
8. Provider failure is explicit. There is no silent heuristic, provider or
   model fallback presented as equivalent intelligence.

## Four-plane Bureau structure

Every named intelligence uses the same separation:

### 1. Mandatory cognitive plane

An approved provider model:

- understands natural-language or event-framed intent;
- conducts clarification dialogue;
- forms one closed typed candidate;
- explains deterministic outcomes and residual uncertainty; and
- has no database, shell, cloud, deployment or command credentials.

### 2. Deterministic proof plane

Typed code outside the model container:

- validates closed schemas and canonical values;
- proves grounding against current authorized context;
- rejects unsupported inference and cross-scope references;
- enforces freshness, bounded retry, supersession and release rules;
- classifies risk and required authority; and
- emits an admitted typed projection, proposal or plan, never a direct effect.

### 3. Authority plane

The trusted backend decides whether the admitted candidate requires:

- ordinary staff confirmation;
- practice-manager or practice-owner confirmation;
- dual review or separation of duties;
- a maintenance window;
- deployment or release approval; or
- unconditional rejection.

A human gate supplements the provider model. It does not remove the model from
the intelligent loop, and model participation never substitutes for the gate.

### 4. Execution and verification plane

Only a single-purpose, allowlisted, typed command may act. The backend owns the
principal, practice or environment scope, current-state revalidation,
idempotency, transaction, audit, outbox, rollback and bounded receipt. Separate
deterministic readback proves the resulting state. The provider model may then
explain that evidence but cannot declare success independently.

## Domain partition

### Bernie: prospective scheduling intelligence

Bernie owns conversational interpretation of future-oriented appointment and
Diary work: finding, creating, moving, resizing, cancelling and explaining
appointments. Bernie translates user language into the shared typed Diary
grammar. The deterministic Diary domain owns availability, conflicts,
freshness, confirmation, writes and audit.

### Rayleen: present-tense waiting-room intelligence

Rayleen is a separate intelligence for arrivals, waiting states, queue flow,
waiting-area placement, practitioner flow and intent-projected waiting-room
views. Rayleen may converse with appropriately authorized staff and, only under
future separately reviewed patient-client identity rules, patients.

Rayleen does not create another waiting-room database or command family. She
uses the same backend-owned appointment, status, waiting-area, identity, audit
and event truth as Reception One. Her model selects or proposes typed projection
parameters and action candidates; deterministic code calculates waiting times,
membership, ordering, thresholds, state validity and command admission.

The historical description of Rayleen as only a server-side auto-arrival daemon
is superseded. Such deterministic observations may remain inputs, but Rayleen
is the model-required present-tense operational intelligence over them.

### Davida: institutional and practice-administration intelligence

Davida owns natural-language interaction over slower-changing practice
configuration and institutional knowledge: locations, practitioners, rooms,
waiting areas, capability posture, onboarding, policy and administrative change
proposals.

Davida must gain a dedicated practice-administration intent grammar, authored-
synthetic language corpus and evaluator comparable in discipline, but not
necessarily vocabulary or implementation, to Bernie's. Her mandatory provider
model forms typed read, explanation, dry-run and proposal candidates. The
deterministic practice-administration services and command plane retain all
authority.

### Branded workspaces are not authority boundaries

`RECEPTION ONE™` and the candidate `Clinician One` name should be treated as
coherent user-facing workspace/projection families, not as security principals,
monolithic agents or fixed staff-role partitions. Branding can organise the
experience around reception and clinical work, but it does not decide which
capabilities a user may invoke.

Authority belongs to smaller typed Bureau capabilities and their backend
actions. A user's effective Raisa surface is assembled atomically from current
role, practice, location, purpose, patient/encounter relationship where
applicable, consent and explicit capability grants. The same person may be
authorised for some capabilities commonly shown in Clinician One or Reception
One and not others; a workspace must omit or disable every Bureau and command
that is not independently granted.

Alongside Consultant's diagnosis and patient-safety focus, the clinical and
practice system will require at least these separately governed future Bureau
families:

- requests, correspondence and referrals;
- prescribing, medicines and medication safety; and
- billing, claiming and financial administration.

These families may interweave with Diary, arrival, practitioner, encounter and
practice-administration work. They do so through typed Context Fabric frames,
bilateral handoffs and the ordinary backend command plane—not through shared
private model memory or authority inherited from a branded shell. Prescribing,
referral, billing and clinical commands retain their own proofreader, human
confirmation, audit, idempotency, post-action verification and professional or
statutory controls.

This section is a permanent architecture direction only. It grants no product,
patient, clinical, prescribing, referral, billing, provider, runtime, command,
deployment or production authority and does not settle final Bureau names or
public branding.

### Controlled recovery and update intelligence: technical control plane

The recovery/update intelligence is separate from all product-domain agents and
from the Ariadne development harness. It operates over version-bound technical
evidence, not patient or clinical context, and uses a separately scoped runtime
identity.

Its provider model is mandatory for operator dialogue, diagnostic synthesis,
candidate runbook selection, update-plan formation and explanation. It receives
only typed system-anatomy frames such as:

- deployed application and component versions;
- health, dependency and saturation observations;
- database schema head and migration compatibility;
- sanitized structured error and audit summaries;
- configuration and policy drift results;
- backup, restore and replica verification status;
- signed runbook definitions and preconditions; and
- signed reference-data provenance and version manifests.

The model emits only closed candidates such as `DiagnosisCandidate`,
`RecoveryPlanCandidate`, `RunbookSelectionCandidate` or
`ReferenceUpdatePlanCandidate`. It cannot emit executable shell, SQL or cloud
instructions for direct execution.

Deterministic proof and authority gates verify evidence sufficiency, exact
runbook identity, preconditions, blast radius, reversibility, rollback,
separation of duties and postconditions before a narrowly privileged actuator
can run anything.

## Foundational safety automation is not optional-model intelligence

Transaction rollback, process liveness, connection timeout, circuit breaking,
platform restart and other preconfigured low-level safeguards remain
deterministic infrastructure. They may operate when a provider is unavailable
because they are not diagnostic or conversational Bureau decisions.

When the provider is unavailable:

- the core PMS and ordinary deterministic/manual controls remain available;
- preconfigured infrastructure safeguards continue;
- no new intelligent interpretation, diagnosis, projection, proposal or repair
  plan is released; and
- the affected intelligent capability reports an explicit unavailable or
  degraded state.

This is continuity of the underlying PMS, not an optional replacement for the
provider model.

## Provider posture

The architecture is provider-neutral but not provider-optional. At least one
provider/model binding must be explicitly configured and accepted before a
named intelligent runtime can be enabled. Any alternate provider requires its
own privacy, security, data-class, region, schema, quality, cost and operational
acceptance. Fallback is never silent.

Frontend clients do not call providers. Every call traverses the EMR4 Access AI
boundary with application identity, capability entitlement, practice or
environment scope, context admission, audit and proofreader-controlled egress.

## Isolation and reuse

Bernie, Rayleen and Davida may share a hardened work-cell base image, typed
contract libraries and deterministic domain packages. They use separate cells,
capability charters, context allowlists, application identities, audit
namespaces and lifecycle policy. Sharing code does not imply shared authority.

The recovery/update intelligence uses a separate technical control-plane
deployment identity and failure domain. It must not inherit product database,
patient, clinical, cloud-owner or unrestricted deployment credentials. Its
actuator is a different component from its model cell and receives only one-use
typed execution authority.

## API Spine alignment

- GraphQL and other query services provide scoped read/context frames only.
- Provider-model invocation is a backend Access AI command and never a frontend
  provider call.
- Product and technical changes use single-purpose REST/OpenAPI commands.
- Events report committed observations and may request a fresh cognitive pass;
  they never grant command authority.
- YAML declares capability, context, runbook and update policy; typed code and
  database policy enforce it.

## Closed gates

This revision grants no Rayleen client, arrival read or write, waiting-room
model context, Davida model runtime, administrative command implementation,
recovery observer, diagnostic model call, actuator, shell, SQL, cloud/IAM,
database migration, backup restore, reference-data import, policy activation,
provider, cost, real identity/data, patient/clinical data, deployment,
production, release, protected-ref or Pages authority.
