# DeepSeek native Harness preset-mount root-service-forwarding process-free correction rehearsal plan

Date: 2026-08-22

Timestamp: 2026-08-22T08:47:30.5660782+10:00 (Australia/Brisbane)

Status: **frozen before implementation**

Reasoning level: **Extra High** for a prospective correction across the native
runner, guard and typed preset-mount bridge boundary.

## Objective

Derive, without executing JavaScript, a prospective native-Harness runner,
effective-tool guard and preset-mount bridge in which the runner's already
admitted root preset service is an explicit typed input and every read,
validation and invocation of its mount handle occurs inside the bridge.

Emit one hash-bound closed correction result or fail closed. Start no Node,
native Harness, worker, model or provider process and modify none of the
accepted source owners.

## Accepted basis

The accepted process-free source reconciliation proves
`root_preset_service_not_forwarded_before_bridge` at implementation source
`ab2018091ee40fa8833f957daf41085a83f6b41d`. The accepted runner already
declares and resolves root `agentPresets` as `presets`; the installed agent-loop
setup context has a narrower dependency surface; and the current guard
dereferences `agentCtx.agentPresets.mount.bind(...)` before entering the typed
bridge. The clockwork accepts that reading at source
`a6341f9225e3453529e70f6b75a45aec484d8f0e`, Continuity 386 / Compass 368.

The consumed native attempt, accepted offline recovery and source-
reconciliation evidence remain immutable and grant no retry.

## Frozen source inventory

The controller may read and bind only:

- the accepted generated runner and guard bytes returned by the existing
  runner-bridge source owners;
- the accepted preset-mount bridge and safe-subcoordinate sanitizer bytes;
- the installed rc.7 preset-service member already bound by the accepted
  package-only seed;
- the accepted source-reconciliation contract and evidence;
- this plan and its threat-model delta; and
- `orchestration_harness/git_object_resolution.py` for machine-only commit
  resolution.

The installed seed is read-only. No accepted Python or JavaScript source owner
may be patched by this tranche.

## Exact prospective correction

The derivation must apply each anchor exactly once and prove the following
closed shape:

1. the runner retains exactly one root `agentPresets` injection declaration
   and exactly one `const presets = ctx.get("agentPresets");` resolution;
2. the runner calls
   `assertEffectiveToolComposition(agentCtx, presets, PRESET_ID, TOOLS)`
   exactly once and contains no old three-argument call;
3. the guard signature becomes
   `assertEffectiveToolComposition(agentCtx, presetService, presetId,
   requiredTools)` exactly once;
4. the guard passes `presetService` into `mountWithSanitizedTerminal` and
   contains no `agentCtx.agentPresets` dereference, mount binding or root
   service lookup;
5. the bridge accepts `presetService`, `agentCtx`, `presetId` and
   `PresetMountError`, and no caller-supplied `mount` function;
6. stable validation of `agentCtx`, `presetId` and `PresetMountError` remains
   fail closed before the bridge's `try`;
7. inside that `try`, the bridge validates that `presetService` is an object or
   function, reads `const mount = presetService.mount`, validates that local
   handle as a function and invokes
   `await mount.call(presetService, agentCtx, presetId)`;
8. service or mount-handle rejection is caught by the bridge and reduced by
   the accepted sanitizer to the exact content-free
   `PRESET_MOUNT_UNCLASSIFIED` terminal;
9. admitted `PresetMountError` failures retain the accepted safe-code mapping,
   successful mounting retains `{ passed: true, terminal: null }`, and the
   guard retains the accepted `PresetMountSanitizedTerminalError` handoff; and
10. no generated source contains prompt, response, raw message, stack, cause,
    path, environment or credential release logic.

The controller records the exact input and derived byte counts and SHA-256
digests plus an ordered predicate reading. It does not materialize or execute
the derived JavaScript.

## Machine-only Git binding

The tranche contract contains no caller-authored Git object ID. It records only
the closed policy `machine_resolved_only` and the plan path. At evidence time
the controller must:

- ask Git for the commit that last changed the frozen plan path;
- pass that result through
  `orchestration_harness.git_object_resolution.resolve_commit_source`;
- obtain the current candidate from the same resolver and machine Git
  snapshot; and
- record only the resolver's full 40-character results in evidence.

Any missing, abbreviated, caller-supplied, non-commit or non-ancestor binding
returns `source_binding_rejected`. The contract schema and tests must reject a
Git-ID field or any embedded 40-character hexadecimal identity in the caller-
authored contract.

## Closed result vocabulary

- `root_service_forwarding_correction_admitted`
- `prospective_source_derivation_rejected`
- `source_binding_rejected`

No descriptive substitute is accepted. A changed source digest, missing or
repeated rewrite anchor, forbidden old call/dereference, predicate-order
failure, Git-resolution failure or prohibited process observation fails closed
without repair or retry.

## Acceptance

Acceptance requires:

- a schema-valid contract with no authored object ID;
- exact accepted input byte/hash bindings;
- every runner, guard and bridge predicate above true in the required order;
- exact derived byte/hash bindings and zero failed coordinates;
- focused tests covering each rejected anchor, old-call/dereference survival,
  validation placement, terminal precedence and contract Git-ID exclusion;
- direct CLI, Ruff, `py_compile`, JSON Schema and relevant governance suites
  passing; and
- zero Node/native-Harness/worker/model/provider processes, requests, retries
  and resumes.

This proves only a prospectively coherent source correction. It does not prove
JavaScript evaluation, native-Harness boot, preset mounting, a DeepSeek turn,
model/provider access or worker quality.

## Parallelism assessment

- DeepSeek: **declined**. The worker and native Harness are the governed path;
  any process or self-review violates the correction latch.
- Gemini: **declined provisionally**. The correction has exact source anchors,
  ordered predicates and a closed verdict. Reassess before acceptance only if
  deterministic verification leaves a material semantic ambiguity.
- Native subagents: **declined**. Current developer policy prohibits
  delegation, and the three-source derivation is serial.
- GPT Sol owns planning, implementation, deterministic verification and
  acceptance.

## Recovery and next coordinate

A failed source binding or derivation stops with its closed result; this
tranche does not patch an accepted source owner or start a recovery process.
After acceptance, the narrowest dependency-satisfied successor is a separately
frozen provider-free isolated Node-fixture rehearsal of the derived source.
That later fixture may prove JavaScript behavior but still grants no native
Harness, worker, model, provider or product authority.

## Explicit exclusions

No Node/native-Harness/worker/model/provider process, retry, resume, accepted-
source mutation, installed-seed mutation, target or product-source change,
configuration/API/database/route/adapter/flag/allowlist/grammar/client/
waiting-area change, ordinary-practice enablement, generic-status `Arrived`
change, patient/product/clinical/historical/protected data, production,
deployment, release, Pages, protected evidence or protected-ref movement is
authorised.
