# Threat-model delta: direct anonymous-record `xmin` access

Date: 2026-08-09

Status: bounded typed-renderer recovery candidate

## New observed failure

An explicitly aliased system column can be present in a PL/pgSQL `record`, yet
`(record).xmin` can still fail because parenthesised SQL composite access asks
PostgreSQL to resolve a fixed composite descriptor before the anonymous
record's runtime shape is available.

## Security properties

- `SYSTEM_XMIN` is valid only for a `LOCAL` record definitely assigned by an
  exact read that explicitly projects `xmin`.
- Lowering must emit direct `record.xmin`, never `(record).xmin`, `OLD.xmin` or
  `NEW.xmin`.
- Every system-column projection must retain explicit `relation.xmin AS xmin`.
- The recognizer must reject residual parenthesised record access across the
  complete artifact, not only the first observed function.
- No typed body semantic, relation, predicate, privilege, trigger, scenario or
  expected outcome may change through this representational correction.
- Parse/catalogue proof and behavior execution remain distinct gates; neither
  substitutes for the other.

## Retained containment

The work remains local, provider-free, unmounted, authored-synthetic and
default-off. Patient/product/protected data, operational sources and
credentials, application or migration runtime, providers, live watchers,
deployment, release, Pages and protected refs remain outside authority.
