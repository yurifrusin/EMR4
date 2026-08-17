# Threat-model delta — Provider-free read-only post-cancellation programme orientation

Date: 2026-08-18

Timestamp: 2026-08-18T03:07:24.5811715+10:00 (Australia/Brisbane)

Status: `frozen_for_read_only_execution`

Task baseline: `5981b6cacdd3d488462803748c0d86f1e9bc2457`

## Assets protected

- one authoritative meaning for appointment arrival, status and waiting-area
  changes;
- the distinction between a default-off authored-synthetic route and a
  generally admitted product command;
- explicit staff confirmation, current-authority/source recheck, idempotency,
  audit, receipts and fresh readback;
- the no-raw-fallback and no-optimistic-truth invariants; and
- sealed evidence, protected refs and all unrelated untracked files.

## Threats in this tranche

| Threat | Fail-closed control |
|---|---|
| Treating route existence as product admission | Matrix records route gate, allowlist and current consumer separately. |
| Treating generic `Arrived` status as automatically identical to dedicated check-in | Compare command payload, confirmation evidence, waiting-area effect, event, audit and receipt semantics before selection. |
| Correcting stale static metadata before choosing canonical meaning | Static grammar and route-contract files remain read-only evidence. |
| Adding a Reception One control by analogy | Successor is read-only readiness/convergence review before any product composition. |
| Letting an event establish current truth | Events remain acceleration hints; fresh authorised source read remains mandatory. |
| Widening A5.1 authored-synthetic authority | Feature flag, practice allowlist and default-off posture remain unchanged. |
| Drifting into patient identity or external adapter work | Patient linking and external channels remain distinct future gates. |
| Hiding untracked user files during closeout | Explicit-path staging only; `docs/branding/` and unrelated untracked files are preserved. |

## Trust-boundary finding to test

Three repository layers may currently disagree about arrival intent:

1. first-party clients can request `Arrived` through the general status family;
2. a dedicated A5.1 check-in proposal/confirm route exists behind a default-off
   authored-synthetic gate and can atomically include waiting-area assignment;
3. the static action grammar and route contract still classify check-in as
   planned-not-implemented with no signed confirm action.

The orientation may describe this as a convergence question. It must not call
any layer authoritative beyond its accepted scope or silently choose a product
route.

## Residual risk and claim boundary

Repository-static consistency does not prove a live route outcome, database
transaction, production usability or safe general admission of A5.1. Passing
this tranche proves only that the current layers were compared and one narrow
read-only successor was selected. All provider, product-data, runtime,
deployment, release and protected-ref surfaces remain closed.
