# Status-confirm route-mounting review — lay and technical closeout

Date: 2026-08-12

Result: **passed, with convergence blocked**

## Lay summary

The appointment-status confirmation doorway already exists in the application,
and the safer database mechanism behind it has now been proved separately. But
the doorway is still connected to the older internal path. So we should not
mistake “the endpoint is mounted” for “the endpoint is using the new safety
mechanism.”

The good news is that this is now a contained plumbing job, not another
four-hour durability mystery. The database work stays accepted. The next step
is to assemble and rehearse the connector off to the side: status-only input,
current staff/session authority, the proved transaction, and one exact response
mapping. Only after that passes would changing the live route be considered.

## Technical summary

- source: `fb3772dea0c27a7572df00e1b9d5153f9165ccf3`
- result: `raisa_provider_free_read_only_status_confirm_route_mounting_admission_review_pass`
- verdict: `mounted_legacy_route_not_admitted_for_physical_convergence`
- mounted path: `POST /api/v1/appointments/proposals/status-confirm`
- matrix: 2 satisfied, 1 partial, 7 blocking
- evidence: 10 exact hashes, 25 structural assertions, 45/45 hostile mutations
- verification: 11/11 focused review tests and 191/191 canonical tests pass
- separate hygiene item: one old Sprint-138 test still expects update/delete
  confirmations not to have the idempotency headers later work added; its
  bounded test-only correction is next and changes no product behavior

No live route, database or product behavior changed. No provider, patient data,
credentials, deployment, Pages or protected ref was touched.
