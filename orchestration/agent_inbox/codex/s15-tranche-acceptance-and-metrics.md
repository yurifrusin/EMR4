# S15 Tranche Acceptance And Process Metrics

Decision: accepted on staging. No worker was allocated. Protected master and
all work beyond S15 remain closed pending Sol review of the separate manifest.

## Deterministic Acceptance

The final command passed 333 tests:

- 226 integrated S14 policy, Diary, workflow-chain, and API-Spine tests;
- 107 Ariadne preflight, PTY, observability, adapter-settings, and allocation-
  schema control tests.

`py_compile` passed for the changed Diary policy/envelopes and the orchestrator
preflight, PTY, and liveness scripts. `git diff --check` passed. The result is
deterministic local evidence only; it is not live-provider, live-backend,
deployment, or external-client evidence.

No conflicting evidence, scope change, authority issue, or failed gate required
a worker, Conductor, or verifier. S15 made no product/runtime change.

## Per-Sprint Metrics

| Metric | S13 | S14 | S15 |
| --- | ---: | ---: | ---: |
| Sol interventions | 1 | 0 | 0 |
| Terra planning/acceptance corrections | 2 | 2 | 0 |
| Actual worker work lanes | 2 | 1 | 0 |
| Worker stalls / retries / marker corrections | 1 / 1 / 0 | 0 / 1 / 0 | 0 / 0 / 0 |
| Lifecycle defects | 2 | 1 | 0 |
| Conductor/verifier consultations | 0 / 0 | 0 / 0 | 0 / 0 |
| Invalid integrations / manifest variances | 0 / 0 | 0 / 0 | 0 / 0 |
| Duplicated-context events | 0 | 0 | 0 |
| Agents/models used | Terra; DeepSeek 4 Flash/high | Terra; Gemini 3.5 Flash/high | Terra only |
| Advisory stage duration | stalled session about 13 min; accepted retry about 211 sec | completed lane about 233 sec | deterministic suite about 115 sec |

S13's first `node-pty` failure occurred before a worker session began. S14's
first CLI attempt and prompt probe changed no worktree file and produced no
artifact, so they are recorded as transport lifecycle evidence rather than
additional worker work lanes.

## Tranche Totals

- Sol interventions: 1, for progress-based recovery only.
- Terra corrections: 4: S13 deadline and direct-name corrections; S14 CLI
  transport and staff-only confirm-alias corrections.
- Actual worker work lanes: 3; stalls: 1; retries: 2; marker corrections: 0;
  lifecycle defects: 3.
- Conductor/verifier consultations, invalid integrations, manifest variances,
  and duplicated-context events: all 0.
- Used resources: Terra, DeepSeek 4 Flash/high, and Gemini 3.5 Flash/high.
  Gemini was omitted in S13 because no independent surface existed; DeepSeek
  was omitted in S14 because Gemini supplied that independent surface; both
  were omitted in S15 because no conflicting evidence existed. DeepSeek Pro,
  Claude, a Conductor, and a verifier were unnecessary throughout.
- Coordination versus product/test added-line measure through S15 acceptance:
  801 / 866.

## Closed Gates

Terminal-to-active policy remains user-owned. Provider/live-provider,
schema/database, deployment/release, external patient client, H15/H-series,
historical trove, memory/RAG/GraphRAG, GraphQL mutation, UI delivery, new
confirmation action/route, and new write authority remain closed.
