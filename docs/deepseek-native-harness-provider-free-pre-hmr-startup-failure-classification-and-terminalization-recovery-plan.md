# DeepSeek native Harness provider-free pre-HMR startup-failure classification and terminalization recovery plan

Date: 2026-08-20

Timestamp: 2026-08-20T23:23:58.3235077+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`deepseek-native-harness-provider-free-pre-hmr-startup-failure-classification-and-terminalization-recovery`

Reasoning level: High. The active latch already freezes the provider-disabled,
non-product and no-worker boundary; this plan adds the narrow deterministic
mechanism needed to satisfy it without revising authority or acceptance meaning.

Machine-bound planning source:
`orchestration/agent_inbox/codex/deepseek-native-harness-pre-hmr-startup-recovery-preplanning-corrected-receipt.json`.

## Purpose

Repair the outer native-Harness controller so a future startup failure before
the first HMR event cannot collapse into only a generic process exit plus raw
stream digests. While the local raw stdout and stderr bytes still exist, the
controller will derive one closed sanitized stage/cause reading, write it
exclusively outside the disposable attempt root, validate it, and only then
delete the raw streams with the root.

This tranche is entirely provider-disabled. It launches no native Harness,
worker, broker, DeepSeek, Gemini or other provider process. It does not retry,
resume, reclassify or overwrite attempts 001 or 002.

## Accepted negative floor

- Attempt 001 is immutable, consumed and provider-free. Its initiating
  controller/broker digest failure and cleanup masking are separately retained.
- Attempt 002 is immutable and consumed after exactly one native process. It
  exited `1` after 11,214 ms with zero HMR events, zero runner events, zero
  provider requests, zero tools and zero file changes.
- Attempt 002 retained 7,314 stderr bytes only as a SHA-256 digest and length.
  Their content was deleted; the exact semantic cause is unproved and must not
  be reconstructed.
- The clockwork closeout passes at Continuity 353 / Compass 335 with canonical
  drift 0, dual ownership 0 and no open register incident.

## Exact implementation boundary

### 1. Closed outer-controller terminal

Add a pure reusable startup-terminal component and bind it into the existing
authored-synthetic controller. It accepts only controller-observed facts:

- whether native process creation succeeded;
- its integer exit code or a closed controller exception coordinate;
- the exact zero-event precondition;
- bounded raw stdout/stderr bytes while they remain local;
- byte counts and SHA-256 digests; and
- operation, attempt and candidate identifiers already admitted by the
  checkpoint.

It emits no raw line, exception message, path, environment value, prompt,
response, reasoning or credential.

### 2. Closed stage vocabulary

Exactly two pre-HMR stages are admitted:

- `native_process_creation`; and
- `native_process_started_before_first_hmr_event`.

Any observed HMR event rejects this component as out of scope. Post-event
startup, runner and provider terminals remain owned by their existing layers.

### 3. Closed cause vocabulary

The component admits only:

- `node_runtime_contract_rejected`;
- `package_entrypoint_load_failed`;
- `profile_load_or_validation_failed`;
- `module_resolution_failed`;
- `required_service_unavailable`;
- `hmr_bootstrap_failed`;
- `operating_system_process_failure`;
- `controller_startup_exception`;
- `startup_stream_limit_exceeded`;
- `ambiguous_startup_signatures`; and
- `unclassified_nonzero_exit`.

Classification uses exact fixed case-insensitive byte signatures grouped by
cause. Zero matched groups produces `unclassified_nonzero_exit`; more than one
matched group produces `ambiguous_startup_signatures`. No precedence rule may
turn ambiguous text into a stronger causal claim. Process-creation and closed
controller-exception facts do not depend on stderr text.

### 4. Bounded raw-stream handling

Hash and count each local stream incrementally. Retain at most 64 KiB per stream
in memory for signature matching. If either stream exceeds that bound, the
cause is `startup_stream_limit_exceeded`; no truncated content is assigned a
semantic cause. The durable terminal contains only counts, digests and safe
enums. Raw files remain inside the exact disposable root and are removed after
terminal validation.

### 5. Ordering and exclusivity

The future occupied order is fixed:

1. observe the failed pre-HMR lifecycle;
2. stop the exact owned process tree;
3. close and incrementally read the local streams;
4. derive and schema-validate the sanitized terminal;
5. write it with exclusive-create semantics outside the disposable root;
6. read it back and verify its canonical digest;
7. remove the exact disposable root and raw streams; and
8. publish the ordinary outer terminal referencing only the sanitized terminal
   digest and cleanup state.

A stale terminal path is a prelaunch refusal. A terminal write/readback failure
cannot be called successful recovery. Secret-deletion remains dominant in an
exceptional filesystem failure, but the future occupied attempt must then fail
closed and cannot be accepted or retried.

## Deterministic evidence

Provider-free tests must cover:

- every admitted stage and cause;
- every fixed signature group independently;
- zero signatures, duplicate signatures and cross-group ambiguity;
- binary, malformed UTF-8, mixed case and secret-looking hostile bytes;
- stream-length boundary, over-limit and incremental digest equality;
- any HMR event, successful exit, non-integer exit and unknown controller
  coordinate rejection;
- exact terminal keys, schema, canonical digest and exclusive-write/readback;
- stale output, second writer, escaped output path and disposable-root output
  rejection;
- ordering that proves terminal validation precedes root removal;
- attempts 001 and 002 byte immutability; and
- zero subprocess, worker, broker or provider invocation.

The evidence artifact must report scenario counts, mutation counts, admitted
vocabulary, source/schema digests, zero-process/zero-provider posture and an
efficacy reading comparing the old generic terminal with the new bounded
coordinate.

## Acceptance and claim boundary

The tranche passes only if the pure component, controller binding, schemas and
hostile fixtures pass; the existing attempt-002 evidence remains byte-identical;
the test suite proves zero native/provider process; and the future ordering
cannot delete raw streams before an exclusive sanitized terminal is validated.

A pass proves only that future pre-first-HMR failures can be recorded with a
bounded, non-secret stage/cause coordinate instead of a generic exit. It does
not establish the cause of attempt 002, make the Harness reliable, demonstrate
DeepSeek performance, authorize another occupied attempt or admit EMR4 product
work.

## Parallelism assessment

- **DeepSeek Flash:** `not_applicable`, neutral leverage. The latch prohibits a
  worker or provider request.
- **Gemini 3.7 Flash/high:** `not_applicable`, neutral leverage. The latch
  prohibits every provider request; deterministic hostile fixtures own the
  complete acceptance surface.
- **Native subagents:** `declined`, negative leverage. Developer policy
  prohibits proactive delegation and classification, terminal ordering and
  cleanup are one coupled serial repair.
- **GPT Sol:** owns plan, implementation, deterministic validation, acceptance,
  clockwork and Git.

## Deliberately closed

No native worker, DeepSeek, Gemini or other provider request; no new occupied
attempt, retry, resume, fallback or second worker; no raw-stream retention; no
product source/configuration, API, OpenAPI, GraphQL, schema, migration, route,
adapter, feature flag, allowlist, command grammar, first-party client or
waiting-area change; no ordinary-practice enablement or generic-status
`Arrived`; no product, patient, appointment, clinical, historical or protected
data; no Docker, PostgreSQL, SQL or transaction execution; no production,
deployment, release, Pages or protected-ref movement.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage explicit paths only; never use
`git add .` or `git add -A`.
