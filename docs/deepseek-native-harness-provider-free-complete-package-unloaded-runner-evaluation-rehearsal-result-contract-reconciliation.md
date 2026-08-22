# Complete package-unloaded runner result-contract reconciliation

Date: 2026-08-22

Status: frozen process-free recovery

Parent operation: `deepseek-native-harness-provider-free-complete-package-unloaded-runner-evaluation-rehearsal`

## Consumed result

Attempt `attempt-001` is immutable and must not be retried. Its content-free
envelope records:

- one Node process;
- numeric exit code zero;
- zero stderr bytes;
- one 129-byte stdout line with SHA-256
  `f868b3fff25a29d8bdd822e0675ffff1bb92363f20ac19bcaf674d85701df49a`;
- one 1,567-byte runner sidecar with SHA-256
  `841881411f203dc5f02f5b785bb5aa3a754f8663517e0145d95fc1376e5ea1a3`;
- complete disposable-root cleanup; and
- zero installed-package, native-Harness and worker/model/provider activity.

The original controller then emitted the closed
`complete_runner_result_rejected` terminal.

## Exact controller error

The fixture source writes the frozen fields in this declared order:

1. `schema_version`
2. `result`
3. `app_exit_code`

The validator incorrectly compared those wire bytes with a generic canonical
serializer that alphabetically sorts object keys. Both representations contain
the same field/value object and are 129 bytes, but have different hashes. The
observed stdout hash is exactly the independently derived hash of the declared
fixture wire order. The observed sidecar hash and byte count are already exact.

This is an evidence-controller contract error after a successful runner
process, not a runner, guard, bridge, sanitizer, stub, package-resolution or
cleanup failure.

## Authorised recovery

One process-free reconciliation may:

1. bind the immutable envelope and failure terminal;
2. machine-resolve the consumed candidate commit from the original controller;
3. derive the exact fixture wire bytes from the frozen fixture source and exact
   result object without reading retained stdout content;
4. derive the exact ordered sidecar bytes from the frozen runner contract;
5. require both byte counts and hashes to equal the immutable envelope;
6. require exit zero, stderr zero, cleanup and every closed counter;
7. write a typed reconciliation evidence object and report; and
8. accept the complete package-unloaded runner only as a reconciled pass.

No Node process, retry, installed-package import, native Harness, DeepSeek
worker, model/provider/broker/network request, target, product/data action,
production, deployment, release, Pages or protected-ref movement is authorised.

If any immutable binding, byte count, hash, Git identity, cleanup field or zero
counter differs, reconciliation fails closed and Yuri's attention becomes
required. If it passes, close the parent operation and advance directly to the
bounded occupied useful Raisa worker promised by the frozen convergence rule.
