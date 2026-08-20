# Provider-free check-in native Harness preset-row service-path recovery plan

Date: 2026-08-20

Timestamp: 2026-08-20T17:42:05.9062693+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery`

## Purpose

Explain and repair the exact configuration difference between the passing
direct rc.7 package scan and the accepted negative native `agentPresets`
service reading. The predecessor is immutable: its sole native process reached
`PRESET_ROW_DISCOVERY_ENTERED` but not `PRESET_ROW_FOUND`, made no external
request, and cannot be retried or reclassified.

The retained rc.7 source exposes one narrow candidate cause. Native
`composeProfile()` appends a final `agent-presets` overlay that replaces every
configured `roots` value with the Harness's shipped preset root. The EMR4
diagnostic profile also set `includeUserRoot: false`, so the derived
`$DSH_HOME/.agent-presets` root holding `emr4-bounded-worker` was excluded. The
direct package scan passed because it received that excluded root explicitly.

This tranche must prove that source-to-effective-config transformation with
closed fixtures before it may correct the diagnostic profile to retain the
shipped root and re-enable the derived user root. It changes no installed
Harness package and admits no DeepSeek request, agent, mount, session or turn.

## Exact predecessor and source binding

- Accepted predecessor source:
  `65a87b14e4c8a06af8bce0e22d39a2ca6b3c2691`.
- Pinned installation:
  `C:\Users\sarashera\EMR4-worktrees\deepseek-check-in-attachment-observability-native-001`.
- Pinned packages: `@deepseek-ai/dsh@0.1.0-rc.7`,
  `@deepseek-ai/dsh-agent-presets@0.1.0-rc.7` and
  `@deepseek-ai/dsh-home-paths@0.1.0-rc.7`, all bound through the retained
  lockfile and exact installed-source digests.
- Canonical preset:
  `.agent-presets/emr4-bounded-worker/agent.cordis.yml`, 158 bytes, SHA-256
  `3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1`.
- The consumed predecessor terminal, process allowance and attempts 001
  through 005 remain byte-immutable.

## Frozen stages

### Stage 1 — exact source and effective-root proof

Create one provider-free controller and focused tests that read only the
retained installation, canonical preset, predecessor evidence and generated
diagnostic profile. They must bind and prove:

1. `AgentPresets` derives `resolvedRoots` once from configured `roots` and,
   only when `includeUserRoot` is true, appends
   `dshHomePath(".agent-presets")` with `user` trust;
2. `composeProfile()` builds the configured row map, then appends a final
   `agent-presets` overlay whose `roots` is exactly the rc.7 shipped preset
   directory with `system` trust;
3. that overlay preserves the existing `includeUserRoot` value while replacing
   the earlier configured roots;
4. the predecessor profile set `includeUserRoot: false`, so its native
   effective root set was exactly the shipped root and excluded the disposable
   `$DSH_HOME/.agent-presets` root;
5. the shipped root contains exactly `code`, `cordis`, `minimal` and
   `standard`, not `emr4-bounded-worker`; and
6. the direct package-only scan was explicitly given the disposable user root,
   explaining why it found one healthy row while the native service did not.

Static/source failure stops the tranche. No Node or native process is needed
for this stage.

### Stage 2 — closed service-input fixture matrix

Materialise disposable, authored-synthetic roots and evaluate the package's
exact discovery semantics without booting the native Harness. The matrix must
cover:

- predecessor effective inputs: shipped root only, no EMR4 row;
- corrected effective inputs: shipped root followed by the derived
  `$DSH_HOME/.agent-presets` user root, exactly one healthy EMR4 row at the
  canonical path with `user` trust, 158 bytes and the exact digest;
- missing user root: fail closed with no EMR4 row;
- duplicate EMR4 id in the earlier shipped root: fail closed as shadowed, not
  silently accepted from the later user root;
- malformed, missing, reordered or broadened fixture/config fields: rejected;
  and
- an attempted arbitrary configured-root override: proved displaced by the
  native final shipped-root overlay rather than reported as effective.

Only enumerated paths, counts, trust labels, digests and reason codes may be
retained. Raw exception text and raw process output are not durable evidence.
Any package-only Node process must import only the pinned local packages, run
offline with the existing network-denial guard, assemble no native Harness
service graph, create no agent and be absent at terminal.

### Stage 3 — minimal diagnostic-profile correction candidate

Amend only the provider-disabled diagnostic profile generator and its closed
runner expectations:

- remove the explicit `includeUserRoot: false` override or set it exactly
  `true`;
- keep the native shipped root and require the derived user root second;
- require `emr4-bounded-worker` to resolve exactly once from the disposable
  user root with `user` trust;
- preserve default preset id, exact bytes, no-agent runner, network denial,
  provider scrubbing, one-shot terminal and cleanup controls; and
- reject any installed-package mutation, shipped-preset copy, arbitrary root
  injection or broad profile change.

This correction is fixture/controller work only. It does not alter the
retained rc.7 installation or any EMR4 product configuration.

### Stage 4 — candidate gate and independent veto

Run contract/schema checks, focused tests, Ruff, Python compilation, static
installed-source checks and the package-only fixture matrix. Because the
candidate changes the meaning of the native effective root and trust label,
one fresh Gemini 3.7 Flash/high read-only veto is required over the exact clean
candidate. Gemini receives no implementation or acceptance authority.

DeepSeek remains declined: the Harness configuration is the evidence subject
and no model request is admitted. Native subagents remain declined under the
current developer policy and serial source/fixture boundary.

### Stage 5 — separate native-process checkpoint

Only after Stages 1 through 4 pass at one exact clean candidate may clockwork
publish a separate checkpoint binding the controller, generated profile,
runner, canonical preset, retained package sources, review receipt, marker
order, terminal path, timeout, cleanup and a one-process/zero-retry allowance.

Before that checkpoint, the new native Harness process count is zero.

### Stage 6 — one provider-disabled native service-row confirmation

The checkpoint may admit exactly one new no-agent native Harness process. It
may boot only far enough to call `agentPresets.list()` once and require:

1. discovery entered;
2. effective roots are shipped `system` then `$DSH_HOME/.agent-presets`
   `user`;
3. exactly one healthy `emr4-bounded-worker` row is found at the canonical
   disposable path with `user` trust; and
4. exact byte length and digest pass.

It must then exit. The runner contains no `agents.create`, preset mount,
session, turn or broker/model/provider call. First process creation consumes
the allowance; failure writes one sanitized terminal, cleans up and forbids
retry.

## Acceptance and claim boundary

The tranche may be accepted when the source and fixture evidence proves the
predecessor exclusion, the corrected profile candidate produces the exact
two-root effective roster in package-only evidence, the independent veto
passes, and the separately checkpointed native service either confirms the
exact user-trust EMR4 row or produces accurately labelled bounded negative
evidence with exact cleanup.

A native pass proves only rc.7 preset-row service convergence under the
provider-disabled disposable envelope. It does not prove preset mount,
effective tools, agent creation, occupied DeepSeek work, model quality,
attempt 006, database or product behavior, production suitability or
deployment authority.

## Parallelism assessment

- **DeepSeek Flash:** declined with negative leverage. No model request is
  admitted and the native Harness is the evidence subject.
- **Gemini 3.7 Flash/high:** declined at planning; required later for one fresh
  exact-candidate veto because root/trust semantics materially change.
- **Native subagents:** declined. Current developer policy prohibits proactive
  delegation and the source-to-fixture sequence is serial.
- **GPT Sol:** owns source analysis, controller/tests, fixture execution,
  checkpoint, one-process monitoring, recovery, acceptance, clockwork and Git.

## Deliberately closed

No retry/reclassification of consumed processes; no DeepSeek or other model
request; no attempt 006; no agent creation, preset mount, session, turn or
occupied worker; no installed-package or shipped-preset mutation; no network,
Docker, PostgreSQL, SQL or transaction execution; no product source,
configuration, API/OpenAPI/GraphQL/schema/migration, route, feature flag,
allowlist, grammar, client or waiting-area change; no ordinary-practice
enablement or generic-status `Arrived`; no product, patient, appointment,
clinical, historical or protected data; no production runtime, deployment,
release, Pages or protected-ref movement.

There is no protected-ref movement.

Preserve `docs/branding/` and every unrelated untracked file. Stage only exact
paths; never use `git add .` or `git add -A`.
