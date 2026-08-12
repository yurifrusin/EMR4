# Threat-model delta: source-owned truth and conditional commands

Date: 2026-08-12

Status: `architecture_only_unmounted`

## Assets and trust boundaries

Protected assets are current appointment truth, schedule exclusivity,
practice/actor authority, confirmation evidence, idempotency identity, audit
attribution and the distinction between a cue and a committed command receipt.
The trust boundary is the authoritative command service and its transaction;
the client, Context Fabric, watcher, event and model output remain untrusted for
write authority.

## Threats and controls

| Threat | Required control |
|---|---|
| Stale frame overwrites newer truth | short-lived backend precondition plus in-transaction current-state recheck |
| Two creates both see a free slot | schedule-domain serialization plus final database conflict constraint |
| Token replay in another practice or operation | bind practice, actor/session, purpose, operation, command digest, nonce and expiry |
| Freshness mistaken for consent | independent confirmation evidence and `confirmation_required` failure |
| Retry creates a second effect | idempotency key bound to command digest and original receipt |
| Missed or duplicated event changes truth | event has cue-only authority; every consequential use performs a fresh authorised read |
| Revoked actor commits from cached context | current-authority check inside the command transaction |
| Compatibility route bypasses invariants | converge all routes on one backend conditional-command kernel before deprecation |
| Loser is reported as winner | typed fail-closed outcomes; success only after commit and deterministic readback |
| Later durable watcher becomes a command plane | durable receipts/checkpoints remain cue-delivery evidence with `command_authority: false` |

## Residual risks held for implementation descendants

- selection of the database-owned schedule fence and its contention behavior;
- canonical lock coverage across practitioner, location and duration changes;
- token key rotation, clock skew, expiry and compromise response;
- compatibility-client handling of typed stale/conflict outcomes;
- RLS and role enforcement on the eventual command kernel;
- operational event latency and eventual durable cue recovery; and
- privacy-safe production telemetry.

## Closed authority

This delta authorizes no patient/product data, live route, database, migration,
watcher, provider, credential, executable, command, deployment or protected-ref
movement.

