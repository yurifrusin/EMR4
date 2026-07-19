# Bernie Stage 1 Tranche A readiness

**Decision:** `ready_for_bounded_run`

Tranche A completed as a read-only readiness and harness-proof tranche at source
`2d3fa717d612add9d1f871daf9e899751c5d210c`. It made no database mutation, no
appointment write, no product change, no provider or cloud call, and did not open
the browser. The fresh Ariadne receipt passed with all five mandatory rehydration
sources. `HEAD`, local and origin `master`, and local and origin
`handoff/current` were aligned at the expected handoff commit before named Stage 1
artifacts were created.

## Frozen bounded run

- Database: `gp_pms_stage1_2d3fa717_20260719` on loopback PostgreSQL
  `127.0.0.1:5434`. It did not exist during Tranche A. The maintenance connection
  and exact-database creation capability passed. Tranche B must create and seed it
  before any browser opens; `gp_pms_dev` and `gp_pms_test` remain forbidden.
- Reference date `D`: `2026-07-20`, the first future Monday with the frozen
  synthetic roster and availability.
- Product instruction: “Make an appointment for Margaret Thompson with Dr Shera
  today after 2 pm but before 3:45.” It is not rewritten or clock-patched.
- Synthetic fixture map: Stage 1 Synthetic Practice in Australia/Brisbane, Main
  Clinic, the configured allowlisted synthetic Receptionist, Dr Alex Shera
  (`MED0001234567`), Margaret Thompson, Standard 15-minute appointments, a
  Monday-Friday 09:00-17:00 schedule, and Room 1 rostered to Dr Shera on `D`.
- Provider boundary: `fake`, mocked/deterministic, with no live provider, external
  prompt, cloud operation, ADC, `gcloud`, ngrok, protected evidence, blocked
  corpus, historical diary, PII, RAG, memory, migration, or durable session use.

## Non-intercepted harness proof

The real static Diary selects `http://localhost:8001` when served on loopback port
3000, obtains pilot eligibility from the authenticated backend, and sends ordinary
HTTP requests through its existing `apiFetch` path. Live Diary loading is separate
from smoke mode. Tranche B will use a loopback same-origin authentication bootstrap
to log in the synthetic receptionist, retain the returned token without inspecting
or recording it, and navigate to the real Diary on `D` with
`bernie_open=true&bernie_review=live` and without `smoke=true`.

No browser request will be fulfilled, altered, or intercepted by the harness. The
evidence label for the happy path will therefore be
`live_local_backend_postgres`. Sanitized request evidence will contain methods,
paths, statuses, counts, and hashes only—not passwords, bearer tokens, raw headers,
or secret-bearing traces.

Before the browser opens, Tranche B must prove the exact database identity,
synthetic-only fixture inventory, authenticated pilot eligibility, roster and
availability, fake provider setting, outbound deny boundary, and zero appointment,
appointment-audit, and completed idempotency baselines. Any failed proof stops the
run before content or appointment mutation.

## Supporting checks

The focused interpretation readiness check passed 44 cases and 7 contracts while
preserving the blocked live-runtime/provider gate. The provider-boundary readiness
report passed with no provider call, route change, database access, memory/RAG, or
historical diary access.

The direct service-only fake-provider smoke parsed `D` and the 14:00-15:45 interval
correctly but returned `clarification_required` because that supporting script has
no database identity context. This is labelled `fake_provider`, not happy-path
evidence. The unchanged authenticated API route performs same-practice patient and
practitioner name resolution before recomputing the interpretation, so no Tranche C
defect is claimed or manufactured from that result.

The canonical machine-readable record is
`docs/bernie-stage1-tranche-a-readiness-report.json`.
