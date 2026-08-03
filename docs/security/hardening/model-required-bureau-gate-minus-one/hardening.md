# Security Hardening Review: Model-required EMR4 Bureaus

## Evidence Basis

I reviewed the source-hashed EMR4 Bureau architecture, Access AI boundary,
work-cell and isolation protocols at revision
`b09739183ddbe1a102086460749a84741a23b11b`, then compared those controls with
current primary research on agent hijacking, control/data-flow security and
prompt-to-host compromise. The 21-item collection and its digest are recorded
in `evidence-index.json` and explained in `context.md`.

The strongest observed property is already present: the provider model is a
candidate generator, while proofreading, authority, commands and readback are
deterministic and separate. What gives me pause is the unfilled space between
those components. A schema-valid candidate can still reflect low-integrity
instructions, and a compromised wrapper can bypass the proof plane if any host
bridge consumes model-controlled bytes first.

The research does not support a claim that prompt injection can be eliminated
by better prompting or detection. It does support a structural response: track
influence and permitted flows deterministically, expose fewer capabilities, and
contain the lifetime and reach of each compromised attempt.

## Constraints

- Provider-model participation remains mandatory for named intelligent
  dialogue; provider outage fails that capability explicitly.
- The model, its prompt, its explanation and its wrapper never supply product
  authority.
- GraphQL and context frames remain read-only; mutation continues through
  typed REST/OpenAPI commands with backend reauthorization, idempotency, audit
  and readback.
- The review may recommend Gate-zero architecture but may not wire a provider,
  open product or patient data, add a tool or actuator, deploy, or move a
  protected ref.
- No measured runtime latency or memory budget is available, so resource
  effects are mechanisms and validation plans rather than benchmark claims.
- Prompt detectors, provider safeguards, canaries and human review are useful
  defense in depth but cannot raise integrity or grant a capability.

## Opportunity Portfolio

| Opportunity | Evidence | Options | Recommendation | Proposal |
| --- | --- | --- | --- | --- |
| Deterministic information-flow confinement | Existing Bureau/Access AI proof boundaries plus CaMeL and FIDES influence-policy research (E001-E003, E013, E017-E019) | Schema only; frozen plan; labeled capability envelope; symbolic vault extension | Select the labeled capability envelope; retain fixed plans as a narrow extra guard | [Deterministic information-flow confinement](proposals/deterministic-information-flow-confinement.md) |
| Cognitive-cell compromise containment | Existing isolation/admission evidence plus Microsoft's prompt-to-RCE and host-file bridge research (E009-E012, E016, E021) | Long-lived container; one-shot brokered cell; one-shot microVM | Select a platform-neutral one-shot brokered cell; preserve microVM as a stronger compatible profile | [Cognitive-cell compromise containment](proposals/cognitive-cell-compromise-containment.md) |

These two opportunities form one decision set. The first prevents hostile
cognition from turning low-integrity influence or protected values into an
authorized sink decision. The second makes the same reasoning hold when the
cognitive wrapper itself is compromised before a candidate reaches the
proofreader.

## Recommendation Summary

I recommend making both selected options prerequisites for Gate zero:

- `bureau-labeled-capability-envelope` adds versioned provenance, integrity,
  confidentiality/readers, freshness, scope and authority ceilings to every
  typed value. Trusted deterministic wrappers assign and join those labels;
  command and egress sinks deny incompatible influence or readers.
- `one-shot-brokered-cell` gives each Bureau attempt a fresh identity and
  sealed lifetime, exactly one typed input and one typed candidate output, and
  no ambient shell, code, tool, filesystem, path, callback, network,
  credential, database or actuator bridge. A deterministic broker owns the
  pinned provider transport and hostile-byte parser.

The recommendation is proportionate under the current high-assurance clinical
constraint because it does not make natural-language interaction optional and
does not ask a model to police itself. A frozen-plan-only design would be
preferable for an exceptionally narrow, data-independent command, but not as
the shared Bureau contract. A symbolic vault becomes preferable for specific
fields that the dialogue model need not inspect. A microVM becomes preferable
if concrete container-escape risk or recovery-domain requirements outweigh its
measured latency, memory and operating cost.

The selected architecture still does not prove implementation, sandbox
invulnerability, provider trustworthiness, correct production labels or the
absence of all covert channels. It changes those from hidden model assumptions
into named, testable residual risks.

## Next Decisions

Before any implementation planning, reviewers should decide whether to accept
the two recommendations as Gate-zero admission conditions. If accepted, Gate
zero must freeze the label algebra, source/sink registry, endorsement and
declassification rules, provider broker, hostile-byte parser, bridge inventory,
runtime profile, quotas, teardown and residue schemas.

The first later runtime decision is deliberately not made here: select a
concrete disposable-container or microVM profile only after the platform-neutral
broker contract exists and p95 latency, peak memory, concurrent-cell capacity
and failure-isolation evidence can be measured. Until then Gate zero and Lanes
A-D remain closed.
