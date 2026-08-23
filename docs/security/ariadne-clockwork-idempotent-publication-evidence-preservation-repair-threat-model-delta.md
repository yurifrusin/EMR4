# Governance clockwork idempotent publication evidence preservation repair — threat-model delta

Date: 2026-08-23

Timestamp: 2026-08-23T18:58:39.0105413+10:00 (Australia/Brisbane)

Status: `frozen`

## Scope

This delta covers one provider-free repair to the existing CLI's exact
already-published branch. It adds one generated machine readback JSON and no
operator document, canonical surface, provider, product, database, credential,
network, runtime, deployment, Pages or protected-ref authority.

## Threats and controls

| Threat | Control |
|---|---|
| Idempotent readback erases publication command digests again | Never call the publication-pair writer from the already-published branch; snapshot and assert both publication files byte-exact in tests and occupied evidence. |
| A readback is recorded against the wrong publication | Require matching operation, source, generation, passing status and `publication_committed` facts in JSON, plus matching bindings in the report. |
| Corrupt or absent historical evidence is silently treated as valid | Reject before readback creation when either publication file is absent, unreadable or mismatched; do not attempt reconstruction. |
| A second report becomes another operator form | Add only one generated JSON with no caller fields and no human-authored companion report. |
| Readback writing partially corrupts its own record | Write the generated JSON through a same-directory temporary file and atomic replace; publication files are never write targets. |
| The repair reexecutes costly verification | Preserve the exact-published check before verification and assert zero executed commands in the readback. |
| The repair mutates canonical clock state | Validate generation, transaction, pointer, latch, lease and drift before/after the occupied proof. |
| Prefix selection becomes free form | Derive only the existing ordinary and checkpoint prefixes from the closed intent schema. |
| A historical overwritten pair is fabricated | Reject non-publication evidence and explicitly leave AER-1130's lost digests unreconstructed. |

## Claim boundary

The repair can preserve future valid publication pairs and record one current
idempotent reading. It cannot restore already-lost digests, reduce governance
test cadence, qualify worker harnesses or open product, provider, data,
production, deployment, Pages, protected evidence or protected refs.
