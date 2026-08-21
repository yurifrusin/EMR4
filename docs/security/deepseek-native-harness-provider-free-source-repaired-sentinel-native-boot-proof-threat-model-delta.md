# Threat-model delta — source-repaired sentinel native-boot proof

Date: 2026-08-21
Timestamp: 2026-08-21T16:12:26.7707451+10:00 (Australia/Brisbane)
Status: `frozen`

## New executable surface

One fresh disposable local rc7 Node/native-Harness process loads only the source-repaired sentinel through the unchanged initial headless profile.

## Threats and controls

- Wrong or unrepaired sentinel: exact whole-controller and repair-evidence digests bind the raw-bytes literal, exact generated module and zero lexical violations.
- Changed runner/worker activation: `changed=False`, zero runner rows/files, no task, no broker and no worker/session are mandatory.
- Provider/network access: credential/proxy names are scrubbed and the accepted preload guard denies and records network primitives; any record fails closed.
- Reuse of a consumed attempt: the operation, attempt ID, evidence paths and disposable prefix are fresh; exclusive creation consumes before `Popen`.
- Hidden retry: the controller delegates to the already inspected single-`Popen` engine; source admission rejects retry loops and the terminal records zero retry.
- Raw-output leakage: launch contains no product data or prompt; only counts/digests survive after exact-root cleanup.
- False readiness: exact schema, monotonic sequence, closed event vocabulary and exact two-event terminal order are mandatory.
- Overclaim: a pass proves sentinel/HMR readiness only, not runner, worker, DeepSeek model/provider or development reliability.

## Residual risk

The proof exercises one Windows process and one prerelease Harness build. Later independent startup or worker defects can still exist and require separately frozen evidence.
