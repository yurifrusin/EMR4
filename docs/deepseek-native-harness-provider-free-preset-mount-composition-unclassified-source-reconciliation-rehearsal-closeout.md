# DeepSeek native Harness preset-mount composition-unclassified source reconciliation closeout

Date: 2026-08-22

Timestamp: 2026-08-22T08:26:47.0343827+10:00 (Australia/Brisbane)

Status: **accepted process-free deterministic source attribution**

Reasoning level: **Extra High**

## Result

At exact implementation source
`ab2018091ee40fa8833f957daf41085a83f6b41d`, the process-free controller bound
the accepted generated runner, guard, preset-mount bridge and sanitizer plus
the installed rc.7 agent-loop, scope and preset-service sources. All thirteen
required source coordinates passed and the closed result is
`root_preset_service_not_forwarded_before_bridge`.

The exact control path is:

- the runner declares and resolves the root `agentPresets` service as
  `presets`;
- the installed agent loop gives setup a private context derived from its own
  narrower dependency surface, which does not declare `agentPresets`;
- the runner does not forward its admitted `presets` handle into the guard;
- the guard evaluates `agentCtx.agentPresets.mount.bind(...)` while building
  the bridge arguments, before the bridge body can sanitize the boundary; and
- the broader sanitizer maps the resulting uncoded escape to the observed
  `EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED` terminal.

This is a deterministic source explanation sufficient for the consumed broad
terminal. It is not a reconstruction of the exact runtime exception or
private-context value.

## Control gain

The failure is no longer an unexplained native-Harness outcome. Ariadne can now
name the exact interface seam that bypassed the typed preset-mount gear. The
narrowest prospective correction is to forward the already admitted root
preset service explicitly into the guard and validate the mount handle inside
the bridge.

That correction was not applied here. The new bridge runtime path remains
unproved, and no retry is authorised by this result.

## Evidence and verification

- The immutable source evidence is bound to exact candidate
  `ab2018091ee40fa8833f957daf41085a83f6b41d` and has zero failed coordinates.
- The focused nine-test file passed.
- The broader native/recovery/bridge/source/guard/latch/Current-Baton suite
  passed with one platform-specific directory-symlink skip.
- The pre-verifier Ariadne receipt passed with the complete five-source
  rehydration and fixed protected refs.
- Ruff, `py_compile`, JSON Schema validation and Git whitespace checks passed.
- Node, native Harness, worker, model and provider processes, requests, retries
  and resumes remained zero.

Clockwork closeout records the machine-object-ID, direct-script import-path and
Markdown-soft-wrap assertion corrections as AER-0908 through AER-0910. The
first is the exact class of clerical binding that the governance mechanism must
continue removing from caller-authored contracts.

## Parallelism disposition

- DeepSeek: declined because the Harness/worker was the governed object and
  the tranche authorised no process or self-review.
- Gemini: declined because a provider process was outside the frozen boundary
  and all thirteen deterministic source coordinates passed with a narrow claim.
- Native subagents: declined under current developer policy.
- GPT Sol owned the serial source attribution and acceptance.

## Next tranche

Proceed with
`deepseek-native-harness-provider-free-preset-mount-root-service-forwarding-process-free-correction-rehearsal`.
It may prospectively derive a runner/guard/bridge composition that passes the
already admitted root preset-service handle explicitly and moves mount-handle
validation inside the typed bridge. It may not start Node, the native Harness,
a worker, a model or a provider, and it may not retry the consumed attempt.

## Boundaries

No exact runtime exception was recovered; no native bridge execution, occupied
DeepSeek worker quality, retry, product/configuration/API/database/route/
adapter/flag/allowlist/grammar/client/waiting-area change, ordinary-practice
enablement, generic-status `Arrived` change, patient/product/clinical/
historical/protected data, production, deployment, release, Pages, protected
evidence or protected-ref movement is accepted.
