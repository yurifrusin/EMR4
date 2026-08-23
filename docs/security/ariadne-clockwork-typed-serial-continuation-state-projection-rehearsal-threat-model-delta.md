# Governance clockwork typed serial-continuation state projection rehearsal — threat-model delta

Date: 2026-08-23

Timestamp: 2026-08-23T19:41:32.8076827+10:00 (Australia/Brisbane)

Status: `frozen`

## Scope

This delta covers one compact, provider-free, serial-only input path in the
existing orchestrator preflight. It changes no requirements settings, provider
transport, worker process, product source, database, credential, network,
runtime, deployment, Pages or protected ref.

## Threats and controls

| Threat | Control |
|---|---|
| Compact input silently drops a hard safety field | Materialize the complete existing runtime-state schema and pass it through the unchanged receipt validator; compare all safety-relevant receipt projections with an equivalent manual state. |
| The preset invents an empty worker pool | Name the preset `observed_empty_workers`; make its selection the explicit typed assertion; forbid worker dispatch and all positive work dispositions through this interface. |
| Unknown transport is mistaken for reachable | Derive every unprobed external adapter as `unknown`, never `reachable`; the rehearsal makes no Harness/provider qualification claim. |
| A free-form lane rationale reintroduces vocabulary lapses | Accept only closed lane IDs and decision codes; derive dispositions, leverage and distinct rationale text from the registry. |
| Caller repeats or mistypes the active latch | Load and validate the canonical latch at invocation; accept no latch field in the compact intent. |
| Caller embeds a short or full Git ID in prose | Derive Git-ref evidence as a fixed machine-snapshot marker and use the existing full-object latch resolution; accept no Git field in the intent. |
| Evidence paths escape the repository or touch arbitrary local files | Require unique relative files under admitted documentation/orchestration roots; reject absolute paths, backslashes, dot traversal, directories and absence before materialization. |
| Settings drift is hidden by projection | Read the same requirements/adapters/worker-pool inputs and preserve the existing latch/settings-fingerprint mismatch guard. |
| A serial preset is reused for occupied dispatch | Reject `pre_worker_dispatch`, non-empty workspace/agent state and `planned`, `dispatched` or `completed` lane outcomes; retain legacy runtime-state input for non-serial work. |
| Generated runtime state becomes a third durable form | Keep expansion in memory and write only the compact intent plus the existing receipt. |
| Efficacy is claimed from a smaller fixture rather than real use | Generate later tranche continuation receipts from the compact current-tranche intent and compare their actual pair measurements with the manual preplanning pair. |

## Claim boundary

The rehearsal can prove typed form reduction with unchanged serial receipt
safety. It cannot prove live worker absence, occupied transport reliability,
provider suitability, reduced test cadence, product correctness, production
readiness or protected integration safety.
