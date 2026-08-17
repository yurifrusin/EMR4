# Reception One selected-appointment cancellation composition threat-model delta

Date: 2026-08-17

Timestamp: 2026-08-17T13:49:00.3722917+10:00 (Australia/Brisbane)

Status: `frozen`

Baseline: `36edc1e5b36b83a54f6af28c9519853290e4189b`

## Security objective

Expose the already accepted delete-confirm command through Reception One
without letting presentation state become authority, creating a second
cancellation path, widening the public receipt, or presenting an uncertain
effect as current truth.

## Trust boundaries

1. **Projection to first-party rendering:** the current scoped appointment is
   display evidence, not a write grant.
2. **Staff draft to proposal:** selected reason/note are untrusted provisional
   input until the backend proposal admits them.
3. **Proposal to explicit confirmation:** the client may render warnings and
   blocks but cannot manufacture or skip server confirmation evidence.
4. **Confirm response to public receipt:** only the recursively closed minimal
   public envelope may cross into client outcome state; private receipt bytes
   and appointment read models remain server-side.
5. **Command outcome to displayed truth:** any terminal or uncertain outcome
   requires a fresh authorised scoped read before further action.
6. **Raisa semantics to adapter UX:** adapters may choose presentation, but
   cannot redefine facts, status, consequences, warnings, confirmation or
   receipt meaning.

## Threats and controls

| Threat | Required control |
|---|---|
| Palette activation accidentally mutates | Open, close, switch and draft issue zero routes. |
| Cancellation is silently downgraded to a status update | Dedicated proposal and canonical confirm endpoints are exact; no status fallback under any error. |
| Raw compatibility DELETE bypasses proposal/confirm | The Reception One bridge contains no `DELETE` and never calls the ordinary modal delete function. |
| Stale client selection cancels another/currently changed record | The bridge binds exact selected ID; backend confirmation rechecks current source version and authority; client refreshes after terminal outcome. |
| Staff confirmation is skipped for an apparently safe proposal | Every admissible delete proposal opens the contained explicit confirmation dialog. |
| A blocked proposal is still confirmable | Typed blocks render a close-only dialog and no confirm request. |
| Adapter or model invents an action | Only allowlisted action/reason/endpoint enums enter the deterministic bridge. Free text is capped and never authority. |
| Malicious/widened response leaks patient or private receipt data | Exact recursive key, enum, identity, reason, warning and audit validation rejects unknown fields and any `appointment` read model. |
| Success/replay body mismatch is obscured | Both must conform to the same strict public schema and produce the same receipt-based visible outcome; replay never implies a second effect. |
| Network/malformed-response ambiguity is displayed as failure or success | Client performs fresh reconciliation; if that fails, it enters `reconciliation_required` and makes no effect claim. |
| Proposed reason/note is shown as current truth | Draft and dialog are labelled provisional; only fresh projection data is current truth. |
| Re-selection or action switching races an in-flight cancellation | Existing global selected-action busy, dialog, interruption and reconciliation locks include cancellation. |
| Focus loss permits duplicate confirmation | One busy latch, contained dialog/Escape ownership and disabled palette/submit controls. |
| Creative renderer omits warnings or changes consequence | Typed semantic envelope fixes mandatory facts, action identity, warnings, confirmation and outcome; only layout/modality/copy within that meaning may vary. |
| External adapter receives raw database rows | Raisa exposes only purpose-limited typed projection/action envelopes. |
| Untracked user material is captured in evidence or commit | Exact owned paths, sanitized authored-synthetic fixtures and explicit-path staging; `docs/branding/` excluded. |

## Fail-closed response admission

A successful result requires exact top-level keys and values for
`raisa.delete_confirm_public_envelope.v1`, exact issue objects, exact sorted
audit labels, no blocks, and one exact
`appointment.delete_confirmation_receipt.v1`. The receipt appointment ID and
reason must match the confirmed request; status is `Cancelled`; waiting area is
null; warning codes are empty or exactly `waiting_area_cleared`. Any mismatch
is an uncertain outcome and triggers fresh reconciliation without rendering the
untrusted body.

## Evidence and data handling

Only fixed authored-synthetic fixtures, route counts, endpoint names,
sanitized lifecycle phases, schema decisions, viewport measurements and source
guards may be retained. Do not retain bearer tokens, headers, signatures,
prepared confirmation evidence, request/response bodies, private receipt
bytes, patient/product data or unrestricted console traces.

## Residual risk and closed surfaces

Route interception cannot prove live backend/PostgreSQL behavior or external
adapter compliance. The accepted HTTP/PostgreSQL tranche supplies separate
authored-synthetic command evidence; this tranche proves only the visible
consumer composition. Ordinary booking-modal raw/fallback compatibility,
real users/data, external channels, provider calls, database execution,
deployment, production and release remain closed.
