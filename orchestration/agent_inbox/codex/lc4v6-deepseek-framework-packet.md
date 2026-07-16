# LC4V6 DeepSeek Empty-Framework Packet

Source head: `4b9caf98064fd5009ac2e5e1673a5a22d70273ed`

You are DeepSeek V4 Flash/high through Claude Code `--bare`, acting only as a
bounded implementation/test worker. GPT Sol owns architecture, acceptance,
recovery, content authorship, sealing, integration, commit, and push.

## Required first checks

Verify the authorized root is exactly
`C:\Users\sarashera\EMR4-worktrees\lc4v6-dw1`, branch is
`claude/lc4v6-content-blind-framework`, HEAD descends from the named source,
and the worktree is clean. Stop with `DECISION: revision_required` otherwise.

Read only these named inputs:

- `AGENTS.md`
- `orchestration/agent_inbox/codex/lc4v6-sol-contract.md`
- `app/services/bernie/semantic_extraction.py`
- `app/services/bernie/lc4v4d3_policy_resolution.py`
- `app/services/bernie/lc4v4d4_composed_integration.py`
- `app/services/bernie/lc4v5r1_development_evidence.py`

Do not Glob, Grep, list, or discover any fixture/test/holdout directory. Do not
open any historical LC4V1-V5 framework, fixture, authoring module, manifest,
seal, receipt, test, filename, or per-case artifact.

## Owned output surface

- `app/services/bernie/lc4v6_content_blind_framework.py`
- `tests/test_bernie_lc4v6_content_blind_framework.py`
- `orchestration/agent_inbox/claude/lc4v6-deepseek-candidate.md`

Do not edit any existing file. Do not create fixtures, content, examples,
manifests, seals, reports, acceptance rules, or scenario utterances. Do not
commit or push.

## Implementation contract

Implement an empty, pure-Python framework that contains no real V6 content and
does not execute at import time. It must provide:

1. frozen typed schema for a future scenario contract and typed observation;
2. strict manifest validation for exact fixed shape 24 groups, 288 scenarios,
   72 multi-turn, 216 one-shot, six actions, 288 unique coverage cells, and two
   repeats, while accepting the future scenario objects only as supplied data;
3. strict source/corpus/manifest/framework/evaluator hash binding helpers;
4. an aggregate-only reducer whose public result cannot contain scenario IDs,
   utterances, expected values, source spans, normalized turns, labels, or
   failure selections;
5. an evidence validator for exact population, zero exceptions/missing
   dimensions/case artifacts/variance, predefined slice arithmetic, and
   hash/schema consistency;
6. a file-backed one-shot state machine that fails closed unless the exact
   frozen source seal is present and unconsumed while marker/report are absent,
   then writes exact attempt `lc4v6-fresh-attempt-001`, consumes the seal, and
   refuses rerun/overwrite/reuse;
7. dependency injection for future interpretation/replay evaluation so empty
   tests never require actual prompts or protected content; and
8. tests for valid placeholder metadata, every malformed population boundary,
   aggregate leakage refusal, tamper/hash failure, pre-run state failure,
   successful single consumption in a temp directory, and all rerun cases.

Do not implement threshold acceptance; Sol writes the separate frozen rule.
Do not import or branch on scenario IDs in product interpretation. Placeholder
tests may use opaque tokens such as `group-001`, `cell-001`, and empty strings,
but no natural-language receptionist instruction or expected semantic value.

Run only:

`C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest tests/test_bernie_lc4v6_content_blind_framework.py -q`

and `git diff --check`.

Write the durable candidate artifact with exact changed files, test count,
framework properties, known limitations, and terminal line `DECISION: pass` or
`DECISION: revision_required`.

Holdouts v1-v5, T3.1-T3.5, providers, local models, historical diary data,
routes, APIs, UI, database, product defaults, deployment, release, and all
live/write authority remain closed.
