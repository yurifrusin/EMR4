# Status-confirm HTTP route convergence

Date: 2026-08-13

Timestamp: 2026-08-13T13:09:24+10:00 (Australia/Brisbane)

## Lay summary

The final backend seam before visible Diary work is closed. When a staff member
confirms an appointment status, both the new canonical address and the old
compatibility address now enter the same protected command path. The server
checks that the proposal still belongs to the current database version,
rechecks the staff member's present authority and current appointment truth,
then records the status change, audit and replay receipt together. A lost
response can be retried without a second change and returns the same bytes.

A waiting-area-only instruction is deliberately refused here, so it cannot
slip back into the older local write mechanism. Twelve database-backed
scenarios, 112 hostile variations, 217 focused tests and the repository's 193
canonical checks all pass. No real patient or product data and no AI provider
were used.

We should not return to CF-D2 before visible UI work. The database command is
already fail-closed against current truth. Wiring the real Diary interaction
next will tell us exactly which quiet cues, refreshes and recovery signals a
future durability watcher needs, avoiding another abstract watcher programme
without a settled consumer boundary.

## Technical summary

- Source: `b414eb256853c301099d9cf7797a69cd3ec077c5`
- Result: `raisa_provider_free_status_confirm_http_route_convergence_pass`
- Canonical route: `POST /api/v1/appointments/proposals/status/confirm`
- Hidden alias: `POST /api/v1/appointments/proposals/status-confirm`
- Proposal carries a server-minted HMAC binding to
  `appointment_state_version`; the client cannot choose the generation.
- Authentication establishes transaction-local tenant context from the
  verified JWT before the RLS-protected user read, then verifies the loaded
  user's practice matches.
- The adapter receives a fresh command-session factory and owns ordered locks,
  current-authority checks, atomic status/audit/v1 receipt completion and exact
  stored-byte replay.
- Waiting-area union input returns `unsupported_status_confirm_variant`; no
  route-local fallback remains.
- Verification: 12/12 scenarios, 112/112 hostile mutations, 217/217 focused
  lineage tests, 193/193 canonical fast tests, Ruff, 209 maintained-source
  compilation, Diary JavaScript syntax, Git whitespace and exact cleanup.

Next: bounded visible native Diary status-confirm wiring and interaction proof.
CF-D2 remains an explicitly deferred observability-first durability extension,
not abandoned work and not a prerequisite for the UI tranche.
