# Ariadne Clockwork Correction

Status: G0 preservation and correction direction
Prepared: 2026-08-25T16:21:42+10:00

## Preserved implementation fact

The latest local clockwork is a real tracked implementation, not a narrative
placeholder. Its frozen Git base is
`03e6860394c39086ec1ffb3f2457acc5f7c8b5f9`, on source branch
`codex/ariadne-bernie-davida-parallel-seam`, already aligned with its remote when
G0 began. It contains the single-writer governance clockwork, typed transition,
closeout, active-operation, risk-weighted and transactional machinery.

G0 preserves that exact state on:

- `refs/heads/safety/ariadne-clockwork-pre-g0-20260825`;
- a verified complete local Git bundle; and
- a separate archive of all 683 pre-existing untracked files.

The recovery branch starts at the frozen clockwork base. Protected master and the
handoff baton remain unchanged at
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Diagnosis boundary

The current clockwork has substantial typed machinery, but the recovery
programme treats these controller-level risks as unresolved until their gates:

- review artifact validity can be confused with positive verdict or integration
  authority;
- verdict parsing can be duplicated or inconsistent;
- local tranche completion can outrank global convergence and global red gates;
- continuation lacks enforced finite cost, retry and wall-clock governance;
- no-progress and WIP limits are incomplete;
- reviewer independence can be asserted without machine-verifiable provenance;
- policy references and current aliases can drift; and
- narrative continuity can become larger or more authoritative than structured
  state.

G0 does not reconstruct or rewrite the clockwork. It freezes its actual source,
establishes one structured programme state and disables ordinary autonomous task
selection.

## Corrected target model

The target is a closed, journalled controller:

```text
DISCOVERED -> PLANNED -> DISPATCHED -> EXECUTING -> REVIEWING
     ^                                                   |
     |                                                   v
  QUARANTINED <- REVISION_REQUIRED <- ACCEPTANCE_DECISION
                                            |
                                            v
                                      INTEGRATION_READY
                                            |
                                            v
                                         CLOSED
```

Every transition must be validated against current state, exact candidate/base,
lease, policy version and evidence. The append-only journal is the source for
replay; narrative views are generated projections.

The controller's acceptance tuple is deliberately separate:

```text
artifact_valid
review_verdict
integration_authorized
```

Only an unambiguous positive verdict bound to the exact candidate, base, policy,
reviewer provenance and evidence can make integration eligible. A valid negative
review artifact remains useful evidence but never becomes process success.

## Escapement and governor

Later G1 tranches must enforce finite attempt, token, cost and wall-clock budgets;
no-progress detection; WIP and stack limits; global-red repair-only mode; stale
lease rejection; and structured stop reasons. Missing state or policy is a hard
stop, not a default.

## Independence

Reviewer identity, execution surface, context lineage, candidate SHA, base SHA,
policy version and evidence digest must be machine-checkable. The generating
worker cannot be the sole accepting reviewer. A claimed independent review with
unprovable provenance is `revision_required`.

## G0 fail-closed overlay

`orchestration/programme/current-state.json` is the machine-authoritative recovery
state. `orchestration/harness_settings/programme_recovery.yaml` declares the
overlay. `scripts/raisa_ariadne_recovery_preflight.py` is the read-only task
admission check. While `programme_mode` is `recovery` and `current_gate` is `G0`,
only `g0_recovery` inspection, preservation, policy, inventory, tests and review
are admitted. Feature, product, integration, provider and deployment work are
blocked.

## Deferred work

- G1A: verdict and integration semantics.
- G1B: persisted state machine and deterministic replay.
- G1C: escapement, governor and global objective.
- G1D: independent provenance.
- G1E: configuration integrity and kernel extraction boundaries.

No item in that list is implemented or started by G0.
