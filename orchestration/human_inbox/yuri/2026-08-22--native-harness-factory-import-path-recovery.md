# Native Harness factory import-path recovery

Date: 2026-08-22

Timestamp: 2026-08-22T19:27:57.8855998+10:00 (Australia/Brisbane)

## Lay summary

This time the mechanism made real forward progress. After proving the two
package files existed in the corrected folder, the one local test reached the
actual installed Harness factory and reproduced exactly the failure we had
predicted: the runner was handing four plugs to the old three-socket safety
guard. Nothing reached DeepSeek or a provider.

We therefore no longer need another diagnosis. The next step is the existing
accepted repair: leave the runner alone and put the already-built four-socket
guard, bridge and sanitizer beside it.

The first implementation test run did catch a handful of brittle test
assumptions before the process—one test also intercepted Git checks while
trying to forbid Node. Those were corrected before the only attempt and are
recorded as AER-0979 so this pass does not conceal its local correction cost.

## Technical summary

- Exact source difference: `package_root.parents[1]` to
  `package_root.parent`; all other fixture source differences: zero.
- Prelaunch imports: Cordis and `dsh-agent`, both present under
  `node_modules/@deepseek-ai`.
- Installed `AgentRegistry.create`: 1 transit; setup callback: 1 invocation.
- Structured coordinate: `EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID`.
- Runner terminal: `failed` / `factory`; requests/tools/turns: 0/0/0.
- Node: one process, exit 0, 641 stdout bytes, 0 stderr bytes.
- Harness / broker / worker / model / provider: all zero.
- Retry / resume / fallback: all zero.
- Cleanup: process and disposable root absent.
- Verification: 63 lineage tests, Ruff, compilation, schemas and whitespace
  pass on an origin-aligned source.

## Deliberately closed

No DeepSeek turn, model/provider request, product or patient data, ordinary-
practice change, production runtime, deployment, release, Pages or protected-
ref movement. Existing untracked files, especially `docs/branding/`, remain
preserved.

## Next tranche and attention

Next:
`deepseek-native-harness-provider-free-integrated-runner-accepted-guard-graph-materialization-recovery`.

It will install only the already accepted guard/bridge/sanitizer graph beside
the unchanged runner and prove the factory mismatch is removed without a model
or provider request. Yuri's attention is not required.
