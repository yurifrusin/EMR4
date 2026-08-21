# Sol acceptance: preset-mount sanitizer Windows minimum environment

Date: 2026-08-22

Timestamp: 2026-08-22T06:03:42.6115665+10:00 (Australia/Brisbane)

Decision: **accepted at the deterministic sanitizer boundary**

I accept the exact execution candidate
`ceac8b2600530bf858394bb84e66a42ec3d016f4` and its immutable evidence:
one five-key local Node fixture process, exit 0, zero stderr, the exact fifteen
closed results, unchanged sanitizer/wrapper hashes, and no retained stream or
environment content.

The acceptance is deliberately non-transferable. It admits
`sanitizePresetMountError` as a pure bounded projection under the reviewed
fixture. It does not admit the runner, DSH, a native Harness process, a worker,
a model/provider request, a retry, an occupied turn or any product authority.

The dependency-satisfied successor is a deterministic runner-bridge rehearsal.
It may compose the admitted sanitizer into the exact preset-mount catch and
prove the finite terminal contract without executing the native Harness.
