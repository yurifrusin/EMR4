# Ariadne Agent Error and Correction Register — Revision 186

Date: 2026-08-08

Revision 186 appends `AER-0215` and does not rewrite any earlier incident.

`AER-0215` records that behavior attempt 039's seven-item semantic probe
failed closed after exact transition-result and relation-delta admission, but
its evidence released only the digest of `BTR-E04`. The exact failed predicate
could not be distinguished after the owned container had correctly been
removed.

The correction keeps raw PostgreSQL values closed while admitting unique
one-based failed probe indexes bounded to integers 1–16. Exact boolean-array
shape and hostile missing, malformed, non-boolean, duplicate, overlong and
out-of-range cases are tested before another disposable characterization.

The database artifact, behavior contract, scenario population, relation
change allowlist, provider boundary, product boundary and protected refs are
unchanged.
