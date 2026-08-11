# Raisa AES-C0 architecture contract closeout

Date: 2026-08-11

Result: `raisa_agent_execution_surface_containment_gate_aes_c0_architecture_pass`

Source baseline: `01d355f42df5981341196f3aa0caec2cccce7a2d`

## Accepted result

AES-C0 passes as the unmounted, provider-free architecture contract for
Raisa's Agent Execution Surface. It converts the accepted containment direction
into six closed message types:

- `GenerationManifest`;
- `CapabilityLease`;
- `BudgetState`;
- `BrokerDecision`;
- `RevocationRecord`; and
- `AuditEvidenceEnvelope`.

Together they bind one Bureau generation to one purpose, one work cell, exact
broker-resolved capabilities, independently cumulative budgets, immutable
supply-chain identities, externally owned revocation and minimized evidence.
The work cell receives neither a lease nor credential and cannot choose its
adapter, destination, method, executable, SQL, filesystem path, command route
or cleanup target.

The only future leaseable classes are `provider_inference`,
`authoritative_read` and `inert_tool_adapter`. Typed proposal egress remains
non-executable. Generic network, filesystem, database/SQL, shell/process,
metadata, repository/CI write, provider-executed tools, runtime control,
product commands and credential enumeration are always denied.

## API and product boundary

The API Steward pass confirms that AES-C0 preserves the mixed API Spine:

- GraphQL remains read-only and cannot become a command or provider tunnel;
- committed events remain signals for fresh authorized reads, not current truth
  or capability evidence;
- Access AI provider invocation remains a future backend-brokered operation;
  and
- any mutation remains on a separately authorized single-purpose REST/OpenAPI
  command with current authorization, a human/policy gate, idempotency, audit
  and deterministic readback.

Provider failure is explicitly `intelligence_unavailable`. Ordinary manual
controls may remain usable, but neither another provider nor a deterministic
substitute may silently imitate required model intelligence.

## Deterministic evidence

- the canonical authored-synthetic packet validates with zero errors;
- all six message definitions are closed JSON Schema objects;
- all 37 independent hostile mutations fail closed;
- the focused AES-C0 plus API Spine packet passes 45/45 tests;
- the maintained `--noconftest` CI-static packet passes 105/105 tests;
- the canonical fast profile passes 111/111 tests, Ruff, in-memory compilation
  of 202 maintained Python files without protected-path enumeration, Diary
  JavaScript syntax and Git whitespace; and
- the preacceptance Ariadne receipt passes from all five required sources.

The evidence is `authored_synthetic_provider_free`: zero provider calls, zero
runtime starts and no patient or product data.

## Issues exposed and resolved

Review found that a zero budget ceiling was initially interpreted as an already
exhausted positive allowance. The validator now treats zero as a disabled
capability while still rejecting any observation above zero; a reached positive
ceiling remains terminal before the next operation.

The first preacceptance receipt attempt used a non-profile continuation label
and omitted three declared synthetic adapter observations. It failed closed,
was not accepted, and was regenerated under the approved
`pre_verifier_acceptance` event with all declared adapters. The accepted receipt
then passed with the exact five rehydration sources.

One replacement character in the newly drafted plan was also removed by
rewriting the file as valid UTF-8 text.

## Claim boundary

AES-C0 proves a coherent, closed and mechanically hostile-tested authority
grammar. It does not implement or prove a broker, work-cell isolation,
container/kernel security, adapter correctness, provider behavior, credential
custody, atomic distributed budgets/revocation, product-data safety, clinical
safety, deployment, production or release readiness.

No protected evidence, historical Diary PHI, patient/clinical/product data,
licensed content, provider, credential, IAM, metadata, network, database/source,
migration, watcher/listener, executable tool, command/write, deployment,
production, release, Pages or protected ref was opened or moved. The user-owned
`docs/branding/` directory and all unrelated untracked files were preserved and
excluded.

## Programme handoff and explicit pause

AES-C1 provider-free admission rehearsal is the next safe planned descendant.
It may instantiate and challenge this exact contract with authored-synthetic
objects only; it cannot add a real runtime broker, adapter, provider call,
product read, tool or command.

Yuri explicitly requested a fresh task-window pause at this tranche boundary.
That pause is a context handoff, not a decision or authority gate. The next task
should perform complete five-source rehydration at the published task HEAD,
generate a fresh receipt, freeze the narrow AES-C1 plan and continue under the
existing standing uninterrupted-development authority.
