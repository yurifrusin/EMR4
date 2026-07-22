# Threat Model Delta - Ariadne Bounded Cognitive Work Cell and Proofreader Gate

Date: 2026-07-23

Scope: repository-local, authored-synthetic, non-executing protocol only

## Boundary statement

This delta covers an inert protocol document, pure standard-library verifier,
compiled dry-run manifests and deterministic tests. There is no model,
provider, real container, database, event feed, product API, live mailbox,
human-gate UI or command connection. All identifiers are opaque authored-
synthetic references and all manifests are default-deny.

The trust boundary is the deterministic egress proofreader. Draft work-cell
frames are untrusted even when structurally typed. Only a verified or explicitly
repaired derived frame may reach a declared downstream or human-gate edge.

## Assets and invariants

- practice and principal isolation;
- exact bounded context and freshness revision;
- immutable original drafts, attempts, verdicts and repairs;
- no authority amplification from interpretation to fact or command;
- exact referential grounding for patient, practitioner and slot references;
- atomic consistency for coupled UX and human-review frames;
- bounded retry without hidden loops;
- forward-only fresh-context supersession;
- human-gate role and action limits; and
- non-executing, source-hashed manifest evidence.

## Threats and deterministic mitigations

| Threat | Failure mode | Required mitigation |
|---|---|---|
| Topology-isolation confusion | Every leaf is treated as a container or an interior agent node escapes isolation policy | Node role, topological role, execution class, agent eligibility and container posture are separate typed fields |
| Premature container proliferation | Empty containers expand identities, network surfaces and operating complexity | Deterministic nodes declare no container; agent eligibility does not start one |
| Silent future agentisation | Deterministic code is replaced by an agent under unchanged authority | New implementation generation, higher policy revision and fresh authorization are mandatory |
| Schema-shaped fabrication | A valid field carries an invented patient, practitioner or slot | Proofreader requires exact membership in authorised input-frame reference sets |
| Authority laundering | A candidate claims verification, confirmation, write or command power | Authority ceiling and forbidden-action checks produce immediate `authority_reject` and edge abortion |
| Stale fact laundering | Old context revision is presented as current | Exact context revision and freshness checks produce `stale_context_reject`; repair is forbidden |
| Repair becomes reasoning | The verifier guesses a missing reference or resolves ambiguity | Repair allowlist contains only stable sort and deduplication of opaque references |
| Original evidence rewrite | A repaired result hides the draft that caused it | Original and repaired hashes plus exact repair rules are retained in an immutable receipt |
| Cross-output inconsistency | UX and human-review packets identify different slots or subjects | Declared atomic groups are verified together before any grouped edge releases |
| Partial atomic release | One member of a failed output group reaches a consumer | Group failure suppresses every member release while audit/control evidence remains |
| Retry loop | Repeated model failures consume unbounded resources or hide instability | Fixed per-reason retry budget; reaching it aborts only the affected edge |
| Retry feedback injection | Error feedback expands context or smuggles draft content | Correction frames carry allowlisted reason codes and coordinates only |
| Retry mutates history | A new attempt overwrites the rejected attempt | Every retry is a later immutable attempt with exact `retry_of` lineage |
| Fresh-read grant laundering | A descriptor is treated as returned data or action authority | Grants require `execution_enabled: false`, `returns_data: false`, exact scope and expiry |
| Stale completion resurrection | An earlier generation completes after supersession | Supersession trace requires explicit stale-completion rejection |
| Human gate as bypass | Human routing rehabilitates a rejected or out-of-scope frame | Only passed or safely repaired frame types are accepted; rejected frames have no gate route |
| Human approval as command | Gate action directly mutates an appointment | Gate declares `command_authority: false`; any future approval is evidence requiring separate backend revalidation |
| Advisory-to-authority flow | Unverifiable explanation feeds a calculation or command | Advisory authority class routes only to a human surface and is excluded from authoritative ports |
| Sensitive-context aggregation | A coarse work cell accumulates contexts with different purposes | Split triggers require a new node at practice, principal, sensitivity, purpose or authority changes |
| Output smuggling | Undeclared properties carry secrets, prompts, content or connection details | Exact per-port payload allowlists plus recursive forbidden-key/value inspection fail closed |
| Diagnostic echo | A caller supplies an arbitrary document whose identifiers or rejection values reach terminal logs | Public trace output contains fixed protocol labels and aggregate counts only; document identifiers, values and rejection details are not emitted |
| Manifest execution | A dry-run declaration is interpreted as runnable configuration | Source hash, `dry_run: true`, `execution_enabled: false`, no adapter/endpoint/image/command and static tests |
| Evidence overclaim | Synthetic proof is described as live model/container/product behavior | Exact evidence label and explicit closed-connection inventory are required |

## Proofreader limitations

The proofreader proves contract conformance, grounding against supplied frames,
freshness, authority and declared consistency. It does not prove that an
interpretation is optimal, that advisory language is clinically correct, or
that a future runtime enforces the manifest. Unverifiable content may be
represented only as explicitly advisory material routed to a human gate.

## Residual risks deferred to later authority

- model prompt injection and model-specific behavior;
- container escape, network policy and workload identity;
- live authorization and product context sourcing;
- PHI minimisation and purpose limitation with real data;
- durable queues, concurrency, retries, dead letters and retention;
- human-gate usability, coercion, role authentication and signed decisions;
- backend command revalidation and idempotency; and
- production observability, RLS, encryption and incident response.

No residual risk here authorises a runtime implementation.
