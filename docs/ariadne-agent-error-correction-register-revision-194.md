# Ariadne Agent Error and Correction Register — Revision 194

Date: 2026-08-08

Revision 194 appends `AER-0225` through `AER-0227` without rewriting earlier
incidents.

- `AER-0225` records the rejected PowerShell backup command which used an
  unsupported `New-Item -LiteralPath` parameter. Nothing was copied or run; a
  fresh stop-on-error command used a validated unique temporary path and proved
  byte-identical backup before attempt 043.
- `AER-0226` records immutable attempt 043. The behavior plan expected
  `F_ADMISSION_SOURCE` / `CF201` for a missing outbox row, while the accepted
  exact-row body correctly and deterministically raises `F_CARDINALITY` /
  `CF004`. The correction changes only that behavior expectation and adds
  bounded expected-versus-observed SQLSTATE telemetry.
- `AER-0227` records the first diagnosis generator's formatting-sensitive
  missing end delimiter. The fresh corrected generator uses the exact next
  named function declaration and emits deterministic evidence.

The database body, inert SQL and parse/catalogue evidence remain byte-identical.
No additional container or provider call was used for diagnosis.
