# DeepSeek native Harness preset-mount sanitizer Windows minimum-environment recovery plan

Date: 2026-08-22

Timestamp: 2026-08-22T05:27:53.1609563+10:00 (Australia/Brisbane)

Status: **frozen before implementation**

Reasoning level: **Extra High** for the narrow launch-envelope repair after a
three-process failed-closed lineage.

## Objective

Replace only the sanitizer controller's empty Windows child environment with a
validated five-key operating-system minimum: `SystemRoot`, `WINDIR`, `ComSpec`,
`TEMP` and `TMP`. Run the unchanged exact-hash sanitizer and typed import
wrapper once, retaining the content-free process envelope before admission.

## Accepted basis

The sanitizer lineage consumed three local Node processes. Attempt 003 at exact
candidate `03a53c5b6f5e487b991e465a73c6368aa9759d74` observed exit 134, zero stdout
and 715 stderr bytes while retaining no stream content. All three attempts used
the unique launch override `env={}`. Accepted repository Node fixture
rehearsals inherit their host process environment. This supports testing the
empty-environment boundary; it does not yet prove it caused the abort.

## Frozen implementation

- Preserve the sanitizer and wrapper bytes exactly.
- Replace `env={}` with a function that requires the five named variables,
  returns exactly those keys and no others, and never persists their values.
- Deny `PATH`, `NODE_OPTIONS`, credentials, provider configuration and every
  unlisted variable.
- Bind key presence and the exact five-key set in Python tests.
- Run one exact candidate/origin-aligned local Node process.
- Persist numeric exit, stream lengths and digests before semantic admission;
  never persist stream content.

## Parallelism assessment

- DeepSeek lane: **declined**. The Harness is still the governed object and no
  worker/model process is allowed.
- Gemini lane: **declined**. The five-key environment projection and exact
  wrapper readback are deterministic; reassess only if the result creates a
  genuine semantic ambiguity.
- Native-subagent lane: **declined**. Developer policy prohibits delegation and
  the one-process environment repair is serial.
- GPT Sol owns implementation, execution, readback and closeout.

## Acceptance and stop rule

Accept only exit 0, zero stderr, the exact fifteen-result safe vector, one local
Node process in this successor, a content-free process envelope, unchanged
sanitizer/wrapper hashes and zero Harness/provider/product activity. Any other
result stops without another process under this plan.

## Explicit exclusions

No DSH/native Harness import or process, model/worker/provider request, full
environment inheritance, `PATH`, `NODE_OPTIONS`, credential or secret access,
runner bridge, repair/retry authority, target, product/configuration/API/
database/route/adapter/flag/allowlist/grammar/client/waiting-area change,
ordinary-practice enablement, generic-status `Arrived` change, patient/product/
clinical/historical/protected data, production, deployment, release, Pages,
protected evidence or protected-ref movement is authorised.
