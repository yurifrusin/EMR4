# Canonical check-in post-proposal revalidation rehearsal report

Date: 2026-08-24

Timestamp: 2026-08-24T18:00:02.9645865+10:00 (Australia/Brisbane)

Status: `frozen_evidence`

Result: `raisa_provider_free_database_backed_check_in_post_proposal_revalidation_pass`

## Outcome

Both missing temporal witnesses pass through the existing default-off local
HTTP/PostgreSQL test boundary without a product change. A proposal does not
preserve Receptionist authority after the role is revoked, and it does not
preserve a selected waiting area after that area is deactivated.

The authority-revocation confirmation is rejected with HTTP 403 before command
execution. The waiting-area confirmation returns the existing typed
`waiting_area_not_active` block after signed-evidence verification. Each leaves
the appointment `Booked` and persists zero audit, committed-event or completed
idempotency row.

## Verification

The two exact witnesses pass after rehydration. The committed candidate passes
the exact seven-file serial profile with 207 collected tests. Ruff, compileall,
diff hygiene and the empty product/API Spine diff check pass. Route, adapter and
configuration blobs are unchanged.

## Claim and boundary

This is authored-synthetic product assurance for two post-proposal transitions.
It does not use the historical diary trove, reopen ordinary-practice admission,
change the feature default or allowlist, change a public contract, or open a
provider, live practice, product data, production, deployment, release, Pages
or protected-ref surface.

The targeted canonical check-in temporal-evidence gap is closed. The next
substantive Rayleen command-family question is the still-separate waiting-area
movement path, beginning with a provider-free read-only readiness review.
