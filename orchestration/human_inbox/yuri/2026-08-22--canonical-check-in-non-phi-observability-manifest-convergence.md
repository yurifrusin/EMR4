# Canonical check-in non-PHI observability manifest convergence

Date: 2026-08-22

Timestamp: 2026-08-22T23:41:40.1369077+10:00 (Australia/Brisbane)

## Lay summary

The second small check-in control artifact is complete. EMR4 now has one exact
default-off list of the five measurements and six critical alerts that a later
check-in monitor may use. The list contains no patient, appointment, practice,
staff or request/response identifiers, and none of its alerts can operate a
control automatically.

Nothing is monitoring or sending alerts yet. Ordinary practices remain denied,
the product and clients are unchanged, and no live data, provider or database
was used.

This was a clean forward step rather than another Harness recovery loop: one
missing artifact was added and mechanically proved. The only correction was a
test phrase that crossed a line break; the actual manifest passed unchanged.

## Technical summary

- reviewed source: `7acd4e9c39ce534042178f9b8b7e049161ce8b03`;
- canonical path:
  `docs/api-spine/manifests/canonical-check-in-non-phi-observability.json`;
- exact size: 6,291 bytes;
- SHA-256:
  `79d6191e1a499e85bb12be38fd15980c7f1bf7dc54eb15132c607b0c43341d8c`;
- exact contents: five low-cardinality metric families, fifteen forbidden
  value classes and six non-identifying/non-actuating critical alerts;
- evidence: 5 focused and 98 integrated checks pass, plus Ruff, compilation
  and whitespace checks;
- execution cost: zero workers, providers, databases, Docker or product
  runtime changes; and
- protected refs and `docs/branding/` remain untouched.

The next narrow tranche will add an unmounted, globally disabled typed adapter
between the accepted admission kernel and this vocabulary. It is executable
development work, but it will still have no transport, exporter, automatic
action, application mounting, practice enablement or product data.
