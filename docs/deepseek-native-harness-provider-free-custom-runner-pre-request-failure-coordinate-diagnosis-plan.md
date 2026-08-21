# DeepSeek native Harness provider-free custom-runner pre-request failure-coordinate diagnosis plan

Date: 2026-08-21

Timestamp: 2026-08-21T20:13:19.9793090+10:00 (Australia/Brisbane)

Status: `frozen`

Reasoning level: `high`

## Starting fact

The consumed attempt 005 crossed `sentinel_activated` and
`stock_headless_hmr_ready`, activated the accepted custom runner, then wrote
`CUSTOM_RUNNER_FAILURE` with zero runner and broker requests. Its generic
catch cannot distinguish the runner operation that rejected. The attempt and
its terminal remain immutable and non-resumable.

## Narrow objective

Read the accepted runner and the relevant cached, pinned rc.7 package source;
bind their exact hashes and operation order; then freeze and deterministically
prove a future-only sanitized post-HMR sidecar. The sidecar must report one
machine-selected coordinate from this exact ordered vocabulary:

1. `loader_readiness_wait`
2. `required_service_lookup`
3. `preset_root_roster_admission`
4. `agent_create_setup_publish`
5. `initial_idle_wait`
6. `first_followup_dispatch`
7. `first_turn_idle_wait`

These are source coordinates, not natural-language diagnoses. The final
coordinate is still request-adjacent: only a separate broker reading of zero
requests may support a pre-request conclusion.

## Source facts to bind

- The runner awaits the loader, reads `agents`, `sessions` and `agentPresets`,
  admits the exact two-root roster, awaits `agents.create({setup})`, awaits
  initial idle, dispatches one follow-up and awaits the first turn idle.
- rc.7 `dsh-agent` delegates `agents.create` to the registered factory.
- rc.7 `dsh-agent-loop` prepares a session, awaits setup before publication,
  starts the loop, supplies synchronous `followup`, and provides the stable
  `whenIdle` boundary.
- rc.7 `dsh-agent-presets` resolves, mounts and binds the selected preset
  inside setup.
- rc.7 `dsh-session` owns the later flush boundary, which is deliberately
  outside this pre-request sidecar vocabulary.

## Diagnostic contract

The future sidecar contains only fixed schema/identity fields, one admitted
stage, one admitted cause coordinate, one admitted error kind and fixed false
raw-retention declarations. The closed cause coordinates are
`operation_rejected`, `required_service_missing`, and
`preset_root_roster_mismatch`. The error-kind vocabulary is `error`,
`type_error`, `aggregate_error`, `preset_mount_error`,
`unknown_preset_error`, `invalid_preset_id_error`, or `unknown`.

The helper may inspect only an error's constructor/name identity. It may not
read or retain a message, code, stack, path, cause, environment value, stream,
session, prompt, response or credential. It writes once with exclusive-create
semantics inside the exact disposable root, suppresses diagnostic-write
failure, and rethrows the identical runner rejection. The controller must
validate canonical bytes and identity before embedding the projection in any
future terminal.

## Implementation and proof

The tranche may add one deterministic diagnostic component, a future runner
instrumentation envelope, exact contract/schema/evidence/report artifacts and
focused hostile tests. It must not alter the accepted runner or any consumed
attempt. Python may read cached package tarballs offline and execute fixture
tests; Node, native Harness, broker, worker, model, provider, network,
database and Docker process counts remain zero.

Hostile cases cover every admitted stage/kind/cause, unknown names, extra or
missing fields, shortened Git IDs, raw-retention flags, dynamic secret/path
text, non-canonical bytes, oversize, symlink and identity mismatch. Any
uncertainty must become `unknown`, `operation_rejected`, sidecar rejection or
fallback to the existing generic terminal.

## Acceptance

- The accepted runner hash/order and all four relevant pinned rc.7 source
  hashes/fragments pass.
- One vocabulary constant owns Python validation, generated helper source,
  schema values and evidence; no caller-authored descriptive stage is
  accepted.
- The future runner envelope assigns every stage immediately before its exact
  operation, writes at most one safe sidecar, and rethrows identically.
- Sidecar validation is exact-key, full-OID, canonical, size-bounded,
  path-contained and raw-retention denying.
- Deterministic evidence and focused tests pass with zero prohibited process,
  request and raw-attempt-stream counts.

## Parallelism assessment

- DeepSeek Flash: `declined`, negative leverage. Any Harness, worker, model or
  provider activity violates this diagnosis boundary.
- Gemini 3.7 Flash/high: `declined`, negative leverage. Provider-free static
  source and hostile-fixture evidence own the decision; reassess only for a
  separately admitted future candidate or occupied proof.
- Native subagents: `declined`, negative leverage. Developer policy prohibits
  proactive delegation and the source mapping, vocabulary and sidecar are one
  tightly coupled serial surface.
- GPT Sol owns source inspection, contract freeze, implementation, tests,
  acceptance and closeout.

## Explicit non-authority

No occupied retry, Harness/broker/worker/model/provider request, product or
configuration change, ordinary-practice enablement, generic-status `Arrived`
change, product/patient/clinical/protected data, production runtime,
deployment, release, Pages or protected-ref movement is authorised. Preserve
`docs/branding/` and every unrelated untracked file; stage explicit paths
only.
