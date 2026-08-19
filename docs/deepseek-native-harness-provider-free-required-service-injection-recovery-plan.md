# DeepSeek native Harness provider-free required-service injection recovery plan

Date: 2026-08-20

Timestamp: 2026-08-20T09:14:31.1452892+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`615c665d33db7d844f5fea6a494a0a2f6f723c63`

Accepted failed native-boot source:
`8155a941a28b3d22a7dbb4132c4b0ada8558482e`

Operation:
`deepseek-native-harness-provider-free-required-service-injection-recovery`

Reasoning level: Extra High freezes the rc.7 service graph, dependency-gated
activation and future native-process boundary. High is sufficient for the
bounded deterministic implementation, tests, independent veto and clockwork
closeout while this plan remains unchanged.

## Objective and exact conclusion to test

The consumed preterminal-observable boot reached the corrected runner and
retained `SERVICES_UNAVAILABLE`. Its patch row and module declared only `hmr`.
This tranche must determine the exact rc.7 reason without starting Harness:

1. `@deepseek-ai/dsh-base@0.1.0-rc.7` supplies the host `tools` row;
2. the `base` + `headless` bundle pair supplies no `agent-presets` row;
3. the rc.7 Web bundle's official host-plane roster row names
   `@deepseek-ai/dsh-agent-presets` with `default: standard`;
4. `composeProfile()` adds the shipped preset root only when the composed rows
   contain `agent-presets`;
5. Cordis combines module and loader-entry injection declarations and keeps a
   plugin fiber inactive until every declared service has an active provider;
   and
6. therefore a future headless patch must add the official `agent-presets`
   host row and the future runner must require exactly `hmr`, `agentPresets`
   and `tools` in both its module export and loader row.

The accepted root-cause label is narrow:
`headless_agent_presets_row_absent_and_runner_dependencies_underdeclared`.
It does not claim that the next native boot would pass. In particular, the
EMR4 profile id `emr4-bounded-worker` is not one of rc.7's shipped presets;
its exact materialisation remains a separate closed prerequisite.

## Immutable inputs and owned artifacts

Both consumed native attempts, their plans, controllers, runners, patches,
ledgers, terminals, evidence and reports remain byte-immutable. The operation
may add only:

- `scripts/deepseek_native_harness_provider_free_required_service_injection_recovery.py`;
- `tests/test_deepseek_native_harness_provider_free_required_service_injection_recovery.py`;
- this plan and its threat-model delta;
- contract, schemas, evidence, report and efficacy reading under
  `orchestration/continuity/deepseek-native-harness-provider-free-required-service-injection-recovery/`;
- Ariadne runtime states and receipts, the exact Gemini review packet/receipt,
  closeout, Sol acceptance and Yuri summary for this operation; and
- the clockwork closeout intent and canonical governance updates.

The deterministic controller may read exact local npm cache blobs in memory.
It may not install or extract packages to disk, retain package source, invoke
Node, enter the native Harness, write a Harness home, contact a registry, or
start an agent, session, turn, broker, model, provider or occupied worker.

## Frozen cache and source boundary

The contract binds exact local cache identities for:

- `@deepseek-ai/dsh@0.1.0-rc.7`;
- `@deepseek-ai/dsh-base@0.1.0-rc.7`;
- `@deepseek-ai/dsh-headless@0.1.0-rc.7`;
- `@deepseek-ai/dsh-web-app@0.1.0-rc.7` as an official inert row reference;
- `@deepseek-ai/dsh-agent-presets@0.1.0-rc.7`;
- `@deepseek-ai/dsh-tools@0.1.0-rc.7`;
- `@deepseek-ai/cordis@4.0.1`; and
- `@deepseek-ai/cordis-plugin-loader@1.0.2`.

Every blob must match its registry SHA-1, integrity and frozen SHA-256. Every
retained member must match exact byte length and SHA-256 before semantic
inspection. Source stays in memory and only booleans, identities, digests,
counts, exact safe row/service names and the generated future declarations may
enter evidence.

## Frozen future declarations

The generated future headless patch fragment must add exactly:

```yaml
- insert:
    - id: agent-presets
      name: '@deepseek-ai/dsh-agent-presets'
      config:
        default: standard
    - id: provider-free-preterminal-observable-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr, agentPresets, tools]
```

The surrounding accepted disabled rows, readiness sentinel, paths and runner
configuration remain unchanged. The generated future runner must change only
its dependency declaration from `export const inject = ["hmr"]` to
`export const inject = ["hmr", "agentPresets", "tools"]`; the accepted
activation vocabulary, sanitized terminal vocabulary, dynamic imports, guard,
scope lifecycle and exit behavior remain exact.

This future fragment is deterministic design evidence, not a write to any
Harness installation or permission to boot. It does not materialise
`emr4-bounded-worker`, mount a preset, create a scope or enter the effective
tool guard.

## Deterministic acceptance

Without Node, Harness or a provider, acceptance must prove:

1. every package/cache/member identity is exact;
2. base has exactly one active `tools` row and no `agent-presets` row;
3. headless adds neither service row and disables the ordinary HMR row;
4. Web rc.7 supplies the exact official `agent-presets` row and default;
5. the agent-presets service is named `agentPresets`, requires `loader`, and
   its config requires `default`;
6. the tool service is named `tools` and requires `systemPrompt`;
7. `composeProfile()` adds the shipped root only after seeing the roster row;
8. the loader merges entry `inject` into the fiber dependency map, Cordis
   resolves arrays exactly, and missing injected services hold activation;
9. the accepted failed patch and corrected runner still declare only `hmr`;
10. the generated future patch and runner both declare the same exact ordered
    set `hmr`, `agentPresets`, `tools`, add one official roster row, preserve
    all accepted coordinate vocabularies, and reject missing, duplicate,
    reordered, surplus or renamed services/rows;
11. both consumed attempts remain byte-exact;
12. no custom preset materialisation or future native execution is claimed;
13. Node/native-Harness, occupied-worker, agent/session/turn, broker, model,
    provider, network, Docker and database counts are all zero; and
14. focused tests, neighbouring provider-free Harness tests, Ruff, compile,
    JSON/schema validation and `git diff --check` pass.

Only after a deterministic clean candidate exists may one fresh Gemini 3.7
Flash/high isolated read-only veto inspect that exact candidate. A P0-P2
finding requires bounded Sol correction and one fresh corrected veto. Gemini
receives no implementation, execution, repair, acceptance, cleanup or Git
authority.

## Explicit parallelism assessment

- **DeepSeek:** declined, negative leverage. The native Harness service graph
  is the provider-free subject. No native process, model request, occupied
  worker or Claude Code fallback is authorised.
- **Gemini:** reserved, required independent leverage. It owns one fresh
  exact-candidate read-only veto after deterministic acceptance.
- **Native subagents:** declined, negative leverage. Current developer policy
  prohibits proactive delegation, and the plugin row, Cordis dependency rule
  and future declaration form one small serial source-semantic boundary.

Sol owns plan, offline inspection, implementation, tests, recovery,
acceptance, clockwork and Git. Reassess all lanes at deterministic candidate,
pre-verifier and closeout.

## Protected and closeout boundaries

This plan authorises no Node/native-Harness process, agent/session/turn,
broker/model/provider request, occupied worker, registry/network access,
credential, Docker, PostgreSQL, SQL or database execution. It changes no EMR4
product source, configuration, REST/OpenAPI, GraphQL, schema, route, feature
flag, authored-synthetic allowlist, action grammar, first-party client or
waiting-area behavior. It enables no ordinary practice, does not add generic
status `Arrived`, and uses no product, patient, appointment, clinical,
historical or protected data.

Production runtime, deployment, release, Pages, protected evidence and
protected-ref movement remain closed. Local/origin `master` and
`handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage explicit paths only; `git add .` and
`git add -A` are forbidden.

At closeout the clockwork is the sole canonical governance writer and must run
`--check` before a separate `--publish`. Sol writes the paired lay/technical
Yuri summary and sends the normal non-PHI Pushover. If accepted, the narrowest
successor is a no-native-process `emr4-bounded-worker` preset-materialisation
recovery; no future boot is implied or authorised here.
