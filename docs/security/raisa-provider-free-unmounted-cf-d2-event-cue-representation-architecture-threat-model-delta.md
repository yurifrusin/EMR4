# Threat-model delta — CF-D2 event and cue representation architecture

Date: 2026-08-13

Timestamp: 2026-08-13T17:19:52+10:00 (Australia/Brisbane)

Status: `provider_free_unmounted_inert_representation_only`

## Assets protected

- source-owned Diary truth and command-time authority;
- exact partition, epoch, position and fencing-generation identity;
- immutable terminal receipt and obligation identity;
- contiguous checkpoint meaning;
- payload-free dispatch and reconciliation evidence; and
- the distinction between representability, transactional enforcement and
  external source truth.

## New boundary

The tranche introduces an abstract relational contract and pure row fixtures.
The checker reads repository JSON and constructs authored-synthetic Python
objects only. It opens no SQL parser, driver, database, migration, listener,
clock, process, network or application route.

## Threats and controls

| Threat | Control |
|---|---|
| Appointment or person truth is smuggled into a generic payload column | Exact seven-relation field sets; no JSON/blob/free-text field; explicit prohibited-column census |
| Position identity becomes ambiguous | Unique partition/epoch/positive-position tuple plus immutable receipt identity |
| Cue-required receipt becomes orphaned | Exact obligation reference plus future same-transaction admission protocol |
| Schema is mistaken for atomicity proof | Every invariant has one enforcement class; transaction protocols are explicitly unproved by row constraints |
| Checkpoint crosses a gap | Explicit-none checkpoint state plus future next-position-only advancement protocol and hostile gap fixtures |
| Coalescing erases or broadens coverage | Pending-only, adjacent, same-partition/epoch/consumer/reason protocol; exact range endpoints |
| Stale owner mutates shared state | Positive generation on every mutating protocol and exact current-generation fence |
| Failed dispatch rewrites cue content | Immutable attempt row and stable allowlisted failure class; obligation remains pending |
| Reconciliation fabricates freshness | Delivered-attempt prerequisite, closed truth table and literal one-attempt acknowledgement |
| Source-head observation is mistaken for truth | Coordinate row is labelled non-authoritative; current source truth remains external |
| Unknown coordinate appears as zero | Explicit state plus nullable position; no numeric zero source coordinate |
| Architecture checker is mistaken for database evidence | No SQL text, database library, connection, migration or persistence; explicit evidence label |

## Residual risk

An abstract representation cannot prove PostgreSQL types, constraint syntax,
deferrable references, transaction boundaries, isolation, locking, crash
behavior, restart, unknown commit, delivery, retention or operational safety.
Those claims remain closed for separately frozen descendants.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient client, real identity, database/source access, SQL or migration
execution, persistence, operational retention, watcher/listener/worker runtime,
provider/ADC, credential/IAM/network, executable tool, command/write, route,
deployment, production, release, Pages or protected-ref authority is opened.
