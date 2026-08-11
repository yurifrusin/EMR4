# Raisa AES-C0 architecture and contract plan

Date: 2026-08-11

Source HEAD: `01d355f42df5981341196f3aa0caec2cccce7a2d`

Status: `frozen_for_provider_free_architecture_execution`

## Purpose

Freeze the smallest deterministic authority contract that every later Agent
Execution Surface descendant must inherit. AES-C0 defines types, trust
boundaries and fail-closed invariants only. It creates no broker process,
container, provider adapter, route, credential, product read, tool or command.

This descendant consumes the accepted containment-gate direction, its threat-
model delta, the model-required/deterministic-authority Bureau doctrine, the
API Spine and the accepted codebase fitness repair at Continuity 236 / Compass
218.

## Selected boundary

AES-C0 will produce one closed architecture contract, one JSON Schema with
named message definitions and one authored-synthetic example packet. The
message definitions are:

1. `GenerationManifest` -- immutable generation, principal/purpose binding,
   exact leaseable capabilities, independent budgets, stop conditions and
   supply-chain identities;
2. `CapabilityLease` -- broker-side, audience-bound, generation-bound and
   revocable authority that is never exposed to the work cell;
3. `BudgetState` -- cumulative reasoning, information, egress, action, denial
   and elapsed-time accounting with terminal exhaustion;
4. `BrokerDecision` -- allow, deny or stop with current-authority, manifest,
   lease, proofreader and budget readback;
5. `RevocationRecord` -- externally owned generation-wide invalidation of
   leases, aliases, tokens and writable caches; and
6. `AuditEvidenceEnvelope` -- minimized counts, reason codes and digests with no
   raw prompt, reasoning, credential, patient/product value or unrestricted
   log.

The normative contract also freezes:

- the only leaseable classes: `provider_inference`, `authoritative_read` and
  `inert_tool_adapter`;
- proposal egress as typed proofreader input, not an execution capability;
- generic network, filesystem, database/SQL, shell/process, cloud metadata,
  repository/CI write, provider-executed tools, runtime control and every
  product command as non-leaseable;
- candidate-controlled values versus broker-resolved operation identity;
- GraphQL/query as read-only, events as signals, and REST/OpenAPI commands as a
  separate current-authority/human-confirmation/idempotency/audit/readback
  plane the broker and work cell cannot confirm;
- explicit `intelligence_unavailable` on provider failure, with no silent
  provider, model or deterministic-equivalent fallback; and
- externally owned stop/revoke/quarantine semantics.

## Owned files

- `docs/raisa-agent-execution-surface-containment-gate-aes-c0-plan.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c0-architecture.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c0-threat-model-delta.md`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/authored-synthetic-contract-examples.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c0_acceptance.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c0.py`
- exact tranche receipts, review, closeout, mailbox, Continuity/Compass updater
  and focused continuity tests if the architecture passes.

The two repair pre-push receipt/state files remain pre-existing untracked
evidence and are preserved but not adopted into AES-C0.

## Forbidden surfaces

- no protected-evidence enumeration, access, import, execution or inference;
- no historical Diary or local PHI access;
- no patient, clinical, product-derived, financial or licensed content;
- no provider/model call, credential, IAM, metadata, network or external
  retrieval;
- no runtime broker, container, work cell, adapter, route, listener, watcher,
  database, migration or persistence;
- no executable tool, filesystem, SQL, shell, process, command or write;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad Git staging or staging of `docs/branding/` or unrelated untracked
  files.

## Deterministic acceptance

AES-C0 passes only when:

1. the architecture contract and schema use exact closed keys and bind all six
   named message definitions;
2. every grant is one generation, one audience, one broker-resolved operation,
   one exact destination/method/media type and a bounded source/field set;
3. reasoning, information, egress, action, denial and time budgets are separate
   and cumulative; redirects are zero and the command/mutation budget is zero;
4. the work cell cannot receive a credential/lease, select an adapter,
   destination, method, URL, executable, SQL, path, tool definition, command or
   cleanup target;
5. context, Memory and candidate values remain inert data and cannot become
   templates, paths, URLs, serialized executable objects or policy;
6. GraphQL remains read-only, events remain signals and REST/OpenAPI command
   confirmation remains outside both work cell and broker;
7. provider failure yields explicit intelligent-capability unavailability with
   no silent or deterministic-equivalent fallback;
8. revocation invalidates all generation authority and the external kill
   switch cannot be influenced by model output;
9. audit/evidence is minimized and the forbidden sensitive-field vocabulary is
   exact;
10. at least twenty independent hostile contract mutations fail closed while
    the canonical authored-synthetic packet passes;
11. repository Ruff, focused static tests, the canonical fast profile and Git
    whitespace pass; and
12. tracked scope is exact, protected refs remain
    `2e34bdad732fdab32fbf778280b3d3c70d66d602`, and all unrelated untracked
    files remain preserved.

## Recovery and next work

An architectural contradiction is repaired only inside these message and
authority boundaries. Any required product/runtime opening, real data,
provider selection, credential action or competing user-owned containment
outcome stops AES-C0.

After acceptance, AES-C1 is the next planned candidate: a provider-free
admission rehearsal over authored-synthetic instances of this exact contract.
It cannot start until AES-C0 passes and it cannot add a real adapter, tool,
provider, product read or command. No user decision fork is present.
