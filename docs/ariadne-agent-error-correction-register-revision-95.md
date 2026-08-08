# Ariadne agent error and correction register revision 95

Date: 2026-08-08

Status: accepted register correction

Revision 95 adds AER-0115 and brings the register to 115 bounded incidents.

## AER-0115 — descendant reused the parent's database sentinel

The first admitted disposable PostgreSQL behavior run failed closed after
artifact admission and before any of the 20 behavior scenarios. Its structured
evidence recorded `catalogue/server_or_database`, zero scenarios, no database
stderr and verified exact container cleanup.

The behavior descendant had correctly created and connected to its fixed
`emr4_synthetic_behavior` database, but directly reused the accepted parent
catalogue assertion. That parent assertion deliberately binds its own
`emr4_synthetic_success` database name. The structural reuse was therefore
valid while the environment-specific sentinel was not.

The failed evidence remains immutable. The repair adds a bounded adapter that:

- independently proves the exact descendant database identity and PostgreSQL
  16 major version;
- deep-copies the catalogue facts without changing the observed evidence;
- substitutes only the parent's private database sentinel in that copy; and
- invokes the unchanged accepted parent assertion for every remaining
  structural, role, schema, function, trigger, privilege and RLS check.

A unit test proves the descendant binding, the non-mutation property and the
private-copy normalization. The corrected candidate remains runtime-closed
until deterministic checks, a new commit and a fresh exact-HEAD independent
veto pass.
