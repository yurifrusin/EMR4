# AGENTS.md Handover Compaction Closeout

Date: 2026-07-15

## Outcome

The root handover was reduced from 131,618 bytes / 1,890 lines to 13,537 bytes
/ 297 lines, an 89.7% byte reduction. The live file now contains current
authority, baton state, rehydration requirements, protected boundaries, user
decision boundaries, operating rules, product guardrails, and the next LC4R9
sequence.

No predecessor information was discarded. The exact source file at commit
`6801fb214d41c41c14f94b90642f6a7d9ee0a6d6` is preserved at
`docs/handover-archive/AGENTS-2026-07-15-pre-compaction.md` with:

- SHA-256 `ad86887db6b640bdeac40111aa9f83c9e422f4ccab5f2eb61334a49449126b4c`;
- Git blob `ace44b93507737141a5e44004c24a087755561af`;
- 131,618 bytes; and
- 1,890 decoded lines.

The archive and manifest were committed and pushed independently at
`e78eda7366e00e21029568fbf5eacda8788fe5fc` before the live file changed.

## Editorial rule

The live file is authoritative for current instructions. Historical detail is
routed through topic ledgers and accepted sprint closeouts. The immutable
snapshot is authoritative only for reconstructing the complete predecessor.
Historical model allocations or retired workflows cannot override the live
authority table.

Future handover updates should change the current baton or boundaries in the
root file and put chronological narrative in the relevant ledger or sprint
closeout. This prevents another unbounded accumulation cycle.

## Verification

`tests/test_agents_handover_archive.py` verifies archive byte identity from the
manifest, Git blob identity, archive index entries, the live size bound,
required authority and protected-boundary phrases, all five mandatory
rehydration sources, and every topic-ledger route.

The maintenance gate passed 13 tests across the archive guards and Ariadne
orchestrator-preflight tests. `git diff --check` was clean. The maintenance
changes no application, provider, route, database, UI, fixture, corpus,
holdout, deployment, or write-authority surface.
