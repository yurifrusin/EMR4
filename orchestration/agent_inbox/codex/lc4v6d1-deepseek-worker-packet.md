# LC4V6D1 DeepSeek Flash Worker Packet

Source head: `b8bafbddf854b671e4e1f12d2c240b88f02db7d6`

Worktree: `C:\Users\sarashera\EMR4-worktrees\claude`

Branch: `claude/current`

Model/transport: DeepSeek V4 Flash/high through Claude Code `--bare` only.
DeepSeek Pro is forbidden.

## Task

Implement the bounded ordinary-development evidence runner and tests defined by
`orchestration/agent_inbox/codex/lc4v6d1-sol-contract.md` for the already
authored fixture
`tests/fixtures/bernie_lc4v6d1_development/probes.json`.

You may read only these task inputs and adjacent ordinary runtime/tests:

- the new contract and fixture;
- `app/services/bernie/semantic_extraction.py`;
- `app/services/bernie/lc4v4d3_policy_resolution.py`;
- `tests/test_bernie_semantic_extraction.py`;
- `tests/test_bernie_lc4v4d3_policy_resolution.py`; and
- `app/services/bernie/lc4v5r1_development_evidence.py` plus its named test as
  a structural example.

## Owned files

- `app/services/bernie/lc4v6d1_development_evidence.py`
- `tests/test_bernie_lc4v6d1_development.py`
- `orchestration/agent_inbox/claude/lc4v6d1-deepseek-candidate.md`

Do not edit any other file. In particular, do not edit the fixture, contract,
parser, policy, AGENTS.md, reports, historical artifacts, routes, APIs, UI,
database/provider code, or test configuration.

## Required behaviour

- Fail closed on fixture schema/population/family-count/ID/required-field drift.
- Compute a deterministic canonical fixture hash.
- Run all 24 probes twice through ordinary `extract_semantics` and explicit
  Option A `resolve_policy`; never pass expected fields downstream.
- Compare extraction and policy separately and report per-layer/composed counts,
  safe counts, repeat variance, and inspectable per-case mismatches.
- Preserve the deliberate contract that unknown practitioner text is exact at
  extraction but becomes clarification at policy when no ID maps.
- Safety for an unknown practitioner requires no mutation tool, delta,
  completion claim, or simulated write at policy.
- Do not add scenario-ID branches or inspect any protected holdout.
- Run focused tests serially using the shared integration Python path.
- Commit only the owned files to `claude/current`.

The durable candidate artifact must name the exact source/candidate commit,
changed files, test command/results, aggregate layer counts, any fixture-label
concerns, and finish with exactly `DECISION: pass` or
`DECISION: revision_required`.

Holdouts v1-v6, T3.1-T3.5, providers, historical material, product/runtime,
routes, APIs, UI, database, deployment, release, and live/write authority are
forbidden.
