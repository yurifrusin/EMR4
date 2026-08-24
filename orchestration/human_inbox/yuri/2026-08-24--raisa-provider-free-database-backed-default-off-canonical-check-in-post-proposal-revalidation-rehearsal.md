# Yuri closeout — check-in post-proposal revalidation

Date: 2026-08-24

Timestamp: 2026-08-24T18:00:02.9645865+10:00 (Australia/Brisbane)

Attention required: `no`

## Lay summary

The existing check-in path safely handles both of the remaining timing changes:
a receptionist cannot confirm an old proposal after losing that role, and a
waiting area cannot be used after it closes. Both requests fail without leaving
a partial arrival or command record. No product repair was necessary.

The historical diary trove was not read or used in this tranche. Its earlier
sanitised timing/provenance seed has produced no new product branch.

## Technical summary

- candidate `c6365f53b7edd902d31b370a321ebc8bf9427185` adds two test witnesses only;
- the existing 403 current-role denial and typed
  `waiting_area_not_active` response are preserved;
- both database readbacks show `Booked` and zero audit/event/completion rows;
- all 207 tests in the committed serial profile pass;
- route, adapter, config and API Spine bytes are unchanged; and
- one bounded manifest/projection-shape incident covers two pre-collection
  filename misses and two harmless post-validation display assumptions; it is
  contained in AER-1162.

## Deliberately closed

Ordinary check-in stays default-off with an empty default allowlist. Generic
status, waiting-area movement, clients, action grammar, provider/model access,
historical or product data, production, deployment, release, Pages and
protected refs remain unchanged and closed.

## Place in Raisa and next tranche

The canonical check-in temporal assurance gap is now closed. The engine will
continue with a provider-free read-only readiness review of the still-separate
waiting-area movement command family, so the next work advances Rayleen's
missing command architecture rather than adding another check-in rehearsal.
