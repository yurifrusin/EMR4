# Ariadne provider-free continuity journal and refinement-promotion plan

Date: 2026-08-15

Timestamp: 2026-08-15T17:27:59+10:00 (Australia/Brisbane)

Source HEAD: `ac638c45a3a1916162424cd42518764af39df7f7`

Status: `frozen_for_provider_free_harness_implementation`

Reasoning level: material workflow continuity and harness authority / Extra High

## Purpose

Implement the smallest useful Prime Agent-derived improvements in Ariadne's
development harness without importing Prime Agent, adding a daemon or changing
Raisa product runtime.

The tranche adds two pure deterministic boundaries:

1. an operation journal that distinguishes exact completed replay from
   in-progress, failed, revoked and explicitly uncertain outcomes across
   immutable generations; and
2. a quarantined refinement-promotion gate that lets a model or human propose a
   small harness lesson but never apply it without typed evidence and distinct
   promotion authority.

Unchanged failed deterministic gates are recognized by exact evidence and
command-manifest fingerprints and return `diagnose_without_rerun`. This reduces
ceremonial reruns without converting stale evidence into success.

## Source binding

The local source allowlist is:

| SHA-256 | File |
|---|---|
| `3db330a36ea75a6eab28ccb02c6b08e23bad1aaee87d0851ed2cb4e0269e08cc` | `orchestration/harness_settings/evidence_led_workflow.yaml` |
| `ced4821b7a4005263d19b360d1489d90884926a35dd9151ab1e75d63740f83e7` | `orchestration/harness_settings/autonomous_continuation.yaml` |
| `ab95380dde9315898ca92397422f0e80bfec464a8db11e87ccf2e181dfccd463` | `orchestration_harness/active_operation.py` |
| `c46326194c192779f05105bf79973660aa121a074878a6dbe4b12e8b00d6b2d9` | `orchestration_harness/orchestrator_preflight.py` |
| `1c7861e9a8b6a9c4be0c889a3f33eb440fed8831fc77dd3a0d575e2b0099bb60` | `scripts/ariadne_evidence_gate.py` |
| `d59cc2bcf2903f78753744b80ba3e00997a00dbd6d60ef413851940cb90fde3d` | `tests/test_ariadne_evidence_gate.py` |
| `0886b81c5f25d536a2d98ba47d73dbcb56b6f91a39dc94738670308acf801a65` | `tests/test_ariadne_active_operation_latch.py` |
| `b33eefa0e085f665b6d72442d731de5f1c0de45c7cbf1133df5217daa5355fc4` | `orchestration/continuity/ariadne-agent-error-register/agent-error-register.schema.json` |

Prime Agent is read-only design evidence at exact upstream commit
`97b994c3d7c45ca1ae635190e91e9e58ddf2577c`. Relevant files are
`packages/coding-agent/docs/agent-connection.md`, `docs/daemon.md`,
`docs/usage.md`, `docs/rlm.md`, `skills/refine/SKILL.md` and
`src/core/refinement/refinement.ts`. No upstream code is copied, installed or
executed.

## Existing Ariadne overlap

Ariadne already has the stronger authority controls: five-source receipts, an
active-operation latch, exact command manifests, deterministic evidence gates,
immutable failed evidence, independent veto and the agent-error register. This
tranche does not replace or weaken them.

The additive gaps are narrowly operational:

- no pure journal currently distinguishes a durable completed command from an
  acknowledged command whose terminal result is missing;
- no generation-plus-sequence cursor currently rejects retired-generation
  incremental events and selects a snapshot after recovery;
- the evidence gate does not yet suppress an unchanged failed gate; and
- error-register and policy changes are human-authored directly rather than
  entering through a reusable quarantined proposal/promotion contract.

## Frozen operation-journal contract

The journal is evidence about Ariadne development operations only. It executes
nothing and grants no command authority.

- `operation_id` and positive `generation` identify one active operation
  generation.
- Every command has one stable `command_id`, exact lowercase SHA-256 request
  digest and state from the closed vocabulary `received`, `running`,
  `completed`, `failed`, `uncertain`, `revoked`.
- Events use the pair `(generation, sequence)`. Sequence begins at one and is
  contiguous inside a generation; bare sequence comparison across generations
  is forbidden.
- The first event for a command is `received`. Legal transitions are
  `received -> running|completed|failed|revoked`,
  `running -> completed|failed|uncertain|revoked`, and
  `received -> uncertain` only during generation recovery.
- `completed` requires an exact result digest. Other states forbid it.
- An exact repeat of a completed command returns `replay_completed` and its
  recorded result digest. A differing request under the same command id returns
  `conflict` before any state-specific decision. Live exact `received`/`running`
  returns `already_in_progress`; exact `failed`, `revoked` or `uncertain`
  requires a new generation and never replays.
- Recovery advances generation exactly once. Unfinished prior-generation
  commands become `uncertain`; they are never silently re-executed. Completed,
  failed and revoked outcomes remain immutable.
- A same-generation cursor receives later events only. A retired, future,
  missing or out-of-range cursor returns `snapshot_required`; the validated
  snapshot, not replay, is authoritative.
- The supplied event array remains in append-only `(generation, sequence)`
  order. A retired generation cannot leave a command in `received` or `running`;
  its exact recovery transition must be present.

## Frozen unchanged-gate contract

Each gate attempt binds `gate_id`, candidate/evidence digest, command-manifest
digest and one result from the closed vocabulary `deterministic_pass`,
`deterministic_failure` or `uncertain`. Transport, provider, timeout and other
transient failures are `uncertain`; they are never memoized as substantive
deterministic failures.

- no prior attempt or a changed fingerprint returns `run_gate`;
- an exact prior pass returns `reuse_exact_pass` only for the identical bound
  candidate, evidence and manifest;
- an exact prior failure returns `diagnose_without_rerun`;
- an exact prior uncertain result returns `resolve_uncertainty`;
- duplicate attempt ids, ambiguous duplicate generations or contradictory
  results for one exact fingerprint fail closed rather than using latest-wins;
- no decision executes the gate or converts failure/uncertainty to success.

The composite fingerprint covers the gate id, exact candidate source HEAD and
tree, evidence-set digest, command-manifest digest, relevant input digest and
toolchain digest. An omitted or changed component requires `run_gate`; partial
fingerprints fail closed.

## Frozen refinement-promotion contract

Refinement is a proposal surface, not self-modifying authority.

- Editable kinds are only `prompt_note`, `memory_note`, `skill_description`,
  `subagent_spec` and `policy_note`. Executable code, dependencies, commands,
  credentials and runtime tools are not representable.
- A proposal binds a unique id, `local` or `global` scope, exact base-state and
  candidate digests, source HEAD, source-evidence digests, proposer identity and
  intended validation manifest. A decision additionally binds the canonical
  proposal digest.
- Every new proposal begins `quarantined`; the proposer cannot promote it.
- Promotion requires a deterministic validation pass whose manifest digest
  equals the proposal, exact candidate/source HEAD binding, and a distinct Sol
  promotion decision. Global proposals additionally require a distinct
  independent review pass.
- Promotion produces only a typed decision record. It does not edit a policy,
  prompt, skill or source file automatically.
- Rejection and rollback are first-class terminal decisions. Rejection preserves
  the actual validation result. Rollback validates an exact latest promoted
  decision against immutable decision history and current state, derives the
  next generation, and restores its recorded base digest; it cannot infer or
  rewrite content, repeat a rollback or skip an intervening decision.
- A new proposal or rollback creates a new immutable generation. In-place
  history rewriting is forbidden.

## Deterministic artifacts

The implementation will add:

- one sidecar policy YAML, without changing the active-latch schema;
- exact JSON schemas for journal, gate attempt, refinement proposal and
  promotion decision;
- one pure Python module and thin validation/decision CLI;
- closed authored-synthetic evidence covering replay, uncertainty, cursor
  recovery, unchanged-gate suppression, promotion and rollback; and
- focused tests with at least sixty hostile mutations.

The code may read supplied JSON but may not spawn a process, execute a command,
write a journal automatically, access the network, open a database or import
application/product modules.

## Parallelism and allocation

- Sol owns this plan, semantics, acceptance, integration and Git.
- A native subagent performs one read-only overlap audit only.
- DeepSeek V4 Flash/high may implement the closed module, schemas, CLI,
  evidence and tests in a disposable exact-source worktree after this plan is
  committed. It receives no semantic or acceptance authority.
- Gemini 3.7 Flash/high owns one fresh exact-candidate independent veto after
  all deterministic gates pass. No fallback is permitted.
- Shared repository tests and all later PostgreSQL-loading product tests remain
  serial.

## Acceptance

Pass requires:

1. every source binding and schema passes;
2. exact replay, conflict, uncertainty, recovery and cursor decisions pass;
3. unchanged failures cannot be rerun as ceremony or relabelled successful;
4. refinement remains quarantined until all exact promotion conditions pass;
5. proposer self-promotion, executable content, missing evidence, stale base,
   same-identity review, global promotion without independent review, in-place
   mutation and ambiguous rollback all fail closed;
6. at least sixty hostile mutations fail closed;
7. focused, canonical fast-profile, Ruff and whitespace checks pass;
8. a fresh Gemini 3.7 Flash/high veto passes at exact clean source; and
9. all protected refs and unrelated untracked files remain unchanged.

## Forbidden surfaces and claims

No Prime Agent installation/runtime, daemon, worker, IPython kernel, executable
skill, shell/process invocation, network, provider call, database, product or
patient data, product command, automatic policy edit, deployment, production,
release, Pages or protected-ref movement is authorised.

This tranche may prove a deterministic development-harness protocol. It cannot
claim crash-safe filesystem persistence, a running supervisor, distributed
consensus, command completion, security sandboxing, autonomous self-improvement
or any Raisa runtime capability.

## Recovery and next tranche

One bounded mechanical correction is allowed when it changes no frozen state,
authority or promotion meaning. A semantic contradiction returns
`revision_required`.

After accepted closeout, perform a fresh five-source rehydration and begin the
already-planned provider-free unmounted delete-confirm physical
schema-and-transaction scaffold.
