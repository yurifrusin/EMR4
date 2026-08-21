# DeepSeek native Harness provider-free proof-module relative-specifier repair plan

Date: 2026-08-21
Timestamp: 2026-08-21T13:41:11.0607422+10:00 (Australia/Brisbane)
Status: `frozen`
Reasoning level: `high`

## Objective

Replace the generated sentinel and later runner module names in the bounded
worker profile with the exact profile-relative specifiers already proven by the
accepted rc7 complete-composition predecessor. Add deterministic regression
evidence while keeping Node, Harness, broker, worker, model, provider and
network activity at zero.

## Accepted predecessor and repair coordinate

- accepted diagnosis source:
  `f735e6c9f4412aea8e83e410c0292668ebe7853f`;
- accepted clockwork diagnosis source:
  `a166c96d35c9200b33d7bd2ec4e492d0a374d57c`;
- current output forms:
  `name: {quoted(proof / "sentinel.mjs")}` and
  `name: {quoted(proof / "runner.mjs")}`;
- required output forms:
  `name: ../../../installation/proof/sentinel.mjs` and
  `name: ../../../installation/proof/runner.mjs`; and
- accepted predecessor evidence SHA-256:
  `9ba784b0726addb5644ac3786def410aed56e5bf9da3e23ec21d8e10f6ba1ea0`.

## Exact implementation allowance

The behavioral diff is exactly two YAML `name` rows in
`profile_patch(...)`. The now-unused local `proof` path assignment may be
removed as mechanical dead-code fallout. Tests and provider-free evidence may
be added. No other emitted profile row, validation rule, runner source,
controller behavior, tool/preset contract, retry rule or product source may
change.

## Deterministic proof

The repair runner and tests must prove:

1. the target source contains each required relative specifier exactly once;
2. neither target uses `quoted(proof / ...)` or an absolute Windows module
   name;
3. the initial generated profile contains sentinel exactly once and no runner;
4. the changed generated profile contains sentinel and runner exactly once;
5. replacing the two repaired rows with their accepted predecessor forms is
   the complete behavioral diff, apart from the dead local removal;
6. all pre-existing bounded profile invariants still validate; and
7. Node, Harness, broker, worker, model, provider and network counts remain
   zero.

Any extra output drift, missing or duplicate relative specifier, retained
absolute target form, execution entry point or input-binding mismatch returns
`failed_closed` and authorises no boot proof.

## Parallelism assessment

- **DeepSeek Flash:** declined, negative leverage. The latch forbids model and
  provider activity and the repair has no separable model work package.
- **Gemini 3.7 Flash/high:** declined, negative leverage. The latch forbids
  provider review; the semantic change is mechanically bound to an already
  passing predecessor. Reassess for a separately frozen boot proof.
- **Native subagents:** declined, negative leverage. Developer policy forbids
  proactive delegation and the two coupled rows have one serial owner.
- **GPT Sol:** owns the exact edit, static proof, acceptance and closeout.

## Acceptance

Accept only when the exact diff, focused regression, widened profile tests,
JSON Schema, Ruff, Python compilation and `git diff --check` pass; the evidence
reports `passed`; and all forbidden activity counters are zero. This accepts a
provider-free profile repair only. It does not prove native boot, DeepSeek
reachability, worker reliability or EMR4 development readiness.

## Protected boundaries

- provider-free two-row profile repair only;
- no Node, Harness, broker, worker, model, provider or network process/request;
- no retry, resume, fallback, second worker or occupied attempt;
- attempts 001-004 and all terminal/consumed evidence remain immutable;
- no raw message, code, stack, path, stream, session or credential
  reconstruction;
- no product/configuration/API/database/route/adapter/flag/allowlist/grammar/
  client/waiting-area change outside the generated Harness profile rows;
- no ordinary-practice enablement or generic-status `Arrived` change;
- no product, patient, appointment, clinical, historical or protected data;
- no production runtime, deployment, release, Pages or protected-ref movement;
- local/origin `master` and `handoff/current` remain fixed at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`;
- preserve `docs/branding/` and every unrelated untracked file; and
- explicit-path staging only; never `git add .` or `git add -A`.
