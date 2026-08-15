# Bounded DeepSeek work packet — Ariadne continuity safeguards

Date: 2026-08-15

Timestamp: 2026-08-15T17:55:00+10:00 (Australia/Brisbane)

Bound source commit: `961a833b65e57682e10088300f4b7909a5a5aee8`

Worker: DeepSeek V4 Flash / high through Claude Code `--bare`

## Rehydrate and bind

Read `AGENTS.md` completely, then read these exact controlling files completely:

- `docs/ariadne-provider-free-continuity-journal-and-refinement-promotion-plan.md`
- `docs/security/ariadne-provider-free-continuity-journal-and-refinement-promotion-threat-model-delta.md`
- `orchestration/agent_inbox/codex/ariadne-prime-derived-harness-adaptations-preplanning-receipt.json`

Verify the exact worktree root, named branch, clean state and bound source commit
before editing. The plan is semantically frozen. Do not reinterpret, simplify or
extend it. If two frozen statements genuinely conflict, stop with
`revision_required`; do not choose.

## Exact owned paths

Create exactly these nine files and edit no others:

1. `orchestration/harness_settings/continuity_and_refinement_safeguards.yaml`
2. `orchestration/continuity/ariadne-continuity-and-refinement-safeguards/operation-journal.schema.json`
3. `orchestration/continuity/ariadne-continuity-and-refinement-safeguards/gate-attempt.schema.json`
4. `orchestration/continuity/ariadne-continuity-and-refinement-safeguards/refinement-proposal.schema.json`
5. `orchestration/continuity/ariadne-continuity-and-refinement-safeguards/refinement-promotion.schema.json`
6. `orchestration/continuity/ariadne-continuity-and-refinement-safeguards/provider-free-authored-synthetic-evidence.json`
7. `orchestration_harness/continuity_and_refinement.py`
8. `scripts/ariadne_continuity_and_refinement.py`
9. `tests/test_ariadne_continuity_and_refinement.py`

Do not edit the plan, threat delta, AGENTS, active latch, existing harness
policy, error register, application, model, schema, service, router, OpenAPI,
migration or any other file.

## Mechanical implementation contract

Encode every frozen decision in the plan. Use closed JSON schemas with
`additionalProperties: false` throughout all objects. The module must use only
Python standard-library deterministic logic plus `jsonschema` for schema
admission if already available. It must not import any `app`, Alembic, database,
network, cloud or provider module.

Expose pure, separately testable decisions equivalent to:

- journal validation and command admission;
- new-generation recovery and generation/sequence cursor handling;
- unchanged deterministic gate decision;
- refinement proposal validation, promotion decision and rollback decision.

Exact mandatory meanings:

- only exact byte-bound `completed` results can return `replay_completed`;
  `running` and `uncertain` never replay;
- recovery advances one generation and marks unfinished prior-generation work
  uncertain without executing it;
- cursor comparison always uses `(generation, sequence)` and stale, future,
  missing or out-of-range cursors return `snapshot_required`;
- gate results are only `deterministic_pass`, `deterministic_failure`, or
  `uncertain`; transient/provider/transport/timeout outcomes can only be
  represented as `uncertain`;
- the gate fingerprint requires exact gate id, candidate source HEAD and tree,
  evidence-set, command-manifest, relevant-input and toolchain digests;
- an exact deterministic pass returns `reuse_exact_pass`, exact deterministic
  failure returns `diagnose_without_rerun`, exact uncertainty returns
  `resolve_uncertainty`, and any changed/missing binding returns `run_gate` or
  closed validation failure as the plan specifies;
- refinement kinds are exactly `prompt_note`, `memory_note`,
  `skill_description`, `subagent_spec`, `policy_note` and remain inert;
- proposer, independent reviewer where required, and Sol promoter separation,
  exact evidence/source binding, quarantine, rejection, promotion and rollback
  are deterministic decision records only; they edit or execute nothing;
- global promotion requires distinct independent review; local promotion still
  requires distinct Sol authority; rollback creates a new generation and
  points to one exact promoted decision/base digest.

The CLI may read explicit supplied JSON and print or write an explicitly named
decision result, but it may not append a journal, discover files, execute a
command, spawn a process, access the network/database/provider, or modify
repository/product state.

The authored-synthetic evidence must cover every positive decision and the
named fail-closed boundaries. Tests must reject at least sixty semantically
distinct hostile mutations across journal transitions/replay/recovery/cursors,
gate fingerprints/outcomes, proposal quarantine/separation/bindings and
promotion/rollback. Do not inflate the count with duplicate encodings.

## Verification and handback

Run only:

- JSON parse and Draft 2020-12 schema validation;
- focused pytest for the one owned test file;
- Ruff over the two owned Python files;
- `python -m py_compile` over the two owned Python files;
- `git diff --check` and exact owned-path/status checks.

Use explicit-path staging only. Never use `git add .` or `git add -A`. Commit
only the nine owned files with message:

`Implement Ariadne continuity safeguards`

Return the exact commit, changed paths, test counts, hostile-mutation count,
clean worktree status and one terminal `DECISION: pass|revision_required`. You
have no acceptance, integration, baton, protected-ref, push, provider, product,
deployment or release authority.
