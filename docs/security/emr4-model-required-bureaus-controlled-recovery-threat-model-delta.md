# Threat-model delta: model-required Bureaus and controlled recovery

Date: 2026-08-04

Status: architecture planning only

Parent:
`docs/emr4-model-required-deterministic-authority-bureau-architecture.md`

## Assets and trust boundaries

Newly material assets are provider-model availability, typed cognitive
candidates, system-anatomy frames, signed runbooks, update provenance,
authority evidence and actuator receipts. The provider model, cognitive cell,
proofreader, authority service and actuator are distinct trust boundaries.

## Threats and required controls

### Provider outage is mistaken for permission to substitute fake intelligence

Controls:

- fail the named intelligent capability explicitly;
- keep the core PMS and deterministic/manual controls available;
- permit only preconfigured foundational infrastructure safeguards;
- prohibit silent heuristic, model or provider fallback; and
- require separately accepted failover providers.

### Mandatory model participation becomes authority

Controls:

- model output is always a candidate;
- proofreader, authorization, command and readback remain independent;
- model credentials cannot reach databases, shells, cloud control planes or
  command actuators; and
- explanations cannot set success or audit fields.

### Cross-Bureau context leakage

Controls:

- separate capability charters, identities and context allowlists;
- Bernie receives prospective scheduling context, Rayleen present-tense
  waiting-room context, Davida practice-administration context and recovery
  technical context;
- no shared conversational memory store; and
- backend authorization precedes context formation.

### Rayleen exposes excessive waiting-room PHI

Controls:

- minimum operational fields and practice/location/resource scoping;
- deterministic aggregation before model admission where possible;
- short freshness/expiry, no routine raw prompt logging and no model memory;
- patient-facing identity and privacy gates remain closed; and
- projections cannot broaden the underlying authorized set.

### Prompt injection or operator wording selects an unsafe recovery action

Controls:

- user text and log text remain untrusted data;
- only signed runbook identifiers and closed parameters are admissible;
- the proofreader rejects free-form shell, SQL, URL or cloud instructions;
- deterministic preconditions and risk tier cannot be overridden by prose; and
- high-risk operations require independent human authority.

### Model hallucinates a system cause or success

Controls:

- every hypothesis cites typed evidence identifiers;
- missing evidence is explicit;
- unsupported causes reject rather than degrade to warning;
- deterministic readback alone sets completion; and
- failed or inconclusive attempts remain immutable audit evidence.

### Recovery actuator accumulates excessive privilege

Controls:

- actuator is separate from the cognitive cell and proofreader;
- one-use, target-bound, expiring execution evidence;
- exact runbook/parameter/environment allowlists;
- least-privilege service identities per operation class;
- idempotency, blast-radius limits, rollback and postcondition checks; and
- no generic shell, SQL console or cloud-owner credential.

### Malicious or defective reference update is promoted

Controls:

- signed provenance, licence and checksum validation;
- schema plus semantic-delta checks;
- issued/effective/expiry/supersession/withdrawal rules;
- quarantined shadow import and staged promotion;
- human or dual review according to update class;
- atomic activation, immutable audit and last-known-good rollback; and
- provider explanation cannot certify authenticity.

### Provider failover changes privacy, region, behavior or cost silently

Controls:

- no automatic unreviewed provider fallback;
- each binding has explicit provider, model, region, identity, data class,
  budget and proofreader acceptance;
- failover is an auditable policy decision; and
- unavailable intelligence is safer than undisclosed substitution.

### Development Ariadne becomes a production recovery actuator

Controls:

- the product recovery/update Bureau is a separate control-plane design;
- Ariadne receipts and worker authority do not transfer;
- development agents cannot receive live operational credentials by
  implication; and
- production recovery, deployment and release remain separate gates.

## Residual decisions

Before runtime work, Yuri must approve the provider/data boundary, acceptable
outage posture, recovery risk taxonomy, human/dual-review matrix, actuator
classes, reference-data sources/licences, retention/audit policy and first
isolated live-development rehearsal.
