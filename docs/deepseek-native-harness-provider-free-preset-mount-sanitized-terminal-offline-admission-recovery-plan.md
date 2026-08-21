# DeepSeek native Harness preset-mount sanitized-terminal offline-admission recovery plan

Date: 2026-08-22

Timestamp: 2026-08-22T07:16:44.5979213+10:00 (Australia/Brisbane)

Status: **frozen recovery before implementation**

Reasoning level: **Extra High** for recovery of one consumed native process
without another native, worker, model or provider process.

## Accepted incident state

The only authorised native rc.7 process is consumed at exact candidate
`c1ae13df334dfdffefb229c3ae5a502a7251451c`. It produced no retained stdout or
stderr and the content-free process envelope records one process, zero retries,
zero resumes, a 1,646-byte sidecar and sidecar SHA-256
`e76534cfe263a0d4239182338d5fdbe2515669fd4dd258107b94e1cf338f7eb4` before
semantic admission.

The retained sidecar is a bounded typed object. Its schema-version token names
the accepted preset-composition predecessor rather than the successor schema,
although its operation, attempt, source, hashes and successor fields are
present. Admission therefore failed closed. The controller then attempted to
rewrite the immutable sidecar-seen envelope as sidecar-absent, which failed
closed before canonical evidence and exact disposable-root cleanup.

There is no evidence of an uncontrolled Harness process: the owned Node process
count is zero. Exactly one retained root named with the frozen
`dsh-agent-factory-diagnostic-` prefix remains under the accepted disposable
parent.

## Narrowest recovery objective

Recover the consumed attempt entirely offline. The recovery controller must:

1. bind the exact attempt-consumed record and content-free process envelope;
2. require exactly one non-symlink retained root under the accepted disposable
   parent and prove no Node process command line owns that exact root;
3. locate exactly one sidecar at the accepted bundle-relative coordinate and
   require its byte count and digest to equal the immutable envelope;
4. admit the actual closed sidecar shape with the predecessor schema token,
   successor `preset_mount_terminal` field and exact operation/attempt/source/
   source-hash/counter semantics;
5. persist only a closed typed projection before cleanup, never a raw message,
   error, stack, cause, path, stream, environment or credential;
6. verify the exact readiness sequence, zero network ledger, zero broker
   counters, unchanged materialized runner/guard/bridge/sanitizer hashes and
   absent target from retained files;
7. remove only the exact verified retained root and then persist a recovery
   evidence/report; and
8. classify the native result honestly as
   `preset_composition_failure_attributed` at
   `EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED`, with the new preset-mount bridge
   runtime path **not proved**.

The recovery also repairs the controller source for future use: a rejected
sidecar must not be converted into a contradictory sidecar-absent envelope, and
runner-source validation must bind the emitted schema token. Those source
repairs do not retroactively alter the consumed candidate.

## Parallelism assessment

- DeepSeek lane: **declined**. Its sole native process is the evidence being
  recovered; another Harness or model invocation would violate the latch.
- Gemini lane: **declined**. Digest equality, schema shape, closed terminal
  semantics and exact-root cleanup are deterministic and have no unresolved
  product judgment.
- Native-subagent lane: **declined**. Developer policy prohibits delegation,
  and cleanup of the one retained root requires one serial owner.
- GPT Sol owns implementation, deterministic verification, offline execution,
  cleanup, closeout and the next-plan decision.

## Acceptance and stop rule

Accept only a zero-native-process recovery whose admitted projection matches the
immutable envelope and retained sidecar, whose required counters are zero, and
whose exact disposable root is absent after execution. No retry or resume is
authorised. Any digest, schema, fixed binding, process-absence or cleanup
mismatch stops without deletion and requires Yuri's attention only if no
further safe read-only diagnosis exists.

## Explicit exclusions

No Node or native Harness process, worker/model/provider request, retry, resume,
raw runtime detail, product/configuration/API/database/route/adapter/flag/
allowlist/grammar/client/waiting-area change, ordinary-practice enablement,
generic-status `Arrived` change, patient/product/clinical/historical/protected
data, production, deployment, release, Pages, protected evidence or
protected-ref movement is authorised.

