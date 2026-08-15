# Threat-model delta: provider-free unmounted delete-confirm conditional-command kernel

Date: 2026-08-15

Timestamp: 2026-08-15T11:50:49+10:00 (Australia/Brisbane)

Status: `frozen_unmounted_delta`

Parent: `docs/security/raisa-reception-one-cancellation-command-path-readiness-review-threat-model-delta.md`

| Threat | Fail-closed control |
|---|---|
| Pre-route authentication is mistaken for final cancellation authority | Recheck actor activity, exact practice, current role and cancellation capability after target lock and again while all locks are held. |
| Revoked actor learns a stored receipt or target existence | Authority and practice-scoped target checks precede idempotency classification and receipt disclosure. |
| Authority changes between recheck and commit | The abstract practice authority fence is held across the write set; physical mapping remains a later proof obligation. |
| Two different keys cancel the same stale appointment | Both serialize on the exact appointment; the waiter rechecks the state version and loses stale without effect. |
| Lost response causes a second destructive effect | Appointment, audit and completed receipt commit atomically; same-key/same-digest retry returns the original receipt. |
| Failure leaves a cancelled appointment without audit/receipt, or a receipt without cancellation | Every pre-commit failure discards the in-progress claim and all staged appointment, audit and receipt state. |
| Signed evidence is valid for a different person, practice, session, appointment, state or reason | Signature admission binds all server identity, operation, target, pre-state, waiting-area, reason, warning, freshness and digest fields exactly. |
| Cancellation reason is dropped or changed | Required structured reason and optional bounded free text are digest-bound and equal across appointment, audit and receipt. |
| Waiting-area side effect is hidden | Signed pre-state binds waiting-area identity and the command binds clearing; success always records and clears it atomically. |
| Raw delete or status fallback weakens the dedicated command | Both are rejected labelled ingress families and receive no kernel authority. |
| Model, event or channel assertion self-confirms | Only a distinct human `confirmed=true` plus backend-signed evidence and current backend authority can admit a first effect. |
| Fresh UI read is mistaken for transactional correctness | The minimized receipt proves command completion; separately authorised readback is reconciliation only. |
| Synthetic locks are mistaken for PostgreSQL proof | The evidence label is unmounted/authored-synthetic and the closeout must retain physical representability and runtime convergence as closed gates. |
| Scope broadens through imports or I/O | Tests reject application, database, network, provider and process imports; every effect-boundary flag remains false. |
| User-owned files enter the tranche | Explicit-path staging excludes `docs/branding/` and every unrelated untracked file. |

The packet contains only `syn-` identifiers, fixed non-secret digests, reason
codes, bounded fictional text and symbolic trace steps. It contains no person,
patient, clinical, product-derived, provider or protected evidence.
