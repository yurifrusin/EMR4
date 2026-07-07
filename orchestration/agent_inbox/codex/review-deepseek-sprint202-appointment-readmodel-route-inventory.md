# DeepSeek Review - Sprint 202 Appointment Read-Model Route Inventory

DeepSeek completed a read-only Sprint 202 review after Sprint 201's audit
correlation continuity index.

Recommendation:

- Add `docs/api-spine/appointment-read-model-route-inventory.md` as a static
  map from GraphQL appointment/diary/audit/Bernie read roots to current
  appointment-router GET/read routes.
- Add `tests/test_api_spine_appointment_read_model_route_inventory.py` as a
  deterministic static test over the GraphQL SDL, appointment router source,
  markdown inventory, and existing OpenAPI drift guard route inventory.
- Mark `diary`, appointment audit, availability, and Bernie session mappings as
  partial where the current GET route is narrower than the GraphQL read root.
- Keep viewer/practice/patient/directory roots as external to this
  appointment-router slice.
- List legacy compatibility writes explicitly outside the read graph.

Risks called out:

- The GraphQL `DiaryDay` and `AuditFilter` surfaces are richer than the current
  appointment GET routes, so `partial` coverage must not be overclaimed as full
  resolver readiness.
- Command-style POST reads, proposal commands, confirm commands, and Bernie
  session POST commands must remain outside the read-model route bridge.
- The inventory must preserve the same closed gates as the Sprint 200 and
  Sprint 201 continuity indexes.

No DeepSeek implementation changes were integrated directly.
