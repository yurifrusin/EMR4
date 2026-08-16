# Ariadne agent error and correction register — revision 325

Date: 2026-08-17

Timestamp: 2026-08-17T08:40:48.9037025+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 325 records 374 bounded known incidents. No incident is open.

- AER-0374 preserves the first occupied delete-confirm HTTP/PostgreSQL harness
  stop. The rehearsal opened only its owned PostgreSQL resources, then failed
  before scenario execution because its independently declared Docker profile
  omitted the inherited helper's mandatory `context` key.
- The released failure evidence remained sanitized and schema-valid. Both the
  first lifecycle and one bounded traced diagnostic lifecycle verified exact
  container/network cleanup; independent label-filtered postflight found zero
  surviving owned resources.
- The repair adds only fixed `context=default` to the rehearsal contract and
  closed schema, raises the hostile population to 135, validates the field and
  directly asserts the inherited `docker --context default exec` argv shape.

## Boundary

No product source, API, schema, command meaning, database authority, provider,
deployment state or protected ref changes. `docs/branding/` and every unrelated
untracked file remain preserved.
