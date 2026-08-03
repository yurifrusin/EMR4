# Security Hardening Proposal: Deterministic information-flow confinement

## Decision

Decide how Gate zero will prevent direct or indirect prompt injection from
turning a schema-valid model candidate into an attacker-directed command or
disclosure. The choice must preserve mandatory provider-model dialogue while
keeping all authority deterministic.

## Executive Recommendation

We have four serious options. Option 1, **schema and proofreader only**, preserves
the present design. Option 2, **frozen plan and parameter guards**, adds narrow
control-flow integrity. Option 3, **Bureau labeled capability envelope**, tracks
integrity, confidentiality/readers and capability scope end to end. Option 4,
**symbolic vault plus envelope**, additionally hides selected values from the
dialogue model.

I recommend Option 3 under the current constraints. It addresses both action
choice and argument/data influence without making the provider model optional.
We should keep Option 2 as defense in depth for genuinely fixed workflows and
revisit Option 4 only for fields whose content the dialogue model does not need
to inspect.

## Evidence

I inspected the repository sources at the target revision and used the external
research to test the structural inference rather than to claim an EMR4 runtime
result.

| Evidence | Finding or document | What it establishes |
| --- | --- | --- |
| `E001` | [Model-required Bureau architecture](../../../../emr4-model-required-deterministic-authority-bureau-architecture.md) | Cognition, proof, authority and execution are separate; model output is a candidate. |
| `E003` | [Current Bureau threat-model delta](../../../emr4-model-required-bureaus-controlled-recovery-threat-model-delta.md) | Context and candidates require typing, provenance, grounding and authority separation. |
| `E013` | [Access AI API design](../../../../../orchestration/access_ai_api_design.md) | Provider access is backend-owned and context frames are minimal and non-authoritative. |
| `E015` | [NIST CAISI large-scale red teaming](https://www.nist.gov/blogs/caisi-research-blog/insights-ai-agent-security-large-scale-red-teaming-competition) | Broad current-model testing found successful and transferable agent attacks, supporting an assume-compromise posture. |
| `E017` | [CaMeL: Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813) | Protecting control flow alone leaves data-flow and argument manipulation; provenance capabilities can constrain values. |
| `E018` | [FIDES: Securing AI Agents with Information-Flow Control](https://arxiv.org/abs/2505.23643) | Integrity and confidentiality labels can drive deterministic trusted-action and permitted-flow checks. |
| `E019` | [Agent security design patterns](https://arxiv.org/abs/2506.08837) | Fixed plans, quarantined models and symbolic values have distinct utility and residual-risk tradeoffs. |
| `E020` | [NCSC prompt-injection guidance](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection) | LLMs do not provide a reliable instruction/data boundary; system impact must be constrained. |

**Observed:** EMR4 already rejects malformed, ungrounded, stale or unauthorized
candidates and keeps model output away from direct database writes.

**Inferred:** those checks cannot distinguish two candidates with identical
schema and grounding when one was selected because low-integrity text instructed
the model to choose it. That inference is consistent with the control/data-flow
failure described by E017-E019.

## Current Design And Failure Mode

An attacker can place instructions in the user's request or in a value that the
model legitimately reads: a database field, policy, runbook, document, provider
response or previous output. The model can follow the instruction while still
emitting a closed candidate type and citing real backend facts. The proofreader
then sees a semantically plausible candidate but no deterministic lineage that
says which low-integrity value influenced the action selection, recipient,
identifier, wording or other security-relevant argument.

This is a confused-deputy path rather than a schema bypass. Human review is not
enough because the confirming user may see a plausible summary without hidden
Unicode, covert encoding or source influence. Confirmation should remain an
authority act, but it cannot retroactively make the source trustworthy.

## Desired Invariants

- Every source value, deterministic transformation, candidate field, command
  argument and response field has explicit versioned security metadata.
- Only trusted deterministic wrappers assign initial labels and capabilities.
- The model may not raise integrity, lower confidentiality, widen readers,
  create a capability, endorse a value or declassify data.
- Unknown source, missing label, unknown transformation and label loss reject.
- Consequential action selection and every security-relevant argument satisfy
  the destination sink's integrity and authority policy.
- Every egress recipient belongs to the joined reader set of all contributing
  values.
- Human confirmation, endorsement and declassification are separate signed,
  field-scoped, purpose-scoped and expiring acts.
- GraphQL and context frames remain read-only; writes continue through typed
  REST/OpenAPI commands with backend reauthorization, idempotency, audit and
  readback.

## Constraints And Non-Goals

The provider model remains mandatory for intelligent dialogue. We are not
designing a heuristic fallback, asking a detector to grant authority, changing
the API Spine mutation boundary, selecting a production provider, or opening
real identity or product data. We have no measured latency or memory budget, so
each resource claim below includes a measurement plan.

## Before Architecture

[Before diagram](../diagrams/deterministic-information-flow-confinement-before.mmd)

The diagram shows the existing strong separation, then the gap: influence and
reader constraints are not joined from sources through the candidate to each
sink. The proofreader knows *what* was proposed and whether it is grounded, but
not a complete deterministic account of *what influenced* every field.

## Options

### Option 1: Schema and proofreader only

The attractive part of this baseline is its simplicity. It preserves the
current schemas, grounding, freshness, authority ceiling and command checks,
adds no data structure, and imposes no new latency or migration. Those controls
remain necessary under every other option.

What gives me pause is that the failure mode is intentionally schema-valid.
No amount of duplicate-key or required-field checking reveals why the model
selected a real appointment, practitioner, recipient or action. Operationally,
an incident also lacks a source-to-sink influence trace. We could roll out this
option immediately because it is the current state; rollback is irrelevant.
Its strongest case is only where every permitted action and parameter is fixed
before the model sees any untrusted value.

[Option 1 after diagram](../diagrams/deterministic-information-flow-confinement-schema-proofreader-only-after.mmd)

| Change | Before | After | Security consequence | Cost |
| --- | --- | --- | --- | --- |
| Influence tracking | Provenance and grounding without deterministic lineage | Unchanged | Schema-valid injected decisions remain possible | None |
| Sink policy | Type, freshness and authority checks | Unchanged | Reader and integrity compatibility remain implicit | None |
| Audit | Candidate and command receipts | Unchanged | Root-cause reconstruction remains incomplete | None |

The after view is deliberately almost identical to the before view. That is a
fair representation of the option's low cost and its inability to close the
specific gap.

### Option 2: Frozen plan and parameter guards

This option asks the model to commit to an action sequence before it reads any
untrusted retrieved data. A deterministic executor then admits only those steps
and validates each argument against a command-specific policy. For narrow
workflows, this is appealing: it is easy to explain, prevents injected content
from adding a new action, and only retains one bounded plan and argument trace.

The limitation is material. A malicious value can still alter an allowed
recipient, identifier or body, and legitimate Bureau tasks often depend on
fresh backend data to decide whether to clarify, propose, explain or stop.
Making the plan language broad enough to accommodate every branch risks
recreating a general interpreter. Performance adds a plan-freeze step and
policy checks; memory adds the plan; operation adds a versioned template per
command family. We could introduce it incrementally for fixed commands and
roll back one template without changing the shared proofreader.

[Option 2 after diagram](../diagrams/deterministic-information-flow-confinement-frozen-plan-integrity-guard-after.mmd)

| Change | Before | After | Security consequence | Cost |
| --- | --- | --- | --- | --- |
| Action sequence | Model can choose after seeing all admitted context | Frozen before untrusted retrieval | Untrusted data cannot add or reorder actions | Extra planning step and templates |
| Arguments | Schema and semantic checks | Per-command allowlists | Narrows arguments but does not establish their integrity | Policy maintenance and false denials |
| Dialogue branching | Flexible | Constrained by plan language | Safer for fixed workflows; brittle for data-dependent dialogue | Utility and migration risk |

The changed edge protects control flow, not all data flow. I would use this as
a supplementary guard, not as the common Bureau boundary.

### Option 3: Bureau labeled capability envelope

This option makes security metadata part of every typed value: source and
transformation provenance, integrity principal set or trust class,
confidentiality/readers, freshness and expiry, Bureau/practice/subject/purpose
scope, and maximum authority/capability ceiling. Trusted wrappers assign source
labels. Deterministic transformations compute least-permissive joins. The model
sees the admitted values but cannot edit their labels; its candidate fields
inherit their declared dependencies and the joined context that influenced
their selection.

At each command sink, the proof plane checks both the integrity of the decision
to call the command and the integrity of every security-relevant argument. At
each response or other egress sink, it verifies that the destination is within
the joined reader sets. A missing label, unknown transformation, stale source,
scope widening or incompatible reader produces a typed denial. This is the
structural control that makes prompt-injected cognition non-authoritative.

The cost is real but bounded. Each request carries a value graph, label joins
and denial trace. Gate zero should measure p50/p95 proof latency, peak graph
bytes and maximum node count for small, typical and maximum frames rather than
guessing at a budget. Reliability improves through explicit fail-closed states,
while wrapper and policy version skew can produce safe false denials.
Operationally, EMR4 must own one central source/sink vocabulary and policy
rollout. Migration cannot permit partially unlabeled intelligent paths: Gate
zero freezes the envelope first, then each later Bureau registers all sources
and sinks. Rollback means disabling that intelligent path and returning to
deterministic/manual controls, never bypassing labels.

[Option 3 after diagram](../diagrams/deterministic-information-flow-confinement-bureau-labeled-capability-envelope-after.mmd)

| Change | Before | After | Security consequence | Cost |
| --- | --- | --- | --- | --- |
| Value metadata | Provenance/freshness conventions | Versioned integrity, readers, scope and authority labels | Untrusted influence and protected flows become machine-enforceable | Metadata and join CPU/memory |
| Transformations | Semantic proofreader logic | Registered deterministic joins | Unknown or label-losing transforms deny | Registry and conformance tests |
| Command sink | Schema, grounding, authority | Trusted-action policy on choice and arguments | Low-integrity input cannot trigger consequential action | More explicit denial cases |
| Egress sink | Output schema | Permitted-flow policy on recipients and fields | Reader-incompatible data cannot leave | Destination policy ownership |
| Human authority | Confirmation of candidate | Signed candidate hash plus separate endorsement/declassification | Review cannot silently upgrade source trust | Richer review UI and evidence |

The diagram's decision-relevant edge is the deterministic policy engine between
the hostile candidate and every sink. The model remains useful and mandatory,
but none of its judgments can mutate the labels that determine authority.

### Option 4: Symbolic vault plus envelope

This option retains Option 3 and stores selected low-integrity or confidential
values behind opaque handles. A quarantined extraction model or deterministic
transform can produce a narrow type; the main dialogue model manipulates the
handle without dereferencing the value. A trusted orchestrator resolves the
handle only after the labeled sink policy passes.

Its strongest case is a workflow where the dialogue needs to refer to a value
but not inspect it. It can prevent the value from injecting the main model and
reduce unnecessary disclosure. The concern is complexity: quarantined
extraction is still probabilistic, reveal policy can become a confused deputy,
and many useful explanations genuinely require the content. Extra provider
calls or transforms add latency, while an isolated vault and handle table add
memory and new stale/missing/cross-request failure modes. Incident debugging
also needs privacy-preserving traces.

We should introduce it field by field only after Option 3 is stable and a
prototype shows acceptable task completion. Rollback disables symbolic handling
for that workflow and keeps it closed until a safe base-envelope path exists;
it must never expose the raw value as a fallback.

[Option 4 after diagram](../diagrams/deterministic-information-flow-confinement-symbolic-vault-plus-envelope-after.mmd)

| Change | Before | After | Security consequence | Cost |
| --- | --- | --- | --- | --- |
| Model exposure | Model reads admitted value | Main model sees opaque handle | Selected value cannot inject main dialogue directly | Extraction/reveal complexity |
| Storage | Request context only | Isolated bounded value vault | Protected value has a separate boundary | Memory, expiry and cleanup |
| Sink resolution | Candidate contains value | Trusted component resolves handle after policy | Reveal is completely mediated | New high-trust resolver |

The diagram adds a useful isolation boundary but not a replacement authority
boundary. The labeled envelope still makes the final decision.

## Comparison

| Option | Security | Performance | Memory | Reliability | Operability | Migration |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Schema only | Leaves valid injected influence | No change | No change | Few components; silent unsafe influence | Simple; weak forensic trace | None |
| 2. Frozen plan | Protects action sequence, not all arguments/egress | One planning step and checks | One bounded plan | Predictable for fixed tasks; brittle for rich dialogue | Templates per command | Incremental but incomplete |
| 3. Labeled envelope | Protects choice, arguments and permitted flows | Bounded joins and sink checks | Bounded per-request graph | Explicit fail-closed denials; policy drift risk | Central registry and denial telemetry | Foundational Gate-zero change |
| 4. Symbolic vault | Adds selective model-data isolation | Extra transforms or calls | Isolated vault and handles | More reveal/expiry failures | Harder privacy-safe debugging | Per-field extension after Option 3 |

No resource effect in this table is measured. The validation plan must compare
each candidate with the current schema-only baseline using the same authored-
synthetic frames and explicit latency, memory and task-completion thresholds.

## Recommendation

I recommend Option 3 because it is the smallest option that covers both the
control-flow and data-flow failure modes while preserving EMR4's model-required
product decision. Option 2 should also be used where an action sequence is
truly fixed. Option 4 should win for a specific value only when a prototype
shows that hiding it materially reduces risk without undermining dialogue.

A different recommendation would be appropriate if Gate zero proves that the
label graph cannot meet an agreed latency or memory budget. In that event, we
should narrow the first intelligent workflows, not silently revert to schema-
only authority.

## Evidence Coverage And Residual Risk

| Evidence | Coverage by recommendation | Residual risk |
| --- | --- | --- |
| `E001` — Bureau separation | Extends the proof plane without merging cognition, authority or execution | Incorrect proof policy remains possible |
| `E003` — Current threat controls | Preserves typing, grounding, freshness and authority ceilings | Source wrappers can assign a wrong label |
| `E013` — Access AI boundary | Keeps provider transport backend-owned and context non-authoritative | Provider-side retention is outside local IFC |
| `E015` — Large-scale red teaming | Assumes model failure rather than model immunity | Novel attacks can still affect response quality and availability |
| `E017` — CaMeL capabilities | Covers provenance/capability influence and tool arguments | EMR4's adaptation requires its own formal/property tests |
| `E018` — FIDES IFC | Covers trusted-action and permitted-flow decisions | Covert and implicit confidentiality channels are not all eliminated |
| `E019` — Design patterns | Retains fixed plans and symbolic handling where proportionate | Pattern composition can introduce new trusted components |
| `E020` — NCSC guidance | Bounds impact rather than claiming injection detection | Social engineering and policy mistakes remain |

## Migration And Rollout

Gate zero should first freeze the label lattice, versioned envelope and source/
sink registries without mounting a runtime. A provider-free reference evaluator
then proves joins, denials, endorsement and declassification. Each later Bureau
may register one bounded source/sink set while remaining default-off. Fixed-plan
guards can be added inside that envelope. An occupied rehearsal is eligible
only after provider-free adversarial acceptance and an independent veto.

Rollout is fail-closed by construction: missing labels, wrapper drift or an
unknown sink leave the intelligent capability unavailable while the manual and
deterministic PMS remains usable. Rollback removes the affected intelligent
binding rather than weakening label policy.

## Validation Plan

- Property-test label joins for associativity, monotonic restriction, reader
  intersection, scope non-widening and authority non-escalation.
- Test missing labels, unknown transforms, stale sources, mixed practices,
  cross-Bureau values, incompatible readers and expired authority.
- Use direct and indirect injection cases in user text, product fields,
  documents, policy/runbook text and provider output while preserving valid
  candidate schemas and real grounding identifiers.
- Test action choice, every security-relevant argument, explanations, logs and
  all response destinations independently.
- Test endorsement, declassification and confirmation as field-specific signed
  acts; prove that confirmation does not upgrade source integrity.
- Benchmark baseline versus Option 3 for p50/p95 proof latency, peak graph bytes,
  maximum node count and authored-synthetic task completion. Gate zero must set
  the decision thresholds before interpreting the measurements.
- Reconstruct a denied attack from immutable source-to-sink evidence without
  logging protected raw prompts.

## Implementation Work Packages

These packages are a future handoff outline, not authorization to implement:

- shared label, dependency and denial schemas;
- deterministic label algebra and property tests;
- trusted source-wrapper registry;
- command, response and audit sink registry;
- endorsement, declassification and confirmation evidence;
- label-aware deterministic review presentation; and
- provider-free adversarial corpus and resource benchmark harness.

## Open Questions

- Which integrity principals and reader sets are sufficient for the first
  authored-synthetic Bureau frames without encoding real identity policy?
- Which future fields genuinely require human endorsement or declassification?
- What p95 proof latency and peak per-request metadata budget should Gate zero
  enforce?
- Which field, if any, is the first credible candidate for the symbolic-vault
  extension?
