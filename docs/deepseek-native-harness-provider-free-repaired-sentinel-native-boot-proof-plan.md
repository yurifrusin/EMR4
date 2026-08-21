# DeepSeek native Harness provider-free repaired-sentinel native boot proof plan

Date: 2026-08-21
Timestamp: 2026-08-21T14:04:01.2651862+10:00 (Australia/Brisbane)
Status: `frozen`
Reasoning level: `high`
Planning source: `0e8ca60b3675e1dd259351e6eca2616ed77d4827`

## Objective

Run exactly one pinned `@deepseek-ai/dsh@0.1.0-rc.7` Node/Harness
process with the accepted bounded-worker profile in its repaired initial form.
The process must emit exactly `sentinel_activated` followed by
`stock_headless_hmr_ready`. The controller then terminates it without ever
writing the changed profile. A non-passing attempt is retained as one
sanitized fail-closed pre-provider terminal and is never retried.

This proves only that the repaired profile-relative sentinel module loads and
that stock headless HMR reaches readiness. It does not load the changed runner,
create a worker or session, send a prompt, use a broker, request a model or
provider, or establish DeepSeek development reliability.

## Frozen lineage

- accepted proof-module repair candidate:
  `3c31f2a9a44713db27b82e338e05374c5d9f62bc`;
- accepted repair clockwork source:
  `b0ab1f7d2d9623890c8ceafa2675545b8bdd8ce6`;
- accepted complete-composition native boot source:
  `6ef058b87a2c927efd9d9d2027b59d6ad279fec5`;
- repaired bounded-worker controller SHA-256:
  `83d7b7ed0a438993f32b60d98f1dda567875eb67e6fcba5087d9b6796d23deeb`;
- repair evidence SHA-256:
  `3f587f86ab3ddf94732ddab3e804fe9b7d8d0bf77f3270ad86b499cfad2a8274`;
- accepted complete-composition evidence SHA-256:
  `9ba784b0726addb5644ac3786def410aed56e5bf9da3e23ec21d8e10f6ba1ea0`.

All object IDs are full 40-character commit IDs and must resolve as ancestors
of the execution candidate before process start.

## Exact construction

Before the sole process start, the controller must:

1. validate the frozen contract, schemas, lineage and component digests;
2. copy the already accepted rc.7 package tree using Python filesystem copying
   only, with no npm, package-manager, Node or network process;
3. create one disposable root beneath the accepted worktree parent;
4. materialize the existing headless profile manifest and accepted bounded
   preset required by the unchanged initial profile;
5. write only `installation/proof/sentinel.mjs` from the accepted controller;
6. generate `cordis.patch.yml` through the repaired
   `profile_patch(..., changed=False)` function;
7. prove the profile contains exactly one
   `../../../installation/proof/sentinel.mjs`, contains no runner row or
   `runner.mjs`, and passes the pre-existing profile validator; and
8. scrub credential/proxy environment names and preload the accepted
   network-denial guard.

The unchanged initial profile may contain its inert loopback model
configuration, but no broker exists, no task is supplied, and no agent or
request is created. The controller must not generate, copy, reference or write
the changed runner.

## Sole launch and terminal

The sole command is exactly:

`node --expose-internals <pinned rc.7 lib/bin.js> --profile headless`

There are no task arguments. The first `subprocess.Popen` consumes attempt
`repaired-sentinel-native-boot-attempt-001`. The controller polls the bounded
event ledger. On the exact two-event prefix it records readiness and terminates
the process. It never mutates the profile. If the process exits early, times
out, emits malformed or surplus events, attempts network access, or cannot be
cleaned up, the result is `failed_closed` with one closed-vocabulary failure
coordinate.

Raw stdout and stderr may exist only inside the disposable root. The controller
retains their byte counts and SHA-256 digests, terminates the exact child,
removes the exact root, proves both absent, and retains no raw stream,
environment, path, message or stack content.

## One-run latch

- native Node/Harness process limit: one;
- automatic retry: false;
- manual retry: false;
- resume: false;
- fallback: false;
- occupied attempts 001-004: immutable and not referenced for execution;
- changed profile writes: zero;
- runner, broker and worker processes: zero;
- prompts, tool calls, model requests, provider requests and network attempts:
  zero.

Construction defects found before `Popen` may be corrected and rechecked.
After the first `Popen` call there is no second process under any result.

## Deterministic admission

Before execution, focused tests and `--check` must prove:

- exact full-hash ancestry and component bindings;
- exact rc.7 package identity and zero-process materialization source;
- exact initial profile and repaired relative sentinel coordinate;
- absence of changed runner materialization and profile mutation code;
- exact five-argument command with no task;
- exactly one `subprocess.Popen` call and no retry loop;
- bounded event parsing, closed failure vocabulary and exclusive outputs;
- terminalization before interpretation and cleanup on simulated success; and
- zero Node/Harness activity during deterministic checks.

The code, contract, schemas and tests must be committed and pushed as one exact
reviewed candidate before a fresh preexecution receipt can authorize the sole
process.

## Parallelism assessment

- **DeepSeek Flash:** declined; model/provider activity would invalidate this
  pre-provider claim.
- **Gemini 3.7 Flash/high:** declined; provider review is outside this latch.
  Reassess after terminalized evidence if later authority permits it.
- **Native subagents:** declined; developer policy prohibits proactive
  delegation and the one-process attempt requires a single serial owner.
- **GPT Sol:** owns the contract, implementation, deterministic admission,
  sole process, terminalization, cleanup and acceptance.

## Acceptance

Accept `pass` only when exactly one native process starts, the event ledger is
exactly `sentinel_activated`, `stock_headless_hmr_ready`, the controller
terminates only after readiness, network and every provider/worker counter are
zero, and process plus disposable root are absent. A sanitized
`failed_closed` terminal is still a valid one-attempt result but is not a
passing boot proof and authorizes no retry.

## Protected boundaries

- no changed runner, broker, worker, model or provider execution;
- no occupied attempt retry, resume, fallback or reclassification;
- no product source, configuration, API, database, route, adapter, flag,
  allowlist, grammar, client or waiting-area change;
- no ordinary-practice enablement or generic-status `Arrived` change;
- no product, patient, appointment, clinical, historical or protected data;
- no production runtime, deployment, release or Pages;
- no protected evidence or protected-ref movement;
- local/origin `master` and `handoff/current` remain fixed at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`;
- preserve `docs/branding/` and every unrelated untracked path; and
- explicit-path staging only; never `git add .` or `git add -A`.
