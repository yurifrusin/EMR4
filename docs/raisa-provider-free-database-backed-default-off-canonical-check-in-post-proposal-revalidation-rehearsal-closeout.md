# Canonical check-in post-proposal revalidation rehearsal — closeout

Date: 2026-08-24

Timestamp: 2026-08-24T18:00:02.9645865+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

Exact reviewed candidate: `c6365f53b7edd902d31b370a321ebc8bf9427185`

## Lay outcome

The existing check-in machinery already does the right thing when reality
changes between proposal and confirmation. A receptionist's earlier proposal
does not let them confirm after losing the Receptionist role. A waiting area
selected earlier is rejected if it closes before confirmation. Neither denial
leaves a partial arrival, waiting-area assignment or command record.

This closes the two useful temporal check-in gaps identified by the preceding
synthetic review. No product repair was needed.

## Technical outcome

- exactly two authored-synthetic HTTP/PostgreSQL witnesses were added;
- current-role revocation returns the existing HTTP 403 authorization denial;
- current-area deactivation returns the existing typed
  `waiting_area_not_active` block after signed-evidence verification;
- both appointments remain `Booked`, with zero audit, committed-event and
  completed-idempotency rows;
- the committed seven-file serial assurance profile passes all 207 tests;
- route, adapter, config, API Spine, feature default and allowlist bytes remain
  unchanged; and
- Ruff, compileall and diff hygiene pass.

The REST command remains explicit, confirmed, practice-scoped, idempotent and
audited. Current authorization and waiting-area truth remain backend-owned;
GraphQL remains read-only and events remain non-actuating.

## Workflow reading

One bounded manifest/projection-shape incident contains two startup-only test
path misses and two post-validation diagnostic-display key assumptions. None
changed runtime or product state. The exact seven-file passing manifest and
typed transaction projection are now evidence-bound; AER-1162 records the
incident.

## Continuing boundary

The targeted temporal check-in gap is closed. The next substantive Rayleen
command-family work is a read-only readiness review for explicit waiting-area
movement, which remains distinct from check-in and general status.

No ordinary activation, feature-default or allowlist change, generic-status
`Arrived` change, client/action grammar, provider, historical data, product
data, production, deployment, release, Pages or protected ref is opened.

Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.
