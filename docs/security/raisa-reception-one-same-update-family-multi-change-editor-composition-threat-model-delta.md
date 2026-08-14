# Threat-model delta — Reception One same-update-family multi-change editor composition

Date: 2026-08-15

Timestamp: 2026-08-15T01:55:57+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_implementation`

Task baseline: `e417eca0e1871a7ce5ed90c5e9223b8f86982b20`

## Security boundary

This tranche adds one local provisional draft across the already accepted
appointment update-family fields: practitioner, local start time and duration.
It adds no authority. The existing authenticated practice-scoped proposal and
confirm routes, signed freshness evidence, confirmer identity, idempotency,
audit and backend transaction remain the only mutation boundary.

The shared draft is not current truth, a reservation, a command, confirmation
evidence or a reusable delegated grant.

## Threats and required controls

| Threat | Fail-closed control |
|---|---|
| Three visible edits become three hidden writes | One bridge call invokes `handleMoveResize` once; source and route-count guards reject loops, sequential executors and more than one proposal/confirm. |
| A safe proposal is treated as permission to write | The combined bridge forces the existing confirmation dialog for every admissible proposal; the confirm route remains untouched until visible `Confirm & Save`. |
| Status leaks into an update-family payload | Status is absent from the shared draft and update bridge. Crossing to or from status discards the outgoing draft; no cross-family atomicity is claimed. |
| A concealed draft survives a semantic boundary | Collapse, status crossover, appointment reselection, root/fresh projection replacement, blur and visibility interruption clear the entire unsubmitted update draft. |
| Switching update fields silently loses compatible intent | Time, duration and practitioner buttons are views of one visibly summarized update-family draft; same-family switching preserves it without a route. |
| Requested values masquerade as current Diary truth | The current-truth summary remains source-derived; the draft summary is explicitly provisional and changed dimensions enter current truth only after fresh terminal reconciliation. |
| A combined time/duration produces an invalid end-of-day interval | The bridge validates the effective pair together before any proposal: 15-minute start, bounded 15-minute duration step and same-day end. |
| An invented, inactive or ambiguous practitioner is proposed | The target must match exactly one active practice-directory projection entry; the backend independently rechecks current practitioner authority at confirmation. |
| A stale or replaced appointment is changed | Existing signed freshness, confirm-time re-proposal, exact command match and fresh read remain mandatory; reselection and fresh replacement are locked/discarding boundaries. |
| Double-click or replay creates duplicate writes | UI busy locking prevents parallel submission; backend idempotency and the accepted M6 kernel proof remain authoritative. |
| Cancel, blocked or failed work promotes some draft fields | No optimistic mutation is permitted. All terminal paths use fresh existing read/reload behavior; requested values never patch the projection directly. |
| The appointment leaves the scoped projection and three success claims appear | One update-family terminal removal outcome replaces the editor; it does not claim three independent commits. |
| Keyboard or screen-reader users bypass confirmation | Native buttons, labelled controls, one live region and the existing focus-contained dialog preserve the same visible explicit confirmation path. |
| A model, email, SMS, voice or chatbot candidate acquires UI authority | No adapter or model reaches the DOM, bridge, proposal route or confirmer. External channel and revocable delegation runtime remain closed. |
| Route interception is overstated as live evidence | Every browser artifact is labelled `route_intercepted_browser` with authored-synthetic fixtures; no backend/database/provider or patient claim is made. |

## Preserved API/security properties

- GraphQL has no mutation role.
- One explicit REST/OpenAPI update proposal and one explicit confirm command own
  the mutation.
- Actor, practice, confirmer, freshness, signed evidence, idempotency and audit
  remain backend-owned facts.
- Events remain refresh hints only.
- No patient/product/clinical data, provider, credential, network, IAM,
  deployment or protected evidence is introduced.

## Residual risk and non-claims

Route-intercepted UI evidence cannot prove real-network retry timing,
production RLS, concurrent different-key serialization, performance,
representative staff usability or patient/delegated-assistant identity and
revocation. Those are not acceptance claims for this tranche.

## Stop conditions

Any need for a new route/request field, backend/API/database change, automatic
multi-command executor, cross-family rollback promise, model/provider runtime,
external channel authority, real data or deployment stops this tranche.
`docs/branding/` and every unrelated untracked file remain outside scope.
