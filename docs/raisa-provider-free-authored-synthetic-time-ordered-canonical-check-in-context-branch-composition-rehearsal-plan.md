# Raisa provider-free authored-synthetic time-ordered canonical check-in-context branch composition rehearsal plan

Date: 2026-08-24

Timestamp: 2026-08-24T15:55:06.2330342+10:00 (Australia/Brisbane)

Status: `frozen_narrow_provider_free_plan`

Operation: `raisa-provider-free-authored-synthetic-time-ordered-canonical-check-in-context-branch-composition-rehearsal`

## Objective

Rehearse the smallest complete pairwise set of authored-synthetic, time-ordered
check-in context changes across the three accepted axis families. Exercise only
the unchanged unmounted canonical check-in adapter through injected in-memory
dependencies. Record each scenario's initial state, intervening change,
adapter result, callback ordering and readback disposition.

This tranche tests composition and precedence already present in the adapter.
It does not add a check-in rule, infer a historical frequency or reopen the
historical diary trove.

## Authority and exact baseline

- The five authoritative rehydration sources are
  `live_handover_current_baton`, `current_authority_allocation`,
  `active_plan_and_acceptance`, `protected_evidence_boundaries` and
  `git_refs_and_worktree`.
- The fresh preplanning receipt passes and the active-operation latch remains
  `in_progress` for this operation.
- The exact task-branch planning baseline is
  `d9114b3e9a72fa94acc0a7ab3657f17043c6be0a`.
- The accepted predecessor review source is
  `0f6c091935f172351972f349db8cc5c1ec72d5dc`.
- The frozen successor-axis contract has SHA-256
  `dc74a5373a670aca52f804436e33be70a10d60ac96dd46508a58b09fd2ca778f`.
- The unchanged adapter has Git blob
  `6955dec2e31e14c0ae4847acba22f9fb0087715b`; its accepted focused test has
  Git blob `97bcfc3725f4df9495333779c75c41d798eeae87`.
- Local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Frozen pairwise design

The factors have 5, 4 and 6 values. Every source/waiting-area value must meet
every idempotency/outcome value, so any pairwise design needs at least
`5 * 6 = 30` cases. The frozen contract uses exactly one cell for each such
pair. Its 5-by-6 matrix selects one authority/evidence/freshness value per
cell, and every matrix row and column contains all four values. It therefore
covers all:

- 20 source/waiting-area × authority/evidence/freshness pairs;
- 30 source/waiting-area × idempotency/outcome pairs; and
- 24 authority/evidence/freshness × idempotency/outcome pairs.

All 74 required cross-family pairs are covered in 30 cases. The 120-case full
cross-product is neither required nor authorised.

## Time-ordered scenario contract

Every scenario has these typed phases:

1. create a patient-free authored-synthetic appointment, Receptionist,
   waiting-area topology, confirmation proposal and opaque synthetic evidence;
2. freeze the proposal freshness against the declared initial appointment;
3. apply the declared synthetic intervening appointment, topology, authority,
   evidence or idempotency-ledger change;
4. invoke the unchanged unmounted adapter exactly once for the observed action
   (an exact-replay case may first create its own isolated stored success);
5. compare the typed result, callback prefix, commit/rollback counts and
   readback disposition with the frozen expectation; and
6. emit only patient-free structural evidence.

The adapter's current fail-closed precedence remains authoritative:

1. exact replay or idempotency stop before appointment locking;
2. locked appointment scope/source-state validation;
3. current Receptionist reauthorisation;
4. proposal freshness;
5. signed evidence;
6. waiting-area topology;
7. precommit composition and rollback;
8. commit-outcome unknown; and
9. committed-readback unavailable.

An axis may be present but masked by an earlier stop. The contract separately
names unmasked witness cells so every axis value and each idempotency outcome
has at least one causally observed example. `conflict_or_in_progress` must
include both exact submodes across its five cells.

## Implementation boundary

The tranche may add only:

1. one frozen JSON scenario contract under this operation's Continuity folder;
2. one deterministic provider-free in-memory rehearsal script;
3. one focused test file covering exact bindings, pairwise minimality,
   unmasked witnesses, result/readback truth, patient-free output and hostile
   contract mutation; and
4. generated evidence/report, acceptance and closeout records.

`app/services/appointment_check_in_product_adapter.py`, routers, schemas,
database code, migrations, API Spine contracts, clients, configuration and all
existing product tests remain byte-identical.

## Parallelism assessment

- DeepSeek: declined, negative leverage. Its native lane remains paused, and
  the 30-case matrix, dependency simulator, result expectations and evidence
  are one tightly coupled deterministic package. Reassess only if a separable
  mechanical repair appears after a deterministic failure.
- Gemini: not applicable, neutral leverage. The adapter is unchanged and the
  closed matrix plus exact assertions can supply the complete verdict. Reassess
  before any independent verifier if evidence conflicts or a semantic claim
  exceeds the frozen contract.
- Native subagents: declined, negative leverage. There is no independent write
  package that would save more than its briefing and reconciliation cost.
- GPT Sol owns the serial plan, implementation, verification and acceptance.

## Acceptance

- All Git IDs are lowercase full 40-character object IDs and all file bindings
  are exact.
- Exactly 30 scenarios cover all 74 cross-family pairs; removing any scenario
  loses its unique source/waiting-area × idempotency/outcome pair.
- Every scenario declares initial state, intervening change, expected adapter
  result, expected callback boundary and readback disposition.
- Every axis value has an unmasked witness, and the grouped idempotency value
  exercises both `conflict` and `in_progress`.
- Replay returns only an exact stored patient-free success before lock;
  precommit failure rolls back; commit and readback failures never release a
  false success.
- Generated evidence is patient-free and contains no evidence token, raw
  idempotency key, patient identifier, reason, note or name.
- Focused tests, the accepted adapter suite, relevant API Spine/governance
  checks, Ruff, compileall and `git diff --check` pass.
- No historical or `local_data` access, provider/model/network call, product
  change, database, route, client, configuration, ordinary-practice activation,
  production, deployment, release, Pages, protected evidence or protected-ref
  movement occurs.
- `docs/branding/` and every unrelated untracked file remain preserved and
  staging uses explicit paths only.

## Stop conditions

Return `revision_required` if an exact binding, closed axis value, 30-case
minimality proof, unmasked witness, precedence expectation, patient-free output
or protected boundary differs. Return `blocked` if success would require
historical data, product modification, provider/runtime access or a weakened
assertion. Do not expand the matrix or change adapter behavior to make the
rehearsal pass.

