# Ariadne Agent Error and Correction Register — Revision 185

## Scope

This revision records one orchestration defect found while verifying the
Context Fabric durability outbox-policy descendant rebind. It changes no
candidate contract or runtime behavior.

## Recorded incident

- `AER-0214` records a Windows verification command that supplied a wildcard
  pytest path literally and then allowed a later successful command to mask
  pytest's non-zero exit.
- The orchestrator detected the explicit file-not-found output, rejected the
  aggregate success, resolved the exact test paths with `rg --files`, and
  admitted pytest, Ruff and `git diff --check` independently.
- The defect resembles the earlier Windows preflight omission in `AER-0178`,
  while remaining a separate attempt rather than an attempt-peer link. The
  narrower prevention rule now forbids both unresolved pytest wildcards and
  chained-exit acceptance on Windows.

## Boundary

This revision records deterministic workflow evidence only. It authorises no
provider call, database write, migration application, product/runtime wiring,
deployment, Pages rebuild or protected-ref movement.
