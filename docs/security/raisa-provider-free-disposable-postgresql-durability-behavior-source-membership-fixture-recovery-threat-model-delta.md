# Threat-model delta: source-membership behavior-fixture recovery

Date: 2026-08-10

Status: candidate recovery control; runtime remains closed

## Changed surface

Only the authored-synthetic proofread-packet fixture and its deterministic
readback change. The accepted database body, inert SQL, RLS, roles, privileges,
failure registry and twenty-scenario population remain unchanged.

## Threats and controls

| Threat | Control |
|---|---|
| A packet proves only source-contract identity, not membership in the exact immutable source row | Canonically digest the ordered eleven-field same-locator outbox tuple with the accepted `source_membership_digest_v1` profile |
| The rehearsal invents a second digest implementation | Derive the expression from the exact accepted typed body node through the accepted renderer and require it to occur in the bound inert artifact |
| A database value chooses executable behavior | Use only a fixed scalar subquery over exact contract-owned synthetic locator fields; no result selects SQL, path, role, scenario or cleanup |
| Readback repeats the old false equality | Independently recompute the same full-row digest and compare it with the stored admission value |
| Recovery weakens the database mismatch guard | Preserve `CF201`, the body predicate, source lookup, principals and scenario expectations byte-identically |
| A contract edit hides scenario drift | Prove the twenty scenario objects and their order are byte-identical before and after the repair |
| A repaired candidate reaches runtime without complete review | Require the full deterministic packet and one fresh exact-HEAD independent veto before another disposable run |

## Residual boundary

This remains a serial, authored-synthetic, provider-free behavior rehearsal.
Concurrency, crash recovery, retention, key rotation, long-lived persistence,
operational feeds/watchers, product data and application wiring remain closed.
