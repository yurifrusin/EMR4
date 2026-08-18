# Threat-model delta — provider-free shadow Ariadne / DeepSeek broker gear architecture

Date: 2026-08-19

Timestamp: 2026-08-19T05:20:02.5485051+10:00 (Australia/Brisbane)

Status: `frozen_shadow_architecture`

Source HEAD: `a29e99c2fbfca59a24c348ded49dd29352b72aa3`

## Scope

This delta covers only the typed causal tick/result architecture, the single-
writer lease between Ariadne and the DeepSeek broker, profile/preset identity
binding, exhaustive terminal receipts, atomic shadow projections and efficacy
measure definitions. It opens no provider, product, data, credential, runtime,
deployment or protected-ref surface.

The accepted transactional closeout engine and provider-free WorkOrder broker
remain read-only predecessor evidence. No live process consumes the new
architecture in this tranche.

## Assets and trust boundaries

Protected assets are:

- exact full Git/ref identity and accepted lineage;
- configured stage/disposition and side-effect policy;
- materialized evidence identity and immutable event history;
- attempt uniqueness, terminality and unknown-commit no-retry;
- single-writer causal order and broker parent/result binding;
- package/profile/preset/tool and authority ceilings;
- canonical Continuity, Compass, latch, register and report projections;
- raw prompts, reasoning, secrets, product data and user-owned untracked files;
  and
- honest efficacy numerators, denominators, exclusions and zero-escape claims.

New trust boundaries are source-readers-to-tick-reducer, Ariadne-to-WorkOrder,
WorkOrder-to-broker lease, broker-result-to-Ariadne acknowledgement and
acknowledged-journal-to-shadow-projections.

## Threats and mandatory controls

| ID | Threat | Mandatory control |
|---|---|---|
| CG-001 | A short, stale or hand-copied Git ID enters a receipt or WorkOrder. | Fixed snapshot plus strict resolver derive one lowercase 40-character object; caller Git fields are forbidden. |
| CG-002 | Stage, disposition or effect class is remembered differently in two artifacts. | Derive each from the validated latch and immutable stage catalogue; exact closed enums and digest binding. |
| CG-003 | A future/nonexistent evidence path is treated as current proof. | Admit only registry entries whose file, canonical digest and creation tick already validate at the parent tick. |
| CG-004 | Two writers advance the journal or one side skips the other. | One sequence lease; WorkOrder transfers it to the broker and only acknowledged terminal result returns it to Ariadne. |
| CG-005 | Replay, gap, stale parent or altered event creates a false causal history. | Contiguous unique sequence, exact parent digest, canonical event digest and operation/attempt ownership on every tick. |
| CG-006 | Broker terminal output is omitted, duplicated or followed by more work. | Exactly one closed terminal result per attempt; post-terminal broker events and duplicate terminals reject. |
| CG-007 | Ariadne projects success before independently validating the broker result. | No downstream tick or projection until one acknowledgement binds the exact terminal event and result-envelope digests. |
| CG-008 | Unknown commit is interpreted as failure-safe retry or success. | No success release, bounded identity readback required, no automatic retry; recovery derives a new attempt ordinal. |
| CG-009 | A permission preset or versatile Harness feature silently broadens authority. | Stage catalogue allowlists exact package/profile/preset/tool digests; presets configure capability but confer no authority. |
| CG-010 | WorkOrder drift changes source, paths, tools, model route, fallback or provider posture. | Whole-WorkOrder digest supplied independently; exact source/authority/owned/forbidden/tool/profile bindings fail before simulated upstream I/O. |
| CG-011 | Clock metadata leaks prompts, reasoning, secrets or product payload. | Identifiers, counts and digests only; result envelope forbids raw content and self-acceptance. |
| CG-012 | A read-only verifier executes a generator. | Effect classifier binds every command before dispatch; generative command under `read_only` rejects. |
| CG-013 | One projection publishes before another validates. | Reduce and validate every view at one acknowledged journal tip, stage privately and publish one shadow generation atomically. |
| CG-014 | Mutable current-state literals create recurring stale tests. | Current projections validate schema/state invariants; exact operation facts bind only immutable event receipts. |
| CG-015 | Incident peer linkage is confused with recurrence. | Peer links derive only within exact attempt identity; recurrence derives separately from the full recurrence signature. |
| CG-016 | New bureaucracy claims efficiency by hiding shared-engine cost or counting expected tests as reruns. | Frozen definitions, source-derived totals, explicit exclusions, raw growth and clean-run overhead; timing cannot decide acceptance. |
| CG-017 | An escaped defect is relabeled as a rejected test case. | Seed inventory is frozen before execution; any breach reaching publication, dispatch or acknowledgement counts as an escape. |
| CG-018 | The shared clock is treated as product, provider, Git or financial authority. | Clock proves causal provenance only. Existing product/provider/Git policies and Yuri's prepaid balance remain separate controlling boundaries. |

## Abuse and failure cases

Deterministic validation must cover unknown keys, supplied derived fields,
seven-character Git, unresolved full Git, wrong settings fingerprint, stale
latch, unconfigured stage/disposition/effect, missing evidence, digest drift,
duplicate attempt ordinal, sequence gaps, replay, concurrent writers, wrong
lease owner, stale WorkOrder parent, wrong package/profile/preset/tool set,
result-before-start, duplicate terminal, broker-after-terminal,
acknowledgement-before-terminal, unacknowledged projection, future evidence,
peer/recurrence confusion, caller-supplied metrics, hidden shared-engine cost,
weakened coverage and partial shadow publication.

No failure may start the native Harness, call a provider, mutate a credential,
write a live authority projection, import product code, touch a route/database,
perform Git writes or access protected evidence.

## Provider, preset and monetary posture

DeepSeek native-Harness package and preset identities are represented only as
digests in authored-synthetic contracts. The unresolved stock-headless HMR
prerequisite remains blocking for occupied EMR4 work. No provider key, broker
token, prompt or external request is used.

Yuri's provider prepayment remains the financial ceiling; lack of a Harness-
native budget is not a defect. This architecture records provider-call and
token observations when future authority exists, but those measurements grant
neither call nor spend authority.

## Residual risk and closed authority

An architecture and provider-free validator cannot prove crash-atomic migration
of independently addressed live files, Windows/process failure behavior,
occupied Harness startup, model completion reliability, provider availability
or lower real-work rerun frequency. Those require later separately frozen
shadow and adoption gates.

No live clock adoption, current-control retirement, occupied DeepSeek/provider
call, HMR retry, product/configuration/API/route/database/client change,
ordinary-practice enablement, product/patient/clinical data, production runtime,
deployment, release, Pages or protected-ref movement is authorized.
