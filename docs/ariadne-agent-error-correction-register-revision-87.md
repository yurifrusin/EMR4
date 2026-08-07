# Ariadne agent-error register revision 87

Date: 2026-08-07

Status: disposable PostgreSQL plan accepted; implementation active

## AER-0093 is corrected

The first PostgreSQL plan reviewer pass remains rejected. Sol corrected the
cluster-role and psql input-mode defects, and a genuinely fresh Gemini 3.6
Flash/high exact-HEAD replacement veto at
`009395ac28eb7ac05017fe5fbd1ae1439ecf948d` reproduced the rollback-first,
cluster-wide role-absence and `--file=-` atomicity requirements, passed 9/9
focused checks and reported no P0-P3 finding.

## AER-0094 is corrected

The first replacement-review checkout used a descriptive Windows worktree path
and repeated the known path-length failure. It stopped before reviewer dispatch;
the failed destination is absent and unregistered, and no Docker/database call
occurred. The unchanged commit was checked out at the established short `r41`
path, passed exact-HEAD clean preflight and completed the fresh veto.

## Register posture

Revision 87 contains 94 bounded incidents: 75 agent-behavior observations,
six harness failures, five repository defects and eight transport timeouts. No
incident is open. The recurring Windows verifier-path signal now binds
AER-0063, AER-0078 and AER-0094; future Windows verifier worktrees use short
`rNN` destinations by default.

This register change supplies no PostgreSQL behavior, migration, operational
database/source, product/patient data, application/runtime, command, provider
product, deployment, production, release, Pages or protected-ref authority.
