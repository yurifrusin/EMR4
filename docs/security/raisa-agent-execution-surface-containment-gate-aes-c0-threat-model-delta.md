# Threat-model delta: Raisa AES-C0 architecture contract

Date: 2026-08-11

Status: architecture-only, provider-free and unmounted

## Scope and security objective

This delta refines the accepted Agent Execution Surface threat model into six
closed message types and deterministic invariants. The security objective is
that compromise of a future occupied Bureau work cell, including malicious but
schema-shaped model output, cannot manufacture authority, select an operation
identity, reach an ambient capability, suppress revocation, cross a generation
boundary or turn context/proposals into commands.

AES-C0 changes no runtime surface. It introduces contract evidence only.

## Assets

- human, practice, purpose and atomic capability authority;
- ContextFrameSet and Memory Bank confidentiality, provenance, freshness and
  expiry;
- immutable generation manifests, audience-bound leases and cumulative budget
  state;
- provider, product, database, cloud, repository and command credentials;
- product, Diary, administrative, financial and clinical truth;
- adapter, model/provider contract, system contract and runtime-image identity;
  and
- minimized audit, revocation and incident evidence.

## Actors and trust posture

| Actor/component | Trust posture |
|---|---|
| Human user and product surface | authenticated input, but authority is rechecked by the backend |
| Backend authority kernel | trusted to bind current principal, practice, purpose and capability |
| Context assembler | trusted only to produce typed, minimized, source-labelled inert frames |
| Model/work cell | untrusted candidate generator; compromise is assumed possible |
| Deterministic proofreader | trusted for closed shape/grounding admission, not command authority |
| External capability broker | future trusted authority kernel; absent in AES-C0 runtime |
| Exact adapter | future least-authority transport/read boundary; absent in AES-C0 runtime |
| External stop control | independent trusted revocation, quarantine and evidence owner |

## Trust boundaries and data flows

1. authorized product surface to backend authority kernel;
2. context assembler to occupied work cell;
3. work-cell bytes to deterministic proofreader;
4. proofreader result to external capability broker;
5. broker to one exact allowlisted adapter;
6. adapter to external or product system;
7. inert proposal to separately authorized REST/OpenAPI command; and
8. minimized telemetry to external stop, revocation and incident control.

No model output controls any boundary. GraphQL is a read-only context source,
an event is only a reason to perform a fresh read, and neither is command
authority.

## Threat analysis

| Threat | STRIDE class | AES-C0 control | Deterministic evidence |
|---|---|---|---|
| Candidate forges a capability, adapter, destination, method or audience | Spoofing / elevation | broker resolves exact operation identity from immutable grant and current authority | candidate-identity and generic-network mutations reject |
| Manifest, lease or budget is changed during a generation | Tampering | immutable manifest; policy change creates a new generation; digest and cross-record binding | mutable-manifest, detached-digest and ceiling mutations reject |
| Operation occurs without attributable decision | Repudiation | closed `BrokerDecision` plus minimized cumulative `AuditEvidenceEnvelope` | missing/mismatched gate fields reject |
| Prompt, reasoning, credential or product value leaks through evidence | Information disclosure | exact evidence allowlist and forbidden-field recursion | raw-prompt and sensitive-evidence mutations reject |
| Repeated probes, redirects or encoded output consume unbounded resources | Denial of service | independent cumulative egress, denial, action and elapsed-time ceilings; zero redirects | dimension-removal, redirect and over-ceiling mutations reject |
| Work cell converts context, a proposal or event into execution | Elevation of privilege | inert context; proposal-only egress; events require fresh read; commands are separately authorized | context-execution, event-truth, GraphQL-command and broker-confirm mutations reject |
| Reusable credential or repository authority persists after compromise | Elevation / persistence | no work-cell lease/credential; no repository or CI credential; external revocation invalidates generation authority | lease-visible, reusable-credential and repository-credential mutations reject |
| Provider failure silently changes the required intelligence | Integrity / availability confusion | explicit `intelligence_unavailable`; no silent or deterministic-equivalent fallback | fallback mutation rejects |

## Security requirements frozen by AES-C0

- Only `provider_inference`, `authoritative_read` and
  `inert_tool_adapter` may be represented as future leaseable classes.
- A work cell receives neither `CapabilityLease` nor reusable credential.
- Destination, method, media type, audience and cleanup identity are
  broker-resolved and candidate-inexpressible.
- Generic network, filesystem, SQL/database, shell/process, metadata,
  repository/CI write, provider tools, runtime control and product commands are
  always denied.
- Every positive budget is cumulative and stops before a following operation;
  product mutations, command confirmations and redirects remain at zero.
- Revocation is externally owned, generation-wide and model-independent.
- Evidence contains only closed reason codes, cumulative counts and digests and
  explicitly contains no sensitive values.
- Supply-chain identities are SHA-256 bound and rechecked before generation and
  broker admission.

## Assumptions and limits

AES-C0 assumes a future backend authority kernel, proofreader, broker, adapter
and external stop control correctly implement the accepted contract. That is
not yet proven. JSON Schema closure cannot by itself provide process isolation,
network policy, credential custody, atomic revocation or trustworthy telemetry.

The 37 hostile mutations are a finite contract-level set. They do not exhaust
parser differentials, side channels, kernel/container vulnerabilities,
supply-chain compromise, confused-deputy behavior in adapters, distributed
races or operational incident-response failures.

## Residual risks and later gates

- broker or adapter implementation defects;
- runtime/kernel/container escape and covert channels;
- stale authority between deterministic checks and adapter use;
- compromised pinned artifacts or signing infrastructure;
- incomplete cross-process budget atomicity or revocation propagation; and
- operator failure to quarantine or rotate a genuinely exposed credential.

AES-C1 may test provider-free admission and cross-record binding only. Runtime
broker simulation, hostile isolation rehearsal, occupied provider use and
product-context admission remain separate later descendants. Any work cell
that can reach metadata, receive a reusable credential, select an executable or
destination, exceed cumulative ceilings, invoke a command or influence the
kill switch must fail closed.
