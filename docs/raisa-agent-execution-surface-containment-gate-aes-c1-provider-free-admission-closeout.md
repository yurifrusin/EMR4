# Raisa AES-C1 provider-free admission rehearsal closeout

Date: 2026-08-11

Result: `raisa_agent_execution_surface_containment_gate_aes_c1_provider_free_admission_pass`

Reviewed source HEAD: `285e60216cf22907e8a0f5596ece11f74f455c81`

## Accepted result

AES-C1 passes as an authored-synthetic, provider-free and unmounted admission
rehearsal against the exact accepted AES-C0 contract. Its pure evaluator admits
an inert operation only when the manifest grant, broker-side lease, immutable
generation, current authority, proofreader result and every cumulative budget
counter intersect exactly at the evaluation time.

The exact 45-scenario registry resolves as two inert `allow` decisions, 25
default-denial decisions and 18 terminal `stop` decisions. The paired denial-
ceiling scenario first returns `deny` with an exhausted after-state; its
following attempt then returns `stop`. No admitted operation is executed.

Revocation, external kill, supersession, manifest-content or supply-chain
identity mismatch, stale authority and invalid time bounds outrank an otherwise
valid grant. Candidate content cannot select a capability, adapter, destination,
method, URL, source, executable, credential, SQL, filesystem path, command route
or cleanup target. All 19 independent AES-C0 cumulative counters are checked
prospectively; a zero ceiling disables only an operation that consumes that
counter, while a reached positive ceiling blocks the next operation.

## Exact inherited boundary

AES-C1 verifies and consumes, without changing, these accepted AES-C0 digests:

- architecture contract: `403c7ddac2399760395d60a8094ffe42d2519a4a809bc8a59104acd2883eb9ae`;
- contract schema: `344d88c59a5d781ebb205de575b66f2e3d64f3878f73c9c0bf4d86eb996b1740`; and
- authored-synthetic examples: `f77801d2d752ca2daeed1b3116d78a965441bc1996f6b6da60eccf72fbee9f3e`.

The eleven AES-C0 broker reason codes and six closed message shapes remain
unchanged. Each decision emits an exact `BrokerDecision` and minimized
`AuditEvidenceEnvelope` containing closed identifiers, decisions, reason codes,
cumulative counts and digests, never prompt, reasoning, credential, exception,
patient or product values.

## API Spine boundary

The API Steward classification remains unchanged. GraphQL is read-only and was
not invoked. Committed events remain signals for fresh authorized reads and
were not consumed. Provider invocation remains a future backend-brokered Access
AI operation. Mutations remain separately authorized, human/policy-gated,
idempotent and audited REST/OpenAPI commands. Provider failure remains explicit
`intelligence_unavailable`; AES-C1 adds no fallback or command path.

## Deterministic and independent evidence

- all 45 canonical scenarios match their exact decision and reason registry;
- all 24 generated hostile attempt mutations reject with zero admission;
- all eight hostile contract mutations reject with zero admission;
- the focused AES-C1/AES-C0/API packet passes 59/59 tests;
- the final maintained `--noconftest` static packet passes 129/129 tests;
- the canonical fast profile passes 135/135 tests, Ruff, compilation of 202
  maintained Python files, Diary JavaScript syntax and Git whitespace;
- the local Python 3.14 environment cannot truthfully run the separately
  version-pinned Python 3.11 `ci-correctness` profile, so that profile is not
  claimed; its maintained static test packet was run directly and passed; and
- the fresh Gemini 3.6 Flash/high exact-HEAD veto independently passes 73/73
  focused review tests, Ruff, whitespace and clean-worktree invariants.

Evidence mode is `authored_synthetic_provider_free_unmounted`: zero runtime
starts, provider calls, adapter executions, network, database/source, tool or
command operations, and no patient or product data.

## Issues exposed and resolved

The first blue candidate left nested contract rules and candidate proposal
fields open. The bounded DeepSeek revision closed both surfaces. Sol's
independent recovery then made inherited AES-C0 digest values exact constants,
not merely well-formed digest strings, and added a hostile mutation for an
existing digest value. A fresh Gemini veto found no remaining defect.

Three orchestration mistakes failed closed before affecting evidence or source:
the revision predispatch state omitted four declared adapters, a recovery state
used invalid receipt vocabulary, and a later draft inferred a full SHA from a
short SHA. They are recorded as AER-0239 through AER-0241 at register revision
207. No worker or integration proceeded on a refused receipt.

## Claim and authority boundary

AES-C1 proves deterministic admission and terminal behavior over unmounted
authored-synthetic objects. It does not prove a broker process, adapter custody,
container or kernel isolation, runtime control-state provenance, atomic
distributed budgets/revocation, provider behavior, product-data safety,
command safety, deployment or production readiness.

No protected evidence, historical Diary PHI, patient/clinical/product data,
licensed content, provider, credential, IAM, metadata, network, database/source,
migration, watcher/listener, executable tool, command/write, deployment,
production, release, Pages or protected ref was opened or moved. User-owned
`docs/branding/` and all unrelated untracked files remain preserved and
excluded.

## Next planned descendant

AES-C2 provider-free broker simulator is dependency-satisfied next work. It may
freeze and exercise exactly one inert allowlisted authored-synthetic adapter
with no external effect, proving that the work cell never receives a credential
or selects the destination, method or executable. AES-C1 grants no C2 runtime,
adapter, provider, data, tool or command authority; C2 requires its own fresh
five-source rehydration, receipt and narrow fail-closed plan.
