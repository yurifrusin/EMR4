# DeepSeek native Harness preset-mount sanitizer typed-process-envelope recovery plan

Date: 2026-08-22

Timestamp: 2026-08-22T05:21:00.2786709+10:00 (Australia/Brisbane)

Status: **frozen recovery before implementation**

Reasoning level: **Extra High** for the final bounded process diagnostic after
two consumed local fixture processes.

## Accepted negative evidence

- Attempt 001 at `475a5b6c210a1bc98f75234f544b5c619a94b704`
  executed the fixture far enough to select its internal exit 2 but emitted no
  stream.
- Attempt 002 at `50a17beba7ea3a461cc2dd2154f747b307119f20`
  removed that self-check yet reached the controller terminal
  `node_fixture_exit_nonzero`. The controller did not retain the numeric exit
  or stream lengths, so no narrower factual coordinate is claimed.

Both attempts are consumed. Neither imported or started the DeepSeek Harness,
made a provider/worker request, connected a runner or wrote product data.

## Narrow recovery objective

Make process observation precede semantic admission. One final attempt 003 may
run a repository-local wrapper that:

1. dynamically imports only the exact hash-bound sanitizer module by its fixed
   relative specifier;
2. emits either the fifteen three-field safe terminals or one three-field
   wrapper terminal from this closed vocabulary:
   `SANITIZER_MODULE_IMPORT_REJECTED` or
   `SANITIZER_MATRIX_EVALUATION_REJECTED`; and
3. never emits an exception, message, stack, reason, path or input detail.

The Python controller must first persist a content-free process envelope with
the numeric exit code, stdout/stderr byte counts and SHA-256 digests. It then
admits an exact success vector or a closed wrapper terminal. It never persists
stream content. A nonzero process exit, unsafe output or wrapper terminal stops
the tranche with no fourth-process authority.

## Execution envelope

Exactly one attempt-003 local Node process is authorised after the wrapper,
controller, hashes, tests and exact candidate/origin alignment are committed.
The only dynamic import permitted is the fixed relative sanitizer specifier;
there is no DSH, package, environment, filesystem API, child-process or network
access. Total local Node fixture processes may become three.

## Parallelism assessment

- DeepSeek lane: **declined**. The native Harness remains the governed object;
  it cannot diagnose its own pre-run sanitizer.
- Gemini lane: **declined**. The wrapper and content-free envelope are exact
  deterministic control surfaces; reassess only if attempt 003 yields a closed
  semantic ambiguity.
- Native-subagent lane: **declined**. Developer policy prohibits delegation and
  this last process transaction is serial.
- GPT Sol owns implementation, execution, admission and the hard stop.

## Acceptance and stop rule

Accept only the exact fifteen-result vector, attempt-003 exit 0, zero stderr,
exact stdout bytes, immutable attempts 001/002, a content-free envelope and
zero Harness/provider/product effects. Any other terminal stops without a
fourth Node process. The wrapper is diagnostic scaffolding, not runner code.

## Explicit exclusions

No fourth Node process, DSH/native Harness import or process, runner bridge,
repair/retry authority, worker/model/provider request, stream-content or raw-
detail persistence, target, product/configuration/API/database/route/adapter/
flag/allowlist/grammar/client/waiting-area change, ordinary-practice
enablement, generic-status `Arrived` change, patient/product/clinical/
historical/protected data, production, deployment, release, Pages, protected
evidence or protected-ref movement is authorised.
