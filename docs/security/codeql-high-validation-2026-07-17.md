# CodeQL High-Candidate Validation — 2026-07-17

Target: `ea0e6537c38fb73b572de2c032aba997ed168cd9`

## Outcome

All ten open CodeQL candidates classified high were closed by validation as
`suppressed` or `not_applicable`; none survives as a reportable high security
finding. This conclusion is narrower than “the Diary is secure.” The URL-driven
smoke/dev controls and fallback identifier generation remain worthwhile
defence-in-depth cleanup because they increase safety ambiguity and scanner
noise, but the traced backend boundaries prevent the claimed authorization or
confidentiality impact.

No GitHub alert was dismissed and no product code or GitHub security setting
was changed during validation.

## Validation rubric

Each candidate was required to satisfy all five criteria before it could be
reportable:

- [x] Identify the exact attacker-controlled or sensitive source.
- [x] Identify the closest security control or claimed missing control.
- [x] Trace a reachable path to a security-relevant sink and product boundary.
- [x] Exercise the realistic backend/CLI interface or use the strongest
  proportionate negative control.
- [x] Record counterevidence, preconditions, remaining proof gaps, and an
  instance-preserving disposition.

## Closure table

| Row | Instance | Root control / affected location | Source | Sink or claimed control | Disposition | Counterevidence or proof gap | Survives |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QH-001 | CodeQL 295, `js/user-controlled-bypass` | `docs/diary/diary.js:5752`, affected `:5790` | URL smoke/dev/review flags | Confirmation POST branch | suppressed | Fixed backend origin; unauthenticated calls fail; write route requires staff role, explicit confirmation, signed/current evidence, owner binding, and idempotency | no |
| QH-002 | CodeQL 232, `js/user-controlled-bypass` | `docs/diary/diary.js:4392`, affected `:4396` | `smoke=true` | Client token check | suppressed | Smoke branch uses authored mock template/appointments/types and avoids protected appointment reads; backend remains independently authenticated | no |
| QH-003 | CodeQL 233, `js/user-controlled-bypass` | `docs/diary/diary.js:7289`, affected `:7314` | live dev-review URL flags | Initial load gate | suppressed | Non-smoke `loadDiary()` repeats the token guard; API calls without a token receive 401 | no |
| QH-004 | CodeQL 234, `js/user-controlled-bypass` | `docs/diary/diary.js:7289`, affected `:7314` | dev-fixture URL flags | Initial load/review gate | suppressed | Fixture endpoint requires authentication and returns 404 outside development; verified by focused tests | no |
| QH-005 | CodeQL 197, `js/insecure-randomness` | `docs/diary/diary.js:186`, affected `:172` | `Math.random` fallback | Initial client session correlation ID | not_applicable | ID is not a credential or authorization token; HTTPS/localhost uses `crypto.randomUUID`; server authority is separately bound | no |
| QH-006 | CodeQL 198, `js/insecure-randomness` | `docs/diary/diary.js:186`, affected `:400` | `Math.random` fallback | New client session correlation ID | not_applicable | Same correlation-only boundary as QH-005; predictability grants no backend capability | no |
| QH-007 | CodeQL 201, `js/insecure-randomness` | `docs/diary/diary.js:193`, affected `:606` | `Math.random` fallback | Server-route idempotency key | suppressed | Keys are caller-supplied replay controls, HMAC-hashed and scoped by practice, actor, and operation; confirmation authorization is independent | no |
| QH-008 | CodeQL 196, `js/incomplete-sanitization` | `docs/diary/diary.js:6293`, affected `:6295` | Selected appointment ID | CSS attribute selector | suppressed | Production appointment IDs are typed UUIDs; mock IDs are fixed safe strings; manual context never populates `sourceAppointmentId`; sink only reselects a UI element | no |
| QH-009 | CodeQL 272, `py/clear-text-logging-sensitive-data` | `scripts/bernie_ui_dag_d5_response_shape_report.py:77`, affected `:138` | Committed D5 review | CLI JSON output | not_applicable | Output is an exact snapshot-bound aggregate; safety assertion rejects patient/practitioner/appointment/API/raw-diary fields; dynamic output contained only aggregate metadata | no |
| QH-010 | CodeQL 268, `py/clear-text-logging-sensitive-data` | `scripts/appointment_route_inventory_preflight.py:114`, affected `:300` | Mounted route metadata | CLI JSON output | not_applicable | Output contains counts, fixed categories, and boolean boundaries; assertions prove no HTTP, DB, provider, historical-data, GraphQL, or write execution | no |

## Evidence and tests

Static tracing established:

- `apiFetch()` fixes the destination to the configured EMR4 backend and attaches
  a bearer token only when one exists (`docs/diary/diary.js:2615`).
- smoke-mode diary loading selects only mock data at
  `docs/diary/diary.js:4439`; normal loading uses authenticated API calls.
- the dev fixture route has explicit authentication and non-development 404
  gates, demonstrated in `tests/test_bernie_dev_fixtures.py`.
- Bernie confirmation requires a mutating staff role at
  `app/routers/appointments.py:7220` and revalidates explicit confirmation,
  evidence, current state, practice/user ownership, and collision state.
- idempotency records are unique per practice, actor, operation, and HMAC of
  the caller key (`app/services/appointment_idempotency.py` and
  `app/models/appointments.py:160`).
- appointment response identifiers are UUID typed at
  `app/schemas/appointments.py:220`; the incomplete selector fallback does not
  receive manual query text.

The focused serial backend boundary gate passed 7/7:

- unauthenticated and production-blocked dev fixture cases;
- unauthenticated Bernie confirmation;
- `confirmed=false` and mismatched selection/create evidence with zero writes;
- unauthenticated create proposal; and
- tampered confirmation evidence with zero writes.

Both flagged CLI reporters executed successfully. Their captured output is
aggregate-only and matches their safety assertions.

Validation artifacts:
`%TEMP%/codex-security-scans/emr4/ea0e6537_20260717T004200Z/artifacts/05_findings/`.

## Residual hardening opportunities

Although the high claims do not survive, a bounded Diary hardening sprint
would reduce recurrence and safety ambiguity by moving smoke/dev enablement to
a localhost or build-time capability, allowlisting confirmation endpoint
paths, replacing every `Math.random` fallback with `crypto.getRandomValues` or
fail-closed generation, and avoiding selector-string construction entirely.
That is product/client remediation, not a prerequisite for suppressing these
specific high findings.

The separate delivery-control recommendation remains unchanged: validate
signals before enforcement, then decide whether to protect `master`, enable
secret push protection, require stable checks, and adopt response SLAs.
