# DeepSeek native Harness preset-mount sanitizer observable-fixture recovery plan

Date: 2026-08-22

Timestamp: 2026-08-22T05:15:00.4286611+10:00 (Australia/Brisbane)

Status: **frozen recovery before implementation**

Reasoning level: **Extra High** for a distinct replacement process after the
first one-process envelope was consumed without a safe mismatch coordinate.

## Accepted negative evidence

At exact candidate `475a5b6c210a1bc98f75234f544b5c619a94b704`,
attempt 001 launched one local Node fixture process. The fixture returned exit
2 with zero stdout and zero stderr because its internal all-or-nothing
self-check rejected. It started no DeepSeek Harness, imported no DSH package,
made no provider or worker request and wrote no evidence output. The attempt is
consumed and immutable.

## Narrow recovery objective

Remove only the redundant fixture-local expected-code comparison. Attempt 002
will always emit the fifteen sanitizer results as a JSON array whose elements
contain only `stage`, a closed code and null `detail`. Python remains the sole
admission owner and compares those bytes with the frozen expected vector.

If the vector differs, Python may retain one rejected artifact containing only
the fifteen closed codes and their first mismatching index. It must not retain
or emit messages, reasons, paths, stacks, causes, fixture inputs or arbitrary
values. Attempt 002 then stops; this plan grants no third Node process.

## Execution envelope

One distinct local Node process is authorised for attempt 002 after the repaired
fixture, hashes, controller, static tests, exact candidate and origin alignment
are committed. Total local Node fixture processes across the tranche may then
equal two: consumed attempt 001 plus attempt 002. All `--check` and closeout
paths remain non-executing.

## Parallelism assessment

- DeepSeek lane: **declined**. The native Harness remains the governed object
  and cannot be used to repair its own pre-run sanitizer.
- Gemini lane: **declined**. The recovery removes one redundant comparison and
  delegates exact vector admission to deterministic Python; reassess only if
  the safe vector exposes a semantic ambiguity.
- Native-subagent lane: **declined**. Developer policy prohibits delegation and
  the single replacement transaction is serial.
- GPT Sol owns the repair, process observation, admission and recovery stop.

## Acceptance and stop rule

Accept only an exact fifteen-result closed vector, null detail, zero stderr,
one attempt-002 Node process, immutable attempt 001 and zero Harness/provider/
product effects. If attempt 002 does not match, preserve only its safe closed
vector, stop without a third process and derive any further action from that
typed mismatch.

## Explicit exclusions

No DSH/native Harness import or process, runner bridge, retry of attempt 001,
third Node process, worker/model/provider request, raw-detail persistence,
target, product/configuration/API/database/route/adapter/flag/allowlist/grammar/
client/waiting-area change, ordinary-practice enablement, generic-status
`Arrived` change, patient/product/clinical/historical/protected data,
production, deployment, release, Pages, protected evidence or protected-ref
movement is authorised.
