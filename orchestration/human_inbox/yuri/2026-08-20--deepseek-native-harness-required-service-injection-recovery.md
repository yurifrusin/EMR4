# DeepSeek native Harness required-service injection recovery — Yuri summary

Date: 2026-08-20

Timestamp: 2026-08-20T09:54:56.7001117+10:00 (Australia/Brisbane)

## Lay summary

We now know why the new DeepSeek harness stopped before it could do useful
work. The runner was waiting for only one service even though it needs three.
The harness package already supplies the tools service, but its headless setup
does not supply the preset service. The next future boot must explicitly add
that preset service and wait for all three services before the runner starts.

The independent review found two genuine test-boundary defects, both of which
were corrected. A later review run did all the work successfully but mistyped
one command in its machine-readable receipt, so the broker rejected it exactly
as intended. A fresh review then passed cleanly: all ten checks, including 86
tests, with the candidate unchanged.

The first clockwork closeout also caught a missing human-readable register
note after publication. It restored the previous governance generation
byte-for-byte; the note and a prepublication presence check have now been
added. This cost one closeout rerun but left no ambiguous canonical state.

This is encouraging but deliberately narrow. We have not yet run a DeepSeek
worker. The named `emr4-bounded-worker` preset still needs to be materialised
and proved against the edit/glob/read boundary before another native boot is
eligible.

## Technical summary

- Accepted candidate:
  `056c59d14de4efc302898e84ec7a69cbf729dfce`.
- Root cause: base supplies `tools`; headless supplies no `agent-presets` row;
  both accepted entry and runner declared only `hmr`; Cordis therefore could
  not gate runner activation on `agentPresets` or `tools`.
- Frozen future declaration: add the official
  `@deepseek-ai/dsh-agent-presets` row with `default: standard`; require ordered
  `hmr`, `agentPresets`, `tools` in entry and runner.
- Deterministic verification: 15 focused tests and 86 exact provider-free
  isolated-worktree tests, plus Ruff, compilation, projection and Git checks.
- Independent review: initial `revision_required`; one corrected non-admitted
  C10 envelope; final Gemini 3.7 Flash/high `pass` with ten zero-exit commands,
  exact C10 argv, unchanged HEAD and clean worktree.
- Clockwork: first publication rolled back byte-exactly after the required
  revision-568 companion note was missing; failed-attempt evidence is retained
  and the corrected command manifest checks the note before republication.
- Execution boundary: zero Node, native Harness, occupied worker, agent
  session, turn, broker, DeepSeek model, provider, external network, Docker and
  database execution.
- Protected boundary: no product, API, client, feature flag, ordinary-practice,
  waiting-area, data, production, deployment, release, Pages or protected-ref
  change.

Next: a separately named provider-free deterministic tranche will materialise
the exact `emr4-bounded-worker` preset and prove only its edit/glob/read mapping.
It will not start the native Harness or contact DeepSeek.
