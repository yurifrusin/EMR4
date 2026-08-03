# Security Hardening Proposal: Cognitive-cell compromise containment

## Decision

Decide the minimum lifetime, bridge and runtime-isolation contract that Gate
zero must impose on every mandatory provider-model attempt. The contract must
remain safe when the model follows injected instructions and when the local
cognitive wrapper is compromised before proofreading.

## Executive Recommendation

We have three options. Option 1, **long-lived shared hardened container**, keeps
a warm service with conventional controls. Option 2, **one-shot brokered cell**,
creates a fresh sealed cell per Bureau attempt and makes a deterministic broker
the only provider and output bridge. Option 3, **one-shot microVM cell**, retains
the broker contract and adds a separate-kernel boundary.

I recommend Option 2 as the platform-neutral Gate-zero minimum. It gives the
cleanest lifetime and capability story without selecting infrastructure before
we have measurements. Option 3 should win later if recovery-domain risk or
concrete runtime evidence justifies its additional latency, memory and operating
burden.

## Evidence

I inspected the existing admission and isolation evidence before treating the
new external failures as applicable analogies. EMR4 has already demonstrated
several strong controls; the gap is that they are not yet the binding contract
for future product cognitive cells.

| Evidence | Finding or document | What it establishes |
| --- | --- | --- |
| `E004` | [Bounded Cognitive Work Cell design](../../../../ariadne-bounded-cognitive-work-cell-protocol-design.md) | Cognitive drafts can be isolated from proof and authority with closed egress. |
| `E006` | [Sandbox-DAG design](../../../../ariadne-sandbox-dag-protocol-design.md) | Immutable policy and bilaterally allowed typed links can constrain node communication. |
| `E009` | [Real-isolation rehearsal](../../../../ariadne-real-isolation-rehearsal-design.md) | A pinned, non-root, read-only, mount-free, network-free profile has repository evidence. |
| `E010` | [Real-isolation threat-model delta](../../../ariadne-real-isolation-rehearsal-threat-model-delta.md) | The rehearsal explicitly does not prove kernel, daemon, prompt/tool or adaptive-model safety. |
| `E011` | [Bounded agent admission](../../../../ariadne-bounded-agent-admission-design.md) | A new cell can begin with empty tools, secrets and capabilities and draft-only egress. |
| `E012` | [Agent-admission threat-model delta](../../../ariadne-bounded-agent-admission-threat-model-delta.md) | Admission treats untrusted evidence separately from immutable control-plane policy. |
| `E016` | [Microsoft prompt-to-RCE and host-bridge research](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/) | Model-controlled input reached evaluation and host file-write bridges in real agent frameworks. |
| `E021` | [NCSC agentic-AI adoption guidance](https://www.ncsc.gov.uk/blogs/thinking-carefully-before-adopting-agentic-ai) | Least privilege, temporary credentials, scope, monitoring, threat modelling and incident planning are necessary system controls. |

**Observed:** existing EMR4 protocols already favor empty capabilities, closed
typed output and strong container flags.

**Inferred:** a future wrapper that adds evaluation, file, URL, callback,
telemetry, upload or generic tool convenience could bypass the proof plane
before a typed candidate exists. The Microsoft cases establish that this bridge
class is practical, not that EMR4 currently contains the same vulnerable code.

## Current Design And Failure Mode

The intended product architecture sends a minimal typed frame into a cognitive
cell, uses a provider model for interpretation, and receives a typed candidate.
The proofreader then validates it. That structure is safe only if every byte and
capability between the frame and proofreader is completely mediated.

An injected model response could target a framework parser, template,
deserializer or generated-code feature. It could instead supply an attacker-
selected path, URL, callback or destination to a nominally legitimate tool. If
the wrapper is long-lived or ambiently connected, the compromise can reach host
files, sockets, credentials, metadata, another Bureau, the database or an
actuator, and then persist in cache, memory or filesystem. This attack occurs
before ordinary candidate proofreading.

## Desired Invariants

- Each Bureau attempt receives a fresh cell generation, identity, quota and
  empty writable state.
- The model-accessible surface is exactly one closed typed input and one closed
  candidate output.
- Provider destination, model, region, identity, data class, budget and retry
  are broker-owned and immutable to model output.
- The cell has no shell, generated-code execution, generic tool, host path,
  mount, runtime socket, metadata endpoint, credential, database, cloud,
  deployment or actuator capability.
- The broker treats output as hostile bytes, accepts one bounded canonical
  UTF-8 JSON document, and never evaluates or dereferences model-controlled
  code, template, object, path, URL or callback.
- Every bridge is versioned, registered, policy-bound and denied when unknown.
- No state, memory, cache, filesystem or identity crosses Bernie, Rayleen,
  Davida, recovery or attempts.
- Every terminal state kills and destroys the cell and records bounded residue.

## Constraints And Non-Goals

The provider model remains mandatory for an intelligent capability. This
proposal does not select a provider, runtime vendor, container engine or
microVM; prove sandbox invulnerability; add an actuator; or open product data.
We have no measured startup, concurrency or memory budget. The recovery Bureau
may analyze typed technical evidence, but its cognitive cell receives no
special route to the separately identified authority service or actuator.

## Before Architecture

[Before diagram](../diagrams/cognitive-cell-compromise-containment-before.mmd)

The diagram marks a future wrapper and the host bridges that are not yet frozen.
It does not assert that those bridges currently exist. Its purpose is to show
why the security boundary must be the broker's exhaustive interface rather than
an expectation that future framework features remain harmless.

## Options

### Option 1: Long-lived shared hardened container

The strongest case for a shared container is operational efficiency. A warm
runtime avoids repeated startup, reuses caches and parser memory, and has fewer
objects to schedule. Existing EMR4 evidence supports non-root execution, a
read-only root, no mounts, dropped capabilities, no-new-privileges, resource
limits and no ambient network. Those should remain baseline controls.

The shared lifetime is the problem. A parser or wrapper compromise can remain
in process state, writable temporary storage or cache and affect later requests.
Sharing the runtime across Bureaus also puts more charters and provider bindings
behind one failure boundary. Memory may be lower at steady state and latency
better, but a corrupted warm process degrades reliability rather than isolating
one failed attempt. Incident scope and residue analysis become larger even if
ordinary deployment is simpler.

We could roll it out conventionally and roll it back by stopping the service,
but the user-visible intelligent path would still depend on a boundary that
does not match the separate-Bureau design. I reject it as the Gate-zero minimum.

[Option 1 after diagram](../diagrams/cognitive-cell-compromise-containment-long-lived-shared-hardened-container-after.mmd)

| Change | Before | After | Security consequence | Cost |
| --- | --- | --- | --- | --- |
| Runtime lifetime | Unfrozen | One warm shared service | Compromise can span requests | Low startup cost |
| Bureau state | Intended separation | Shared process/caches | Cross-Bureau contamination becomes plausible | Lower aggregate memory |
| Hardening | Prior rehearsal only | Conventional container profile | Narrows ordinary privilege, not persistence | Profile maintenance |

The after diagram's shared edges are exactly what make the option efficient and
what enlarge its compromise window.

### Option 2: One-shot brokered cell

Create a fresh pinned cell for one Bureau attempt. A trusted deterministic
broker constructs one minimal labeled input, owns the provider request, and
returns provider response bytes to the same cell. The cell can emit exactly one
bounded candidate. It has no general HTTP client or provider credential; the
broker pins destination, model, region, identity, data class, budget and retry
outside model control.

The runtime profile is non-root/rootless where supported, read-only,
mount-free, without host or runtime sockets, with dropped capabilities,
no-new-privileges, syscall restriction, and process, CPU, wall-time, memory and
output quotas. The broker parses one canonical UTF-8 JSON document with size,
depth, member and string bounds and duplicate-key rejection. It performs no
`eval`, generated-code execution, polymorphic deserialization, template
interpolation, path access, URL fetch, callback or upload based on cell output.

This adds creation, copy, provider-relay and teardown latency, and concurrent
attempts consume separate bounded process memory. We should measure p50/p95/p99
end-to-end latency, per-cell RSS and maximum safe concurrency on the actual
runtime. In return, failure is easy to reason about: one malformed, killed or
compromised cell cannot corrupt the next attempt. Broker startup, relay and
teardown failures are new but can terminate with typed receipts.

Operation requires pinned-image provenance, runtime profiles, an exhaustive
bridge registry, quotas, alerts and residue evidence. Migration begins with a
platform-neutral Gate-zero protocol and a provider-free hostile-output harness;
no occupied model path starts until a concrete runtime passes. Rollback disables
the intelligent binding and returns to deterministic/manual PMS controls,
never to a warm cell with more authority. I select this option.

[Option 2 after diagram](../diagrams/cognitive-cell-compromise-containment-one-shot-brokered-cell-after.mmd)

| Change | Before | After | Security consequence | Cost |
| --- | --- | --- | --- | --- |
| Lifetime | Unfrozen future wrapper | One fresh cell per attempt | Compromise and residue are attempt-bounded | Cold start and teardown |
| Provider access | Future implementation unspecified | Broker-owned pinned envelope | Model cannot redirect network, identity, model or budget | Relay hop and broker ownership |
| Input/output | Typed intent, bridge details unfrozen | One closed input and one hostile-byte output | Complete mediation can be tested | Parser and schema maintenance |
| Host capabilities | Earlier rehearsal, not product contract | No tools, mounts, sockets, paths, metadata or credentials | Prompt-to-host paths are removed by construction | Runtime-profile enforcement |
| Terminal state | Unfrozen | Kill, destroy and residue receipt | Persistence is observable and bounded | Cleanup and evidence cost |

The decisive edge is the broker. It owns provider transport and parses a
candidate, but it does not become a generic tool router. Every added bridge is
a new security-architecture decision.

### Option 3: One-shot microVM cell

This option preserves Option 2's exact broker and channel contract but runs the
cell behind a separate guest kernel. Its strongest case is high-assurance
containment when a shared-kernel container escape is inside the accepted threat
model. Recovery analysis may eventually justify that profile even though the
model still cannot reach an actuator.

We should be honest about the operating cost. Boot and device setup are likely
slower; each concurrent attempt carries guest-kernel memory; and kernel images,
hypervisor patching, capacity, telemetry and incident response need mature
ownership. More components can also reduce availability even while improving
failure isolation. Those effects are analogous, not measured here. A prototype
must run the same broker suite on the actual candidate platform and compare
p50/p95/p99 latency, resident memory, concurrency and fault recovery with
Option 2.

The stable broker protocol makes later migration and rollback credible. We can
replace only the runtime profile, preserve schemas and policies, and fall back
to a previously accepted one-shot profile if the microVM platform fails its
resource or reliability thresholds. I defer this option because the current
evidence does not show that its extra boundary is worth the unmeasured cost.

[Option 3 after diagram](../diagrams/cognitive-cell-compromise-containment-one-shot-microvm-cell-after.mmd)

| Change | Before | After | Security consequence | Cost |
| --- | --- | --- | --- | --- |
| Kernel boundary | Host/shared runtime unfrozen | Disposable guest kernel | Narrows shared-kernel escape | Boot latency and fixed memory |
| Broker protocol | Same selected contract | Unchanged | Authority and bridge semantics do not drift | Runtime adapter work |
| Operations | Container-class profile | MicroVM images and hypervisor | Stronger isolation with new platform risk | Patching, capacity and telemetry |

The unchanged broker edge is important: stronger runtime isolation must not
gain more tools, data or authority.

## Comparison

| Option | Security | Performance | Memory | Reliability | Operability | Migration |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Long-lived container | Ordinary privilege reduction; persistent shared compromise | Best warm latency | Shared warm footprint | Warm availability; corruption spans attempts | Few objects; broad incident scope | Conventional, but wrong lifetime boundary |
| 2. One-shot brokered cell | Attempt-bounded, no ambient bridges | Cold start, relay and teardown | Bounded process per concurrent attempt | Failures isolated; more explicit terminal states | Image, broker, bridge and residue ownership | Gate-zero protocol then provider-free runtime proof |
| 3. One-shot microVM | Adds separate-kernel isolation | Highest expected startup cost | Guest-kernel overhead | Strong isolation; more orchestration failures | Highest platform burden | Compatible runtime swap after measurement |

No table entry is a benchmark. Gate zero should record the workload, baseline,
candidate runtime, metrics and thresholds before choosing infrastructure.

## Recommendation

I recommend Option 2 because it fixes the lifetime and bridge problem at the
architecture level while leaving the concrete runtime replaceable. It also
matches EMR4's separate Bernie, Rayleen, Davida and recovery charters: no shared
model memory or process needs to be trusted.

Option 3 should replace it as the first runtime profile if an approved threat
model includes shared-kernel escape and a prototype meets the agreed latency,
memory, concurrency and operability thresholds. Option 1 should not win merely
because it is faster; if one-shot overhead is unacceptable, we should narrow
the intelligent workflow or invest in safe pre-pulled images rather than widen
the compromise lifetime.

## Evidence Coverage And Residual Risk

| Evidence | Coverage by recommendation | Residual risk |
| --- | --- | --- |
| `E004` — Cognitive Work Cell | Promotes draft-only closed egress into the product cell contract | Broker implementation becomes a trusted component |
| `E006` — Sandbox-DAG | Uses immutable policy and typed allowed links | Policy generation and version binding can be wrong |
| `E009` — Real isolation | Retains pinned, non-root, read-only, mount-free and network-denied controls | Host kernel/runtime zero-days remain |
| `E010` — Isolation limits | Preserves the explicit no-invulnerability claim | Microarchitectural and daemon risk remain outside the proof |
| `E011` — Agent admission | Starts with empty tools, secrets and capabilities | A future bridge can widen reach if governance fails |
| `E012` — Admission threat model | Separates untrusted evidence from immutable control policy | Broker or manifest parser defects remain |
| `E016` — Prompt-to-host failures | Removes evaluation, model-selected path and generic tool bridges | Novel parser/bridge classes require ongoing adversarial review |
| `E021` — Agentic-AI controls | Applies least privilege, temporary identity, scope, monitoring and incident evidence | Operational control quality must be proven later |

Provider-side compromise, host/hypervisor vulnerabilities, covert channels in
an explicitly allowed response, denial of service and policy mistakes remain.
The selection bounds reach and lifetime; it does not claim that a sandbox is
invulnerable.

## Migration And Rollout

Gate zero first defines the cell, broker, parser, bridge, quota and residue
schemas without choosing or starting a runtime. A provider-free reference cell
then receives authored-synthetic hostile inputs and outputs and proves that no
unregistered bridge is reachable. A concrete runtime profile is source-hashed,
dependency-reviewed and tested in default-off mode. Only after deterministic
acceptance and independent veto could a separately authorized occupied model
rehearsal be considered.

Rollout is one Bureau and one bounded capability at a time. The provider binding
and cell identity remain distinct per Bureau. Teardown or residue failure opens
no retry automatically. Rollback revokes that broker binding and disables the
intelligent path while deterministic/manual product controls remain available.

## Validation Plan

- Attempt generated-code, `eval`, template, polymorphic-deserialization,
  duplicate-key, Unicode, depth, member, string and oversized-output attacks.
- Attempt path traversal, arbitrary file write/read, URL and callback redirect,
  upload destination, metadata access, environment and credential discovery,
  host/runtime socket access, database reach and actuator reach.
- Attempt cross-request and cross-Bureau memory, filesystem, cache, process and
  identity reuse.
- Fault-inject provider timeout, malformed provider bytes, quota exhaustion,
  process kill, broker restart, teardown failure and retry amplification.
- Verify one terminal receipt, deterministic destruction and zero owned residue
  for every terminal state.
- Review runtime and parser dependencies and the chosen isolation platform's
  escape boundary without converting a clean scan into a zero-day claim.
- Benchmark the same authored-synthetic workload for p50/p95/p99 latency,
  per-cell/total RSS, maximum concurrency, error rate and teardown time. Gate
  zero must establish thresholds before interpreting the results.
- Rehearse image revocation, bridge-version mismatch, compromised-cell
  investigation and safe path disablement.

## Implementation Work Packages

These packages are a future handoff outline, not authorization to implement:

- one-attempt cell input/output and identity schemas;
- broker-owned provider envelope and immutable binding;
- hostile-byte canonical JSON parser profile;
- deny-by-default bridge registry and admission manifest;
- runtime security profile and dependency inventory;
- quota, kill, teardown and residue evidence;
- provider-free adversarial cell harness; and
- runtime resource, failure and incident-rehearsal benchmark.

## Open Questions

- What p95 latency, peak memory and concurrency budgets should Gate zero use?
- Which platform will enforce provider-only egress without exposing a general
  HTTP client or credential to the cell?
- Does the first recovery-domain runtime require a separate kernel immediately,
  or can that decision wait for the Option 2 prototype evidence?
- Which team owns broker, image and runtime-profile patch SLAs in a future
  production design?
