# Ariadne agent error and correction register revision 143

Date: 2026-08-09

Status: corrected; deterministic rerun pending

Revision 143 adds AER-0168 and brings the register to 168 bounded incidents
with zero open incidents.

## AER-0168 — descendant provenance assertion drift

The first complete alias-lock deterministic packet failed three repository
tests before any runtime was eligible. Two retained pre-repair structural/body
digests. A third repeated the already registered AER-0165 pattern by comparing
immutable attempt-026 evidence to the valid mutable attempt-027 alias without
first matching attempt identity.

The descendants now bind the exact alias-lock structural and body contracts
and the current inert rebind ledger. Historical attempt 026 remains protected
by its immutable SHA-256; the optional mutable alias is compared byte-for-byte
only when both objects carry the same attempt identifier.

This correction changes tests and register evidence only. It grants no
PostgreSQL run, migration, operational database, source, watcher/listener/feed,
patient/product data, provider, command, application/API/Diary wiring,
deployment, release, Pages or protected-ref authority.
