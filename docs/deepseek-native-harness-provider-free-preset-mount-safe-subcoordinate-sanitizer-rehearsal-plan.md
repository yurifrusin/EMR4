# DeepSeek native Harness preset-mount safe-subcoordinate sanitizer rehearsal plan

Date: 2026-08-22

Timestamp: 2026-08-22T04:50:32.7098461+10:00 (Australia/Brisbane)

Status: **frozen before implementation**

Reasoning level: **Extra High** for a new typed error-reduction boundary that
must never serialize the underlying path-bearing exception.

## Objective

Implement and execute a pure provider-free JavaScript sanitizer that accepts an
in-memory rc.7 preset-mount exception plus the exact `PresetMountError`
constructor and returns only one schema-closed safe subcoordinate with null
detail. Exercise it with synthetic exceptions in a local Node process, without
starting the DeepSeek Harness.

## Closed output vocabulary

- `PRESET_MOUNT_AGENT_SCOPE_ABSENT`
- `PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE`
- `PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED`
- `PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT`
- `PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT`
- `PRESET_MOUNT_ROOT_SERVICE_LEAK`
- `PRESET_MOUNT_UNCLASSIFIED`

Every result is exactly:

```json
{"stage":"preset_mount","code":"<closed value>","detail":null}
```

No message, reason, stack, cause, path, row id, package name, prompt, response,
session value, credential or arbitrary input field may be returned, logged or
persisted.

## Required source binding and classification

The implementation must bind the exact accepted rc.7 `PresetMountError`
constructor and six source coordinates. It may inspect only in memory:

- the exact unscoped-context prefix;
- `PresetMountError.reason` prefixes owned by the exact pinned source; and
- constructor identity.

Unknown constructors, shapes, reasons or prefixes map to
`PRESET_MOUNT_UNCLASSIFIED`. A valid `PresetMountError` not matching the four
post-await/stamp prefixes maps to the source-owned import/apply coordinate. The
sanitizer is pure, import-free, filesystem-free and network-free.

## Execution envelope

One local Node process may run a fixed authored-synthetic fixture matrix. It
must not import or start `@deepseek-ai/dsh`, read the environment, open files,
spawn children or make network requests. Python admission verifies exact
stdout JSON and zero stderr; no fixture contains product, patient or clinical
data. No native Harness process is authorised.

## Parallelism assessment

- DeepSeek lane: **declined**. The sanitizer will govern later DeepSeek Harness
  failures; using the governed worker before admission is circular.
- Gemini lane: **declined**. The exact prefix-to-enum function and hostile
  synthetic matrix are deterministic; reassess only if a semantic ambiguity
  remains after tests.
- Native-subagent lane: **declined**. Developer policy prohibits delegation and
  the pure source/fixture transaction is serial.
- GPT Sol owns implementation, local Node execution, readback and closeout.

## Acceptance and stop rule

Accept only exact mapping for every source coordinate, fail-closed
`UNCLASSIFIED` behavior for hostile/unknown values, byte-for-byte absence of
input details from output, one local Node fixture process and zero native
Harness/provider/product activity. This tranche does not connect the sanitizer
to a runner and authorises no native attempt. If constructor identity or source
prefixes cannot be bound without broad string interpretation, stop without a
runtime bridge.

## Explicit exclusions

No native Harness process, runner integration, retry, worker turn, model/
provider request, raw-error persistence, target edit, product/configuration/
API/database/route/adapter/flag/allowlist/grammar/client/waiting-area change,
ordinary-practice enablement, generic-status `Arrived` change, patient/product/
clinical/historical/protected data, production runtime, deployment, release,
Pages, protected evidence or protected-ref movement is authorised.
