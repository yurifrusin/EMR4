# Raisa Projection-Native North Star

Status: G0 constitutional direction, not product implementation
Prepared: 2026-08-25T16:21:42+10:00

## Decision

Raisa will converge on one tenant-safe clinical and scheduling truth expressed as
typed commands, committed events and versioned projections. Word, Diary, mobile,
accessible fallback and later multimodal surfaces are adapters over that truth;
none is an independent mutation authority.

```text
human intent / bounded AI candidate
                 |
                 v
       typed intent + context
                 |
                 v
 deterministic policy and admission
                 |
                 v
       canonical typed command
                 |
                 v
 database transaction + audit event
                 |
                 v
 versioned semantic projection
          /          |          \
       Word        Diary       fallback
```

## Constitutional boundaries

### Identity and tenancy

Every intent, command, event and projection binds practice, actor, role, purpose
and resource. Patient identity is explicit. Application checks do not substitute
for database tenant enforcement. A projection cannot broaden the authority of
the context from which it was built.

### Command truth

Each mutation family has one canonical command path. Compatibility routes may
adapt into it but may not preserve a second mutation kernel. Commands carry an
idempotency identity, expected aggregate/version information and auditable human
authority. Concurrency-sensitive invariants are committed in the database.

### Event truth

Committed events describe accepted state change; they are not model prose. They
carry schema version, aggregate identity/version, tenant, actor, command and
causation/correlation provenance. Audit history is append-only.

### Projection contract

A projection is a typed, versioned, purpose-specific semantic view. It records:

- source event/version or read-model version;
- practice, actor, role, purpose and resource scope;
- generated-at, freshness horizon and invalidation token;
- permitted interactions and confirmation requirements;
- accessible labels and deterministic fallback semantics; and
- provenance sufficient to rebuild and compare it.

A stale, invalid, unknown-version or over-privileged projection is display-only
or rejected. It never authorises an action.

### AI boundary

AI may interpret intent, propose a typed plan or explain a projection. It may not
invent identity, elevate scope, commit state, attest a clinical conclusion,
finalise a prescription/claim, or convert an invalid projection into authority.
The deterministic admission layer validates every model-derived candidate.

### Surface parity

Word and Diary can optimise layout for their contexts while preserving the same
semantic fields, authority, confirmations, error states and committed outcome.
Visual convenience cannot hide a risk or create a command unavailable through
the stable accessible fallback.

## Version and evolution rule

Schemas evolve by explicit version. Readers reject unknown required semantics.
Projection rebuilds are deterministic from source truth. Compatibility is
time-bounded and measured; it cannot become a permanent parallel command path.

## G0 boundary

This north star freezes direction only. G0 does not redesign product routes,
schemas, database models, UI surfaces or clinical workflows. G3 owns the full
constitutional schema freeze; G4 and later gates own implementation.
