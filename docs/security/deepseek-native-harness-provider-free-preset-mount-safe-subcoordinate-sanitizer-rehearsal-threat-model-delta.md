# Threat-model delta: preset-mount safe-subcoordinate sanitizer

Date: 2026-08-22

Timestamp: 2026-08-22T04:50:32.7098461+10:00 (Australia/Brisbane)

Status: **frozen before implementation**

## Scope delta

The accepted source reconciliation leaves six internal mount candidates. This
tranche adds a pure in-memory reduction function and one synthetic local Node
fixture process. It does not start or modify the DeepSeek Harness.

## Controls

| Threat | Fail-closed control |
|---|---|
| Path-bearing exception text escapes | Output is an exact three-field object with null detail; fixture secrets and raw prefixes are forbidden from stdout/stderr/evidence. |
| A forged error selects a trusted coordinate | Source-specific mappings require exact constructor identity; unknown constructor or shape maps to `PRESET_MOUNT_UNCLASSIFIED`. |
| Prefix matching broadens silently | Bind every admitted prefix to exact pinned rc.7 source hashes and test near-miss/hostile variants. |
| Import/apply becomes a catch-all factual claim | The coordinate is admitted only for an exact `PresetMountError` after excluding owned stamp/post-await prefixes; it remains a safe reduction, not causal proof. |
| Pure rehearsal starts the Harness | Fixed Node command imports only the repository sanitizer and synthetic fixture; deny DSH imports, child processes, filesystem and network. |
| Sanitizer admission is treated as retry authority | Runner integration and any native attempt remain separately closed and false. |

## Residual risk

The sanitizer can only distinguish stable source-owned error shapes. A future
rc.7 drift or unexpected error maps to `PRESET_MOUNT_UNCLASSIFIED`; it must not
be repaired or retried from this tranche.

## Security acceptance

Accept only closed code/null-detail output, exact hostile fixtures, zero detail
leakage, one local non-Harness Node process and unchanged runtime/provider/
product boundaries.
