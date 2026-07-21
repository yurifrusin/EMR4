---
name: ariadne-continuity
description: Preserve and inspect EMR4 work lineage and programme position with the local Ariadne Continuity Engine and read-only Compass. Use for checkpointing or comparing work branches, recording a fork or candidate knowledge harvest, closing a branch with evidence, auditing inherited obligations and closed authority boundaries, or explaining where the active programme sits and which decisions remain open. Do not use it as a substitute for the mandatory EMR4 rehydration, acceptance, integration, planning authority, workflow execution, or product runtime.
---

# Ariadne Continuity

Use the repository's metadata-only continuity graph to make branch relationships, inherited obligations, evidence, and unresolved gates explicit.

Use the Compass when the question is larger than branch status: where the
current work fits in EMR4, why it was undertaken, what it proved, what it
unlocks, what it does not solve, and which next directions remain candidates.

## Start safely

1. Read the repository `AGENTS.md` completely.
2. If the EMR4 handover requires rehydration, complete its mandatory five-source process before planning or implementation. The graph is not a sixth source and never replaces a receipt.
3. Work in the applicable task worktree. Do not disturb a live product runtime or focused review session.
4. Run commands from the repository root with the active Python environment:

```powershell
python scripts\ariadne_continuity.py validate
python scripts\ariadne_continuity.py audit
python scripts\ariadne_continuity.py show
python scripts\ariadne_compass.py validate
python scripts\ariadne_compass.py show --format markdown
```

Stop on `revision_required`. Route each reason to the missing artifact, contract evidence, authority source, or lineage correction. Never override a failing audit by changing historical acceptance status.

## Read and compare

Use `show --node <id>` to inspect one branch and its inherited contracts. Use two or more repeated `--node` arguments to compare branches:

```powershell
python scripts\ariadne_continuity.py compare `
  --node functional-meta-grid-client `
  --node meta-grid-live-local-integration
```

Treat output as an evidence index and continuity prompt, not as proof that the underlying artifact passed.

## Navigate with the Compass

Run `ariadne_compass.py validate` before relying on the current programme
position. Validation binds the map to an exact continuity-graph revision,
requires real accepted nodes and lineage, checks repository evidence, audits
the terminal product node and rejects unknown boundary changes.

Use `show --format markdown` for human orientation and `show --format json` for
automation or comparison. The report distinguishes the product decision
horizon from programme-support work and labels every horizon item `candidate`,
`deferred` or `blocked`.

The Compass does not recommend or select a winner. Do not treat the last journey
node as an instruction to continue expanding that branch. Every Yuri-owned
question and every boundary-changing candidate remains a fresh decision.

## Record bounded changes

- `checkpoint --node-file <repo-relative-json>` adds a complete node. Updating an existing node requires the explicit `--update` flag.
- `fork` records a child relationship and coordinates. It does not create a Codex task, Git branch, or worktree.
- `harvest` records candidate knowledge from one or more source nodes into a target. It does not change target decisions, acceptance, authority, or implementation.
- `close` records a branch disposition. `accepted` requires an existing repository acceptance path. The command cannot accept its own work, move the baton, change Git refs, or push.

Use explicit `--at` timestamps in deterministic tests and evidence runs. Every evidence, waiver, decision, and authorization source must be an existing repository-relative file.

## Preserve authority boundaries

The graph globally inherits all closed EMR4 boundaries. Only an `authorized_openings` record naming both a closed boundary and an evidence path can describe a bounded opening; the graph itself grants nothing.

Never place raw conversations, clinical or identifying data, credentials, secrets, external-provider prompts or responses, model reasoning, protected evidence, or historical diary material in the graph. Store only short metadata summaries and repository-relative evidence pointers.

The `protects` and `supersedes` relationships are descriptive and do not inherit product contracts. `builds_on`, `implements`, `validates`, `forked_from`, and `synthesizes` do inherit contracts through the complete ancestor chain.

## Validate after mutation

After any graph write, run:

```powershell
python scripts\ariadne_continuity.py validate
python scripts\ariadne_continuity.py audit
```

Then run the focused continuity tests. A structural validation pass and a contract audit are separate gates: a graph may be structurally valid while accurately returning `revision_required` for an open inherited obligation.
