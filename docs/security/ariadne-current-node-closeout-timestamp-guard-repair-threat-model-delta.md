# Threat-model delta — Ariadne current-node closeout timestamp guard repair

Date: 2026-08-23

Timestamp: 2026-08-23T00:23:23.4768539+10:00 (Australia/Brisbane)

Status: `frozen_for_execution`

Operation: `ariadne-current-node-closeout-timestamp-guard-repair`

## Security boundary

This tranche changes repository documentation metadata and one deterministic
test only. It adds no runtime component, service, route, provider, database,
credential, data read, exporter, command or deployment surface.

## Protected assets

- honest chronology for accepted current-node evidence;
- exact separation between a metadata repair and semantic history rewriting;
- graph-derived coverage that advances without a hand-authored operation list;
- repository containment of every evidence path; and
- all existing product, data, provider, production and protected-ref closures.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| An orchestrator remembers the date but omits the timestamp | The current-node consistency test requires both fields in the first twelve lines. |
| Date and timestamp disagree | Parsed calendar dates must be equal. |
| A non-Brisbane or offset-free time is accepted | Literal zone label, explicit ISO offset and exact `+10:00` are mandatory. |
| The guard becomes stale after graph advancement | Paths are derived from the latest Continuity node's `plans`, `closeouts` and `acceptances` categories. |
| Yuri summary escapes the rule | It is already a current-node `closeouts` artifact and therefore uses the same guard. |
| The three repaired documents regress after the graph moves | Their exact paths remain an explicit fixed repair set passed through the same validator. |
| A graph path escapes the repository | Every resolved path must remain relative to the repository root and exist as a file. |
| Repair rewrites accepted history | The candidate diff permits only one timestamp line after each existing date; semantic text and Git bindings stay unchanged. |
| Another bureaucratic surface is created | The guard lives in the existing Baton consistency suite; no new form, ledger, updater or manual receipt field exists. |

## API and data posture

No REST/OpenAPI, GraphQL, async, audit, idempotency, command or response
contract changes. No product, patient, appointment, practitioner, practice,
clinical, historical or protected evidence is accessed.

## Residual risk

The guard intentionally checks the current node plus the three repaired paths,
not all historical Markdown. It validates declared local time metadata, not the
independent truth of wall-clock capture. The transactional clockwork and Git
object bindings remain the authoritative source/result controls.

No provider, database, Docker, application runtime, deployment, release, Pages
or protected ref is accessed or changed.
