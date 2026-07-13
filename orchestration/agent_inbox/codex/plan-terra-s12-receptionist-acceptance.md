# S12 receptionist acceptance plan

## Status

`accepted_for_execution` under the revised routine Terra contract. No optional
Conductor consultation trigger is present: the scope, authority, and acceptance
criteria are explicit and unchanged.

## Boundary

S12 closes the S10-S12 tranche with deterministic evidence over the integrated
S9 Diary dev-loop, S10 provider-free workflow chain, S11 confirmation-contract
matrix, and the Deep Code liveness/transcript checkpoint. It permits only a
local harness dependency install declared by `orchestration/deepcode_pty` so
the tracked bounded-transcript test can execute in this fresh worktree.

It does not alter terminal-to-active policy, providers, app/services runtime,
schema/database, deployment/release, external patient clients, H15/H-series,
historical diary material, memory/RAG/GraphRAG, or write authority.

## Allocation

| Lane | Model and transport | Deliverable | Acceptance |
| --- | --- | --- | --- |
| W1 | DeepSeek 4 Flash/high via detached Deep Code PTY | Independent evidence-only S12 receptionist workflow acceptance review | Canonical `STATUS: complete` artifact, completed PTY receipt with bounded redacted transcript, no code changes, and conclusions traceable to the named deterministic tests. |

No Gemini lane is allocated. The integrated scope has no rendered receptionist
or Diary change requiring a distinct visual/browser capability; a Gemini lane
would duplicate deterministic evidence rather than add material coverage.

## Acceptance

1. Install the lockfile-pinned local PTY adapter dependency in the staging
   worktree only; do not modify lockfiles or committed dependency state.
2. Run the S9, S10, S11, and liveness/observability focused suites together.
3. Validate W1's artifact, receipt, mailbox event, containment, and bounded
   redacted terminal transcript with the liveness observer.
4. Independently review the staged diff and run `git diff --check`.
5. Commit only S12 plan, packet, accepted review, and closeout/manifest
   evidence on `codex/s10-terra-staging`. Protected-master integration remains
   Sol-authorized only.
