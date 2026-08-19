# Ariadne provider-free no-database manifest and runner admission repair closeout

Date: 2026-08-20

Timestamp: 2026-08-20T01:45:06.9565729+10:00 (Australia/Brisbane)

Status: **accepted**

## Outcome

Provider-free test execution now has a pre-execution interlock instead of a
memory rule. A pure AST classifier reads the exact selected test bytes without
importing or collecting them, resolves the supported local fixture graph, and
denies ordinary pytest, shared-conftest reachability, unknown or ambiguous
fixtures, dynamic grammar, unsafe paths and digest drift before a subprocess
can start.

The same canonical admission digest is checked at manifest preflight and again
at runner launch. New DeepSeek work orders use
`ariadne.deepseek_work_order.v2`, binding the exact command manifest and
no-database admission artifacts. The broker validates both supplied artifact
bodies before `broker-ready` or simulated upstream I/O. Historical v1 orders
remain test-only behind an explicit compatibility switch.

## Exact sources and evidence

- Tranche base: `440fc7bbd071fbb97a97c986e8c80fe69b83f747`
- First reviewed candidate: `91ee5ee06b7f1fb698b0240208295b226c4b87ff`
- Corrected independently reviewed candidate:
  `60ce7b7603331d4e69d551db92eb592c7fef1ea3`
- Command-manifest SHA-256:
  `sha256:5a2c760132aad87d3c05b46ac2aeb65e2bd5e4d8dd6ca9fcbbaf7d685e872b99`
- Aggregate admission SHA-256:
  `sha256:bf1fa67c57c589ec67bae88a3fd71795f75057b598b5b6090cd7ba21263e1bbc`
- Protected local/origin `master` and `handoff/current`:
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

## Verification

- The focused provider-free suite passed 48 tests.
- The existing provider-free clockwork/governance selection passed 527 test
  functions through the admitted runner.
- All 128 hostile fixture, import, grammar, path and binding mutations were
  rejected with zero escape.
- The repository A5.1 suite was rejected before subprocess creation with
  `provider_free_conftest_import_forbidden`.
- Manifest preflight and runner selection produced byte-identical admission
  artifacts.
- Broker tests rejected missing or mutated v2 bindings before readiness or
  simulated upstream I/O.
- Ruff, Python compilation, Node syntax and Git whitespace checks passed.
- Selected-module imports, pytest collections, ordinary pytest, Docker,
  PostgreSQL, provider calls and occupied DeepSeek attempts were all zero in
  the deterministic evidence build.

Gemini 3.7 Flash/high returned `revision_required` at the first exact clean
candidate because two synthetic evidence operands embedded the main
worktree's absolute path. That made otherwise identical evidence drift in the
isolated review worktree. The evidence-only operands were made repository-
relative (`python` and `--repo-root .`); a cross-worktree comparison then
matched exactly. One fresh corrected review passed all 11 commands at exact
candidate `60ce7b7603331d4e69d551db92eb592c7fef1ea3`, left it clean, and
reported no P0-P2 finding.

## Efficiency and control reading

The tranche removes the observed repeated reminder/rerun class: a provider-
free manifest can no longer launch an ordinary pytest entry point or a selected
test whose supported fixture graph might acquire shared PostgreSQL. The
classifier is intentionally syntactic and fail-closed; unsupported Python or
pytest grammar is a denial rather than an inferred safety claim.

One advisory pre-verifier check also rejected the orchestrator's first
observation-method spelling before any worker started. That bounded authoring
correction and the first Gemini portability rejection are retained here as
efficacy readings. They are not manually projected into the clockwork-owned
canonical error register.

## Parallelism closeout

- DeepSeek was not invoked. Its native Harness cannot review its own broker
  interlock, Claude Code is not a fallback, and occupied work remains closed
  pending the separate provider-free boot proof.
- Gemini owned one corrected exact-candidate read-only veto and passed it.
- Native subagents were not used under the active developer constraint and
  because the classifier, manifest, WorkOrder and broker bindings were one
  serial authority boundary.

## Boundaries retained

No product source, API Spine, OpenAPI, GraphQL, configuration, database,
Docker, feature flag, allowlist, action grammar, first-party client,
waiting-area behavior or ordinary-practice admission changed. No product,
patient, appointment, clinical, historical or protected data was used. No
provider call, occupied DeepSeek attempt, production runtime, deployment,
release, Pages or protected-ref movement is authorised. `docs/branding/` and
every unrelated untracked file remain preserved.

## Next operation

Proceed under Yuri's standing authority to
`deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-boot-proof`.
Freeze and execute the narrowest provider-free proof that the pinned native
Harness can boot through its documented stock headless path and reach the
custom runner under HMR with traceable readiness, terminal state and cleanup.
It authorises no DeepSeek model call, credentials, product data, attempt-004,
development edit, production or protected-ref movement.
