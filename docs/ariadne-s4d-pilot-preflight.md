# Ariadne S4d Pilot Preflight

Date: 2026-07-11

## Outcome

`revision_required` before worker dispatch. This is a valid pilot outcome: the
preflight caught stale worker mirrors and an execution-surface mismatch without
letting the orchestrator silently substitute a verifier.

## Receipts

| Assigned role | Resource / transport | Workspace receipt | Result |
|---|---|---|---|
| Conductor | Claude Opus through Claude CLI | `claude/current`, clean, `HEAD = handoff/current = abe8b47f` after target-worktree realignment | Ready |
| Antigravity review lane | Antigravity platform, Gemini Flash 3.5, `agy.exe` CLI | `antigravity/current`, clean, `HEAD = handoff/current = abe8b47f` after target-worktree realignment | Ready but not dispatched |
| Verifier | DeepSeek Flash through local Codex call/spawn | The user-confirmed transport is declared in `transport_adapters.yaml`; this Codex task exposes only built-in subagent model handles, not the configured DeepSeek bridge handle | Not dispatchable from this task surface |
| Orchestrator | GPT Terra / protected Codex session | Integration worktree on `master` | No substitution permitted |

The initial Claude plan was rejected because `claude/current` was stale and did
not contain the committed harness settings. The standard realignment command
correctly refused when first invoked from `master`; run from the target clean
Claude worktree it realigned to `handoff/current`. Antigravity was likewise
clean but behind the handoff and was realigned from its target worktree.

## Conductor Proposal Preserved

Claude Opus proposed a bounded docs/tests-only EMR4 sprint to harden the
transport-adapter reachability-versus-authority guard:

- DeepSeek D1: standalone negative/positive adapter-guard tests;
- DeepSeek D2: transport-adapter authority doctrine note;
- Antigravity: independent adversarial review packet only;
- no runtime, provider, frontend, database, GraphQL, H15/H-series, D5,
  deployment, or release work.

The proposal remains unverified. Its expected verifier result is not inferred.
Do not dispatch workers until a Codex surface that exposes the declared
DeepSeek local-spawn adapter submits an actual `pass` or `revision_required`
artifact against the current settings fingerprint.
