# Threat Model Delta - Ariadne Bounded Agent-Admission Design

Date: 2026-07-23

Scope: provider-neutral, repository-local, authored-synthetic and non-executing

## Boundary statement

This delta covers an inert protocol document, a pure standard-library
validator, source-hashed dry-run manifests and deterministic negative cases.
There is no model, provider, prompt transmission, model mount, container run,
network, secret, database, event feed, product API, live mailbox, human UI or
command connection.

The new trust boundary is the proposed admission envelope between a bounded
context assembler and an unoccupied cognition adapter. A structurally valid
envelope remains non-executable and grants no authority.

## Assets and invariants

- instruction-plane policy is independent from evidence-plane content;
- exact practice, principal, purpose, correlation and context revision;
- minimal, allowlisted, source-labelled and freshness-bound context;
- no secret or ambient capability exposure;
- model-independent byte/frame/draft/attempt caps;
- no guessed token authority before model/tokenizer selection;
- terminal cancellation, expiry and supersession;
- draft-only output through the accepted deterministic proofreader; and
- accurate non-executing evidence labels.

## Threats and deterministic mitigations

| Threat | Failure mode | Required mitigation |
|---|---|---|
| Design-valid becomes execution grant | A runtime treats schema conformance as permission to invoke | Every envelope and manifest fixes `execution_enabled: false`; decision vocabulary is `design_valid`, never `admit` or `run` |
| Transport selection laundering | A provider or local server is implied by optional fields | All topology candidates are explicit, unselected and unconfigured; model/provider/endpoint fields are null or absent |
| Local-equals-safe assumption | A local model bypasses provenance, licence, device or resource review | Catalogue local risks explicitly and require fresh topology authority and generation |
| Prompt injection through evidence | User/fact text instructs the adapter to ignore policy or add capabilities | Immutable control plane is separately hashed; evidence is typed data and cannot modify policy, ports, transport or capability fields |
| Task instruction becomes authority | A natural-language request claims approval or asks for a command | User request is a task frame only; output authority remains draft and command/approval types are forbidden |
| Cross-practice aggregation | Frames from another practice enter one context | Exact envelope/frame practice and principal equality; mismatch fails closed |
| Purpose drift | Context gathered for one task is reused for another | Exact purpose binding on envelope and every frame |
| Stale fact use | An old availability or policy frame reaches cognition | Exact revision and freshness interval checks; stale attempt requires new superseding context |
| Context smuggling | Unknown fields/types carry clinical text, secrets or connection data | Per-frame type/payload allowlists, sensitivity allowlist and recursive forbidden-key inspection |
| Oversized context | Excess input causes denial, truncation or hidden loss | Canonical frame-count and byte caps are checked before any future adapter |
| False token precision | An arbitrary token cap is accepted without a model/tokenizer | Token value must remain null and unresolved until a concrete model decision |
| Capability emergence | Model/provider convention exposes tools, files, network or product APIs | Empty tools/secrets and false capability matrix; any true/unknown capability rejects the envelope |
| Secret exposure | Provider or model credentials appear in context or manifest | No secret fields, secret references, environment inheritance or endpoint configuration; forbidden-key scan |
| Cancellation race | A late result is verified or released after cancellation | Cancellation/expiry/supersession are terminal and late result is rejected before proofreader entry |
| Proofreader bypass | Generated content routes directly downstream or to a human | Exact egress destination is the accepted proofreader only; all other routes reject |
| Authority-shaped output | A draft claims verified fact, approval or command status | Exact accepted draft port/type/authority allowlist; false authority rejects before egress |
| Raw-content logging | Prompts, output, identifiers or hidden reasoning leak into evidence | CLI and committed evidence contain only hashes, fixed codes and counts |
| Model-specific safety overclaim | Structural cases are described as proving prompt resistance | Closeout distinguishes protocol separation from future model-specific adversarial testing |
| Manifest execution | Dry-run JSON becomes an actuator | Source hashes, default deny, `execution_enabled: false`, no endpoints/images/commands and static import/CLI tests |

## Transport-specific deferred threats

An in-cell local model would add model supply chain, weights/image integrity,
licence, device, memory and container-escape questions. A host-local broker
would add IPC authentication, host trust, multiplexing and cancellation. A
remote provider would add network egress, workload identity or secrets,
jurisdiction, contractual processing, cost, retention and availability.

None is opened or resolved by this design.

## Residual risks and closed gates

Model behaviour, tokenizer accounting, prompt-injection resilience, output
quality, container isolation with a real model, live authorization, PHI
minimisation, durable concurrency, human decision quality, backend revalidation
and production operations remain unproved. No residual risk authorises model,
provider, container, product or command execution.
